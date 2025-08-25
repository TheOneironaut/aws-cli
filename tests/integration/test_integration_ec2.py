import os
import time
import boto3
import botocore
import pytest

if os.getenv("RUN_AWS_INTEGRATION") != "1":
    pytest.skip("Set RUN_AWS_INTEGRATION=1 to run real AWS integration tests", allow_module_level=True)

from aws_object import AwsObject, Ec2


@pytest.fixture(scope="session")
def region():
    return os.getenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture(scope="session")
def aws_object(region):
    return AwsObject(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", ""),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
        owner=os.getenv("TEST_OWNER", "integration-test-owner"),
        region_name=region,
    )


def test_ec2_create_tag_list_stop_start_terminate(aws_object):
    ec2_wrap = Ec2(aws_object)
    ec2_client = boto3.client("ec2", region_name=aws_object.region_name)

    instance_id = None
    try:
        # Create instance with default valid type/image
        assert ec2_wrap.create_ec2() is True

        # Find the instance by our tags
        ids = ec2_wrap.get_id()
        assert len(ids) >= 1
        instance_id = ids[0]

        # Try to stop without waiting (ignore IncorrectInstanceState)
        try:
            ec2_wrap.stop(instance_id)
        except botocore.exceptions.ClientError as e:
            if e.response.get('Error', {}).get('Code') != 'IncorrectInstanceState':
                raise

        # Try to start without waiting (ignore IncorrectInstanceState)
        try:
            ec2_wrap.start(instance_id)
        except botocore.exceptions.ClientError as e:
            if e.response.get('Error', {}).get('Code') != 'IncorrectInstanceState':
                raise
    finally:
        if instance_id:
            try:
                ec2_client.terminate_instances(InstanceIds=[instance_id])
                waiter = ec2_client.get_waiter('instance_terminated')
                waiter.wait(InstanceIds=[instance_id], WaiterConfig={"Delay": 5, "MaxAttempts": 24})
            except Exception:
                pass
