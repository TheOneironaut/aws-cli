import pytest
from moto import mock_aws
import boto3
import os
from aws_object import AwsObject

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture
def aws_object_instance(aws_credentials):
    """Yields an AwsObject instance configured for testing."""
    return AwsObject(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        owner="test-owner"
    )

def test_save_creadencial(aws_object_instance, monkeypatch, tmp_path):
    # Override the home directory to use a temporary directory
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    aws_dir = home_dir / ".aws"
    
    # Monkeypatch os.path.expanduser to return our temporary home directory
    monkeypatch.setattr(os.path, 'expanduser', lambda path: str(home_dir) if path == '~' else path)
    
    aws_object_instance.save_creadencial()
    
    credentials_file = aws_dir / "credentials"
    assert credentials_file.exists()
    content = credentials_file.read_text()
    assert "[default]" in content
    assert "aws_access_key_id = testing" in content
    assert "aws_secret_access_key = testing" in content
    

@mock_aws
def test_valid_user_true(aws_object_instance):
    boto3.client("iam", region_name="us-east-1")
    # Moto's mock IAM GetUser doesn't require a user to exist for the call to succeed,
    # it just needs valid (mocked) credentials.
    assert aws_object_instance.valid_user() is True

@mock_aws
def test_valid_user_false(aws_object_instance, mocker):
    # We can simulate an exception by mocking the get_user call
    mocker.patch('boto3.client', side_effect=Exception("Invalid credentials"))
    assert aws_object_instance.valid_user() is False

@mock_aws
def test_add_user(aws_object_instance, mocker):
    # Mock save_creadencial to avoid filesystem interaction
    mocker.patch.object(aws_object_instance, 'save_creadencial')
    
    # Mock valid_user to return True
    mocker.patch.object(aws_object_instance, 'valid_user', return_value=True)
    
    result = aws_object_instance.add_user()
    
    aws_object_instance.save_creadencial.assert_called_once()
    aws_object_instance.valid_user.assert_called_once()
    assert result is True
