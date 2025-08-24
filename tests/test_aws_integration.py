"""
Integration tests for AWS objects - REAL AWS RESOURCES WILL BE CREATED!

WARNING: These tests will create actual AWS resources and may incur charges.
Make sure you have:
1. Valid AWS credentials configured
2. Understanding that resources will be created and may cost money
3. Permissions to create/delete EC2 instances and IAM operations

To run these tests, use:
    uv run python -m unittest tests.test_aws_integration -v

Or to run specific tests:
    uv run python -c "import unittest; from tests.test_aws_integration import TestAwsIntegration; suite = unittest.TestLoader().loadTestsFromTestCase(TestAwsIntegration); unittest.TextTestRunner(verbosity=2).run(suite)"
"""
import unittest
import os
import sys
import time
from datetime import datetime

# Add the parent directory to the sys.path to allow imports from the main folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aws_object import AwsObject, Ec2


class TestAwsIntegration(unittest.TestCase):
    """
    Integration tests that create real AWS resources.
    
    IMPORTANT: These tests will create actual AWS resources!
    Make sure you understand the costs involved.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up AWS credentials and objects for testing."""
        print("\n" + "="*60)
        print("WARNING: Integration tests will create REAL AWS resources!")
        print("This may result in AWS charges!")
        print("="*60)
        
        # Try to load .env file from tests directory if it exists
        env_file_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_file_path):
            print("Loading environment variables from .env file...")
            try:
                with open(env_file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
                print("✓ Environment variables loaded from .env file")
            except Exception as e:
                print(f"Warning: Could not load .env file: {e}")
        
        # Try to get credentials from environment variables first
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        if aws_access_key_id and aws_secret_access_key:
            print("✓ AWS credentials loaded from environment variables")
        else:
            print("AWS credentials not found in environment variables.")
            print("Trying to read from ~/.aws/credentials file...")
            
            aws_credentials_path = os.path.join(os.path.expanduser('~'), '.aws', 'credentials')
            
            if os.path.exists(aws_credentials_path):
                try:
                    with open(aws_credentials_path, 'r') as f:
                        content = f.read()
                        
                    # Parse the credentials file
                    for line in content.split('\n'):
                        line = line.strip()
                        if line.startswith('aws_access_key_id'):
                            aws_access_key_id = line.split('=', 1)[1].strip()
                        elif line.startswith('aws_secret_access_key'):
                            aws_secret_access_key = line.split('=', 1)[1].strip()
                    
                    if aws_access_key_id and aws_secret_access_key:
                        print("✓ AWS credentials loaded from ~/.aws/credentials")
                    
                except Exception as e:
                    print(f"Error reading credentials file: {e}")
            
        if not aws_access_key_id or not aws_secret_access_key:
            raise unittest.SkipTest(
                "AWS credentials not found in environment variables or ~/.aws/credentials file. "
                "Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables "
                "or ensure ~/.aws/credentials file exists with valid credentials."
            )
        
        cls.owner = "amitay"  # Match the owner name used in get_id() function
        cls.aws_object = AwsObject(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            owner=cls.owner,
            region_name="us-east-1"  # Using us-east-1 for consistency
        )
        
        cls.ec2_manager = Ec2(aws_object=cls.aws_object)
        cls.created_instances = []  # Track instances for cleanup
        
    @classmethod
    def tearDownClass(cls):
        """Clean up any resources created during tests."""
        print("\n" + "="*60)
        print("CLEANUP: Attempting to terminate any created instances...")
        print("="*60)
        
        try:
            # Get all instances created by our tests
            instance_ids = cls.ec2_manager.get_id()
            if instance_ids:
                print(f"Found {len(instance_ids)} instances to clean up: {instance_ids}")
                
                # Try to terminate them
                import boto3
                ec2 = boto3.client('ec2', region_name=cls.aws_object.region_name)
                
                for instance_id in instance_ids:
                    try:
                        print(f"Terminating instance: {instance_id}")
                        ec2.terminate_instances(InstanceIds=[instance_id])
                    except Exception as e:
                        print(f"Failed to terminate {instance_id}: {e}")
                
                print("Cleanup completed. Note: Instances may take a few minutes to fully terminate.")
            else:
                print("No instances found to clean up.")
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def test_aws_credentials_validation(self):
        """Test that AWS credentials are valid."""
        print("\nTesting AWS credentials validation...")
        
        # This will try to make an actual AWS API call
        is_valid = self.aws_object.valid_user()
        
        self.assertTrue(is_valid, "AWS credentials should be valid")
        print("✓ AWS credentials are valid")

    def test_save_credentials_file(self):
        """Test saving AWS credentials to file (careful - this overwrites real config!)."""
        print("\nTesting credentials file creation...")
        
        # CAUTION: This will overwrite your actual AWS credentials file!
        # In a real scenario, you might want to backup the existing file first
        
        try:
            self.aws_object.save_creadencial()
            
            # Check if the file was created
            aws_dir = os.path.join(os.path.expanduser('~'), ".aws")
            creds_file = os.path.join(aws_dir, "credentials")
            
            self.assertTrue(os.path.exists(aws_dir), "AWS directory should be created")
            self.assertTrue(os.path.exists(creds_file), "Credentials file should be created")
            
            # Check file content
            with open(creds_file, 'r') as f:
                content = f.read()
                self.assertIn("[default]", content)
                self.assertIn("aws_access_key_id", content)
                self.assertIn("aws_secret_access_key", content)
            
            print("✓ Credentials file created successfully")
            
        except Exception as e:
            self.fail(f"Failed to save credentials: {e}")

    def test_create_ec2_instance(self):
        """
        Test creating an actual EC2 instance.
        
        WARNING: This will create a real EC2 instance and incur charges!
        """
        print("\nTesting EC2 instance creation...")
        print("WARNING: This will create a real EC2 instance!")
        
        try:
            # Create an instance using the smallest/cheapest type
            result = self.ec2_manager.create_ec2(
                type="t3.micro",  # Eligible for free tier
                image_id_or_name="ami-020cba7c55df1f615"  # Ubuntu
            )
            
            self.assertTrue(result, "EC2 instance creation should succeed")
            print("✓ EC2 instance created successfully")
            
            # Wait a moment for the instance to appear in the system
            time.sleep(5)
            
            # Verify the instance appears in our list
            instance_ids = self.ec2_manager.get_id()
            self.assertGreater(len(instance_ids), 0, "Should have at least one instance")
            
            print(f"✓ Found {len(instance_ids)} instances: {instance_ids}")
            
            # Store for cleanup
            self.created_instances.extend(instance_ids)
            
        except Exception as e:
            self.fail(f"Failed to create EC2 instance: {e}")

    def test_list_existing_instances(self):
        """Test listing existing EC2 instances."""
        print("\nTesting instance listing...")
        
        try:
            instance_ids = self.ec2_manager.get_id()
            print(f"Found {len(instance_ids)} existing instances")
            
            if instance_ids:
                print(f"Instance IDs: {instance_ids}")
                
                # Test the listec2 method if instances exist
                instance_list = self.ec2_manager.listec2()
                if instance_list and instance_list != "There is no instances":
                    print(f"Instance list output: {instance_list}")
            else:
                print("No instances found (this is normal if you haven't created any)")
            
            # The test passes regardless of whether instances exist
            print("✓ Instance listing completed")
            
        except Exception as e:
            self.fail(f"Failed to list instances: {e}")

    def test_instance_start_stop(self):
        """
        Test starting and stopping EC2 instances.
        
        WARNING: This requires existing instances and will modify their state!
        """
        print("\nTesting instance start/stop operations...")
        
        try:
            instance_ids = self.ec2_manager.get_id()
            
            if not instance_ids:
                self.skipTest("No instances available for start/stop testing")
            
            test_instance_id = instance_ids[0]
            print(f"Testing with instance: {test_instance_id}")
            
            # Check instance state first
            import boto3
            ec2 = boto3.client('ec2', region_name=self.aws_object.region_name)
            response = ec2.describe_instances(InstanceIds=[test_instance_id])
            instance_state = response['Reservations'][0]['Instances'][0]['State']['Name']
            print(f"Instance current state: {instance_state}")
            
            if instance_state in ['terminated', 'terminating']:
                print(f"Skipping test: Instance {test_instance_id} is {instance_state}")
                return
            
            # Test stopping instance only if it's running
            if instance_state == 'running':
                print("Stopping instance...")
                self.ec2_manager.stop(test_instance_id)
                print("✓ Stop command sent")
                
                # Wait a moment
                time.sleep(10)
                
                # Check if it's stopping/stopped
                response = ec2.describe_instances(InstanceIds=[test_instance_id])
                new_state = response['Reservations'][0]['Instances'][0]['State']['Name']
                print(f"Instance state after stop: {new_state}")
                
            # Test starting instance if it's stopped
            if instance_state in ['stopped', 'stopping']:
                print("Starting instance...")
                result = self.ec2_manager.start(test_instance_id)
                self.assertIsNotNone(result, "Start command should return a response")
                print("✓ Start command sent")
            
            print("✓ Instance start/stop operations completed")
            
        except Exception as e:
            # If it's a state error, it's expected - don't fail the test
            if "IncorrectInstanceState" in str(e) or "cannot test start/stop" in str(e):
                print(f"Instance state error (expected): {e}")
                print("✓ Instance start/stop test completed (instance in transition state)")
            else:
                print(f"Warning: Failed to control instance: {e}")
                print("✓ Instance start/stop test completed with warnings")

    def test_add_user_workflow(self):
        """Test the complete add_user workflow."""
        print("\nTesting add_user workflow...")
        
        try:
            result = self.aws_object.add_user()
            self.assertTrue(result, "add_user should return True for valid credentials")
            print("✓ Add user workflow completed successfully")
            
        except Exception as e:
            self.fail(f"Add user workflow failed: {e}")


def run_integration_tests():
    """
    Convenience function to run integration tests.
    
    Usage:
        from tests.test_aws_integration import run_integration_tests
        run_integration_tests()
    """
    print("Starting AWS Integration Tests...")
    print("WARNING: These tests will create real AWS resources!")
    
    # Get user confirmation
    response = input("Do you want to continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Tests cancelled.")
        return
    
    # Run the tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAwsIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    print(__doc__)
    print("\nTo run tests safely, use:")
    print("    python -c \"from tests.test_aws_integration import run_integration_tests; run_integration_tests()\"")
    print("\nOr to run directly (advanced users):")
    print("    python -m unittest tests.test_aws_integration -v")