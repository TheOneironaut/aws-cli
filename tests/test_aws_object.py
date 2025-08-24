import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys

# Add the parent directory to the sys.path to allow imports from the main folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aws_object import AwsObject, Ec2

class TestAwsObject(unittest.TestCase):

    def setUp(self):
        """Set up a new AwsObject instance before each test."""
        self.aws_object = AwsObject(
            aws_access_key_id="test_access_key",
            aws_secret_access_key="test_secret_key",
            owner="test_owner"
        )

    def test_init(self):
        """Test the __init__ method of AwsObject."""
        self.assertEqual(self.aws_object.aws_access_key_id, "test_access_key")
        self.assertEqual(self.aws_object.aws_secret_access_key, "test_secret_key")
        self.assertEqual(self.aws_object.owner, "test_owner")
        self.assertEqual(self.aws_object.created_by, "platform-cli")
        self.assertEqual(self.aws_object.region_name, "us-east-1")

    @patch("os.path.expanduser")
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_creadencial(self, mock_file, mock_makedirs, mock_expanduser):
        """Test the save_creadencial method."""
        mock_expanduser.return_value = "C:\\Users\\fakeuser"
        
        self.aws_object.save_creadencial()

        mock_expanduser.assert_called_once_with('~')
        # On Windows, the path should use backslashes
        expected_aws_path = "C:\\Users\\fakeuser\\.aws"
        mock_makedirs.assert_called_once_with(expected_aws_path)
        
        expected_creds_path = "C:\\Users\\fakeuser\\.aws\\credentials"
        mock_file.assert_called_once_with(expected_creds_path, "w")
        handle = mock_file()
        
        # The function writes everything in one call as an f-string
        expected_content = (f"[default]\n"
                           f"aws_access_key_id = {self.aws_object.aws_access_key_id}\n"
                           f"aws_secret_access_key = {self.aws_object.aws_secret_access_key}\n")
        handle.write.assert_called_once_with(expected_content)

    @patch("aws_object.AwsObject.valid_user")
    @patch("aws_object.AwsObject.save_creadencial")
    def test_add_user(self, mock_save_creadencial, mock_valid_user):
        """Test the add_user method."""
        mock_valid_user.return_value = True
        
        result = self.aws_object.add_user()
        
        mock_save_creadencial.assert_called_once()
        mock_valid_user.assert_called_once()
        self.assertTrue(result)

    @patch("boto3.client")
    def test_valid_user_success(self, mock_boto3_client):
        """Test the valid_user method for a successful validation."""
        mock_iam_client = MagicMock()
        mock_iam_client.get_user.return_value = {"User": {"UserName": "test_user"}}
        mock_boto3_client.return_value = mock_iam_client
        
        self.assertTrue(self.aws_object.valid_user())
        mock_boto3_client.assert_called_once_with('iam')

    @patch("boto3.client")
    def test_valid_user_failure(self, mock_boto3_client):
        """Test the valid_user method for a failed validation."""
        mock_iam_client = MagicMock()
        mock_iam_client.get_user.side_effect = Exception("Invalid credentials")
        mock_boto3_client.return_value = mock_iam_client
        
        self.assertFalse(self.aws_object.valid_user())
        mock_boto3_client.assert_called_once_with('iam')


