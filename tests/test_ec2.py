import pytest
try:
    from moto import mock_aws
except ImportError:  # pragma: no cover - environment without dev deps
    import pytest as _pytest
    _pytest.skip("moto is not installed; run `uv sync --dev` to enable these tests.", allow_module_level=True)
import boto3
from aws_object import AwsObject, Ec2

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
def ec2_instance(aws_object):
    return Ec2(aws_object)

@mock_aws
def test_create_ec2_success(ec2_instance):
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    result = ec2_instance.create_ec2()
    assert result is True
    
    instances = ec2_client.describe_instances()
    assert len(instances['Reservations'][0]['Instances']) == 1
    tags = instances['Reservations'][0]['Instances'][0]['Tags']
    assert {'Key': 'CreatedBy', 'Value': 'platform-cli'} in tags
    assert {'Key': 'Owner', 'Value': 'test-owner'} in tags


@mock_aws
def test_create_ec2_invalid_type(ec2_instance):
    result = ec2_instance.create_ec2(type="invalid-type")
    assert "instance type must one of" in result

@mock_aws
def test_get_id(ec2_instance):
    ec2 = boto3.resource('ec2', region_name='us-east-1')
    instance = ec2.create_instances(
        ImageId='ami-020cba7c55df1f615',
        InstanceType='t3.micro',
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[{'ResourceType': 'instance', 'Tags': [{'Key': 'Owner', 'Value': 'amitay'}, {'Key': 'CreatedBy', 'Value': 'platform-cli'}]}]
    )
    instance_id = instance[0].id
    
    ids = ec2_instance.get_id()
    assert ids == [instance_id]

@mock_aws
def test_stop_and_start(ec2_instance):
    ec2 = boto3.resource('ec2', region_name='us-east-1')
    instance = ec2.create_instances(
        ImageId='ami-020cba7c55df1f615',
        InstanceType='t3.micro',
        MinCount=1,
        MaxCount=1
    )[0]
    
    instance.wait_until_running()
    
    ec2_instance.stop(instance.id)
    instance.reload()
    assert instance.state['Name'] == 'stopping' or instance.state['Name'] == 'stopped'

    # Note: moto might not fully simulate the start/stop state changes perfectly,
    # so we check for 'pending' as well.
    ec2_instance.start(instance.id)
    instance.reload()
    assert instance.state['Name'] in ['pending', 'running']

@mock_aws
def test_stop_all_and_start_all(ec2_instance, mocker):
    mock_ids = ["i-12345", "i-67890"]
    mocker.patch.object(ec2_instance, 'get_id', return_value=mock_ids)
    mock_stop = mocker.patch.object(ec2_instance, 'stop')
    mock_start = mocker.patch.object(ec2_instance, 'start')

    result_stop = ec2_instance.stop_all()
    assert result_stop is True
    assert mock_stop.call_count == len(mock_ids)
    mock_stop.assert_any_call("i-12345")
    mock_stop.assert_any_call("i-67890")

    result_start = ec2_instance.start_all()
    assert result_start is True
    assert mock_start.call_count == len(mock_ids)
    mock_start.assert_any_call("i-12345")
    mock_start.assert_any_call("i-67890")

@mock_aws
def test_list_ec2(ec2_instance, mocker):
    mocker.patch.object(ec2_instance, 'get_id', return_value=["i-12345", "i-67890"])
    # This test is a bit weak as listec2 doesn't return the list.
    # It just prints. We'd need to capture stdout to test it properly.
    # For now, just call it to ensure no errors.
    # A better implementation of listec2 would return the string.
    ec2_instance.listec2()
