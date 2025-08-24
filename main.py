from aws_object import AwsObject, Ec2
import os


def main():
    # Get AWS credentials from environment variables
    key = os.getenv('AWS_ACCESS_KEY_ID')
    secret = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if not key or not secret:
        print("Error: AWS credentials not found!")
        print("Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
        print("Or use the AWS credentials file by running the setup first")
        return
    
    aws_obj = AwsObject(key, secret, owner="amitay")
    print("Adding user and validating credentials...")
    result = aws_obj.add_user()
    print(f"User validation result: {result}")
    
    if result:
        ec2 = Ec2(aws_obj)
        print("Creating EC2 instance...")
        ec2_result = ec2.create_ec2()
        print(f"EC2 creation result: {ec2_result}")


if __name__ == "__main__":
    main()


