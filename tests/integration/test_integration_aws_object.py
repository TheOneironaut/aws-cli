import os
import pytest

if os.getenv("RUN_AWS_INTEGRATION") != "1":
    pytest.skip("Set RUN_AWS_INTEGRATION=1 to run real AWS integration tests", allow_module_level=True)

from aws_object import AwsObject


def test_valid_user_real():
    # This calls IAM GetUser; it will succeed if credentials are valid and authorized
    obj = AwsObject(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", ""),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
        owner=os.getenv("TEST_OWNER", "integration-test-owner"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    )
    assert obj.valid_user() is True
