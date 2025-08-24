import boto3
import os

class AwsObject():
    def __init__(self,aws_access_key_id,aws_secret_access_key,owner,region_name = "us-east-1"):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.created_by = "platform-cli"
        self.owner = owner
        self.region_name = region_name
    def save_creadencial(self):
        folder_pat = os.path.join(os.path.expanduser('~'),".aws")        
        try:
            os.makedirs(folder_pat)
        except FileExistsError:
            print("Creating a folder: Skips an existing file")

        a = os.path.join(folder_pat, f"credentials")
        with open(a, "w") as f:
            f.write(f"[default]\n"
                    f"aws_access_key_id = {self.aws_access_key_id}\n"
                    f"aws_secret_access_key = {self.aws_secret_access_key}\n")
            
    def add_user(self):
        self.save_creadencial()
        return self.valid_user()
    
    
    def valid_user(self):
        iam_client = boto3.client('iam')
        try:
            response = iam_client.get_user()
            return True
        except Exception as e:
            return False
        

class Ec2():
    def __init__(self,aws_object: AwsObject,region_name = None):
        self.valid_type = ["t3.micro","t2.small"]
        self.max_instnces = 2
        self.valid_images = [{"ubuntu":"ami-020cba7c55df1f615","amazon-linux":"ami-00ca32bbc84273381"}]
        self.aws_object = aws_object
        self.region_name = region_name or self.aws_object.region_name


    def create_ec2(self,type = "t3.micro",image_id_or_name = "ami-020cba7c55df1f615"):
        if type not in self.valid_type:
            return f"instance type must one of {self.valid_type}"
        for name, id in self.valid_images[0].items():
            if name == image_id_or_name or id == image_id_or_name:
                image_id_or_name = id
                ec2 = boto3.resource('ec2',region_name = self.region_name)
                try:
                    instances = ec2.create_instances(
                        
                        ImageId=image_id_or_name,
                        InstanceType=type,
                        MinCount = 1,
                        MaxCount = 1,
                        TagSpecifications = [{"ResourceType": "instance", "Tags": [{"Key": "CreatedBy", "Value": self.aws_object.created_by}, {"Key": "Owner", "Value": self.aws_object.owner}]}],

                    )
                except Exception as e:
                    print(f"Error creating EC2 instance: {e}")
                return True
            return f"instance type must one of {self.valid_images}"



    def get_id(self):
        ec2 = boto3.client('ec2',region_name = self.region_name)
        custom_filter = [{
            'Name':'tag:Owner', 
            'Values': ['amitay']},{
            'Name':'tag:CreatedBy', 
            'Values': ['platform-cli']}]
            
        response = ec2.describe_instances(Filters=custom_filter)
        instance_ids = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_ids.append(instance['InstanceId'])
        
        return instance_ids

    def stop(self,id):
        ec2 = boto3.resource('ec2', region_name=self.region_name)
        instance = ec2.Instance(id=id)
        instance.stop()
    
    def stop_all(self):
        ids = self.get_id()
        if ids == None:
            return "There is no instances"
        for id in ids:
            self.stop(id)
        return True

    def start(self,id):
        ec2 = boto3.resource('ec2', region_name=self.region_name)
        response = ec2.start_instances(
        InstanceIds=[f"{id}"])

        return response
   
        
    def start_all(self):
        ids = self.get_id()
        if ids == None:
            return "There is no instances"
        for id in ids:
            self.start(id)
        return True


    def listec2(self):
        ids = self.get_id()
        if ids == None:
            return "There is no instances"
        ls = ""
        for i in ids:
            ls += f"instance id: f{i}\n"


class S3():
    def __init__(self, aws_object: AwsObject):
        self.aws_object = aws_object

    def create_bucket(self, bucket_name: str, state = "private"):
        if state not in ["private", "public"]:
            return False
        s3_client = boto3.client('s3', region_name=self.aws_object.region_name)
        try:
            # For regions other than us-east-1, we need to specify the LocationConstraint
            if self.aws_object.region_name == 'us-east-1':
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': self.aws_object.region_name
                    }
                )
            
            # Add tags to the bucket
            s3_client.put_bucket_tagging(
                Bucket=bucket_name,
                Tagging={
                    'TagSet': [
                        {'Key': 'Owner', 'Value': self.aws_object.owner},
                        {'Key': 'CreatedBy', 'Value': self.aws_object.created_by}
                    ]
                }
            )
            
            if state == "public":
                try:
                    # Try to use simpler ACL method for public read access
                    s3_client.put_bucket_acl(Bucket=bucket_name, ACL='public-read')
                except Exception as acl_error:
                    # If ACL fails (due to Block Public Access), create bucket as private
                    # but still return True since bucket was created successfully
                    print(f"Warning: Could not set bucket to public due to Block Public Access settings: {acl_error}")
                    print(f"Bucket '{bucket_name}' was created as private instead.")
            return True
        except Exception as e:
            print(f"Error creating bucket: {e}")  # For debugging
            return False

    def is_bucket_public(self, bucket_name: str):
        """Check if a bucket has public read access."""
        s3_client = boto3.client('s3', region_name=self.aws_object.region_name)
        try:
            acl = s3_client.get_bucket_acl(Bucket=bucket_name)
            # Check if there's a public read grant
            for grant in acl.get('Grants', []):
                grantee = grant.get('Grantee', {})
                if (grantee.get('Type') == 'Group' and 
                    grantee.get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers' and
                    grant.get('Permission') in ['READ', 'FULL_CONTROL']):
                    return True
            return False
        except Exception as e:
            print(f"Error checking bucket ACL: {e}")
            return False

    def upload_file(self, bucket_name: str, file_path: str, aws_object: AwsObject, object_name: str = None):
        s3_client = boto3.client('s3', region_name=aws_object.region_name)
        try:
            s3_client.upload_file(file_path, bucket_name, object_name or file_path, ExtraArgs={"Tagging": f"Owner={aws_object.owner}&CreatedBy={aws_object.created_by}"})
            return True
        except Exception as e:
            return False

    def list_files(self, bucket_name: str, aws_object: AwsObject):
        s3_client = boto3.client('s3', region_name=aws_object.region_name)
        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Tagging=f"Owner={aws_object.owner}&CreatedBy={aws_object.created_by}")
            return response.get('Contents', [])
        except Exception as e:
            return []

    def is_bucket_public(self, bucket_name: str):
        """Check if a bucket is configured for public access."""
        s3_client = boto3.client('s3', region_name=self.aws_object.region_name)
        try:
            acl = s3_client.get_bucket_acl(Bucket=bucket_name)
            # Check if any grant gives public read access
            for grant in acl.get('Grants', []):
                grantee = grant.get('Grantee', {})
                if (grantee.get('Type') == 'Group' and 
                    grantee.get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers' and
                    grant.get('Permission') == 'READ'):
                    return True
            return False
        except Exception:
            return False
