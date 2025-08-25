import pytest
try:
    from moto import mock_aws
except ImportError:  # pragma: no cover - environment without dev deps
    import pytest as _pytest
    _pytest.skip("moto is not installed; run `uv sync --dev` to enable these tests.", allow_module_level=True)
import boto3
from aws_object import AwsObject, Route53

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    import os
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture
def aws_object(aws_credentials):
    return AwsObject("testing", "testing", "test-owner")

@pytest.fixture
def route53_instance(aws_object):
    # Keep the moto mock active for the entire test using a context-managed fixture
    with mock_aws():
        # The Route53 class creates a zone on init, so we need the mock active
        r53 = Route53(aws_object, "example.com")
        yield r53

@mock_aws
def test_create_zone(aws_object):
    route53_client = boto3.client("route53", region_name="us-east-1")
    
    # We are testing the __init__ method here as it calls create_zone
    r53 = Route53(aws_object, "newzone.com")
    
    zones = route53_client.list_hosted_zones()
    
    assert any(zone['Name'] == 'newzone.com.' for zone in zones['HostedZones'])
    
    # Note: moto doesn't fully support tagging on creation for Route53 zones in the same way.
    # A more complex test would be needed to verify tags, possibly by listing tags for the resource.

def test_create_record(route53_instance):
    response = route53_instance.create_record("test.example.com", "1.2.3.4")
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200
    
    route53_client = boto3.client("route53", region_name="us-east-1")
    record_sets = route53_client.list_resource_record_sets(HostedZoneId=route53_instance.resourceId)
    
    a_records = [r for r in record_sets['ResourceRecordSets'] if r['Type'] == 'A']
    assert any(r['Name'] == 'test.example.com.' and r['ResourceRecords'][0]['Value'] == '1.2.3.4' for r in a_records)

def test_delete_record(route53_instance):
    # First, create a record to delete
    route53_instance.create_record("delete-me.example.com", "5.5.5.5")
    
    response = route53_instance.delete_record("delete-me.example.com")
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200

def test_update_record(route53_instance):
    # First, create a record to update
    route53_instance.create_record("update-me.example.com", "8.8.8.8")
    
    # Update the IP
    response = route53_instance.update_record("update-me.example.com", "A", ip="9.9.9.9")
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200
    
    route53_client = boto3.client("route53", region_name="us-east-1")
    record_sets = route53_client.list_resource_record_sets(HostedZoneId=route53_instance.resourceId)
    
    a_records = [r for r in record_sets['ResourceRecordSets'] if r['Type'] == 'A' and r['Name'] == 'update-me.example.com.']
    assert a_records[0]['ResourceRecords'][0]['Value'] == '9.9.9.9'
