import pytest
from moto import mock_aws
import boto3
from aws_object import AwsObject, S3
import os

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture
def aws_object(aws_credentials):
    return AwsObject("testing", "testing", "test-owner")

@pytest.fixture
def s3_instance(aws_object):
    return S3(aws_object)

@mock_aws
def test_create_bucket(s3_instance):
    result = s3_instance.create_bucket("test-bucket")
    assert result is True
    s3_client = boto3.client("s3", region_name="us-east-1")
    response = s3_client.list_buckets()
    assert "test-bucket" in [bucket['Name'] for bucket in response['Buckets']]

@mock_aws
def test_upload_file(s3_instance, tmp_path):
    s3_client = boto3.client("s3", region_name="us-east-1")
    # For us-east-1, no LocationConstraint should be specified.
    s3_client.create_bucket(Bucket="test-bucket")
    
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")
    
    result = s3_instance.upload_file("test-bucket", str(test_file))
    assert result is True
    
    response = s3_client.get_object(Bucket="test-bucket", Key="test.txt")
    assert response['Body'].read().decode('utf-8') == "hello world"

@mock_aws
def test_list_buckets(s3_instance):
    s3_resource = boto3.resource('s3', region_name='us-east-1')
    
    # Create a bucket that should be listed
    bucket1 = s3_resource.create_bucket(Bucket='owned-bucket')
    bucket1.Tagging().put(Tagging={'TagSet': [{'Key': 'Owner', 'Value': 'test-owner'}, {'Key': 'CreatedBy', 'Value': 'platform-cli'}]})

    # Create a bucket that should NOT be listed (different owner)
    bucket2 = s3_resource.create_bucket(Bucket='other-owner-bucket')
    bucket2.Tagging().put(Tagging={'TagSet': [{'Key': 'Owner', 'Value': 'other-owner'}, {'Key': 'CreatedBy', 'Value': 'platform-cli'}]})

    # Create a bucket with no tags
    s3_resource.create_bucket(Bucket='no-tags-bucket')

    buckets = s3_instance.list_buckets()
    assert 'owned-bucket' in buckets
    assert 'other-owner-bucket' not in buckets
    assert 'no-tags-bucket' not in buckets