class TestEc2(unittest.TestCase):

    def setUp(self):
        """Set up a new Ec2 instance before each test."""
        self.mock_aws_object = AwsObject(
            aws_access_key_id="test_access_key",
            aws_secret_access_key="test_secret_key",
            owner="test_owner",
            region_name="us-west-2"
        )
        self.ec2_instance = Ec2(aws_object=self.mock_aws_object)

    def test_init(self):
        """Test the __init__ method of Ec2."""
        self.assertEqual(self.ec2_instance.aws_object, self.mock_aws_object)
        self.assertEqual(self.ec2_instance.region_name, "us-west-2")
        # Test with region_name override
        ec2_instance_override = Ec2(aws_object=self.mock_aws_object, region_name="eu-central-1")
        self.assertEqual(ec2_instance_override.region_name, "eu-central-1")

    @patch("boto3.resource")
    def test_create_ec2_success(self, mock_boto3_resource):
        """Test successful EC2 instance creation."""
        mock_ec2_resource = MagicMock()
        mock_boto3_resource.return_value = mock_ec2_resource
        
        result = self.ec2_instance.create_ec2()
        
        self.assertTrue(result)
        mock_boto3_resource.assert_called_once_with('ec2', region_name="us-west-2")
        mock_ec2_resource.create_instances.assert_called_once_with(
            ImageId="ami-020cba7c55df1f615",
            InstanceType="t3.micro",
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[{"ResourceType": "instance", "Tags": [{"Key": "CreatedBy", "Value": "platform-cli"}, {"Key": "Owner", "Value": "test_owner"}]}]
        )

    @patch("boto3.resource")
    def test_create_ec2_success_by_name(self, mock_boto3_resource):
        """Test successful EC2 instance creation using image name."""
        mock_ec2_resource = MagicMock()
        mock_boto3_resource.return_value = mock_ec2_resource
        
        result = self.ec2_instance.create_ec2(image_id_or_name="ubuntu")
        
        self.assertTrue(result)
        mock_boto3_resource.assert_called_once_with('ec2', region_name="us-west-2")
        mock_ec2_resource.create_instances.assert_called_once_with(
            ImageId="ami-020cba7c55df1f615",
            InstanceType="t3.micro",
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[{"ResourceType": "instance", "Tags": [{"Key": "CreatedBy", "Value": "platform-cli"}, {"Key": "Owner", "Value": "test_owner"}]}]
        )

    def test_create_ec2_invalid_type(self):
        """Test EC2 creation with an invalid instance type."""
        result = self.ec2_instance.create_ec2(type="t2.nano")
        self.assertIn("instance type must one of", result)

    def test_create_ec2_invalid_image(self):
        """Test EC2 creation with an invalid image ID or name."""
        result = self.ec2_instance.create_ec2(image_id_or_name="invalid-image")
        self.assertIn("instance type must one of", result)

    @patch("boto3.client")
    def test_get_id(self, mock_boto3_client):
        """Test the get_id method."""
        mock_ec2_client = MagicMock()
        mock_ec2_client.describe_instances.return_value = {
            "Reservations": [
                {"Instances": [{"InstanceId": "i-12345"}, {"InstanceId": "i-67890"}]}
            ]
        }
        mock_boto3_client.return_value = mock_ec2_client
        
        instance_ids = self.ec2_instance.get_id()
        
        self.assertEqual(instance_ids, ["i-12345", "i-67890"])
        mock_boto3_client.assert_called_once_with('ec2', region_name="us-west-2")
        custom_filter = [{
            'Name':'tag:Owner', 
            'Values': ['amitay']},{
            'Name':'tag:CreatedBy', 
            'Values': ['platform-cli']}]
        mock_ec2_client.describe_instances.assert_called_once_with(Filters=custom_filter)

    @patch("boto3.resource")
    def test_stop(self, mock_boto3_resource):
        """Test the stop method."""
        mock_instance = MagicMock()
        mock_ec2_resource = MagicMock()
        mock_ec2_resource.Instance.return_value = mock_instance
        mock_boto3_resource.return_value = mock_ec2_resource

        self.ec2_instance.stop("i-12345")

        mock_boto3_resource.assert_called_once_with('ec2', region_name="us-west-2")
        mock_ec2_resource.Instance.assert_called_once_with(id="i-12345")
        mock_instance.stop.assert_called_once()

    @patch("aws_object.Ec2.get_id")
    @patch("aws_object.Ec2.stop")
    def test_stop_all(self, mock_stop, mock_get_id):
        """Test the stop_all method."""
        mock_get_id.return_value = ["i-12345", "i-67890"]
        
        result = self.ec2_instance.stop_all()
        
        self.assertTrue(result)
        mock_get_id.assert_called_once()
        self.assertEqual(mock_stop.call_count, 2)
        mock_stop.assert_any_call("i-12345")
        mock_stop.assert_any_call("i-67890")

    @patch("aws_object.Ec2.get_id")
    def test_stop_all_no_instances(self, mock_get_id):
        """Test stop_all with no instances to stop."""
        mock_get_id.return_value = None
        result = self.ec2_instance.stop_all()
        self.assertEqual(result, "There is no instances")

    @patch("boto3.resource")
    def test_start(self, mock_boto3_resource):
        """Test the start method."""
        mock_ec2 = MagicMock()
        mock_boto3_resource.return_value = mock_ec2
        
        self.ec2_instance.start("i-12345")
        
        mock_boto3_resource.assert_called_once_with('ec2', region_name="us-west-2")
        mock_ec2.start_instances.assert_called_once_with(InstanceIds=["i-12345"])

    @patch("aws_object.Ec2.get_id")
    @patch("aws_object.Ec2.start")
    def test_start_all(self, mock_start, mock_get_id):
        """Test the start_all method."""
        mock_get_id.return_value = ["i-12345", "i-67890"]
        
        result = self.ec2_instance.start_all()
        
        self.assertTrue(result)
        mock_get_id.assert_called_once()
        self.assertEqual(mock_start.call_count, 2)
        mock_start.assert_any_call("i-12345")
        mock_start.assert_any_call("i-67890")

    @patch("aws_object.Ec2.get_id")
    def test_start_all_no_instances(self, mock_get_id):
        """Test start_all with no instances to start."""
        mock_get_id.return_value = None
        result = self.ec2_instance.start_all()
        self.assertEqual(result, "There is no instances")

if __name__ == "__main__":
    unittest.main()
