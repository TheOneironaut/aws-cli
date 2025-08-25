import boto3
import os
from botocore.exceptions import ClientError

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

    def create_bucket(self, bucket_name: str):
        s3_client = boto3.client('s3', region_name=self.aws_object.region_name)
        try:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': self.aws_object.region_name,
                    'Tags': [
                        {'Key': 'Owner', 'Value': self.aws_object.owner},
                        {'Key': 'CreatedBy', 'Value': self.aws_object.created_by}
                    ]
                }
            )
            return True
        except Exception as e:
            print(f"Error creating bucket: {e}")
            return False
        
    def upload_file(self, bucket_name: str, file_path: str):
        s3_client = boto3.client('s3', region_name=self.aws_object.region_name)
        object_name = os.path.basename(file_path)
        try:
            s3_client.upload_file(file_path, bucket_name, object_name, ExtraArgs={"Tagging": f"Owner={self.aws_object.owner}&CreatedBy={self.aws_object.created_by}"})
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False

    def list_buckets(self):
        s3_resource = boto3.resource('s3', region_name=self.aws_object.region_name)
        owned_buckets = []
        for bucket in s3_resource.buckets.all():
            bucket_tags = bucket.Tagging().tag_set
            bucket_owner = None
            bucket_creator = None
            for tag in bucket_tags:
                if tag['Key'] == 'Owner':
                    bucket_owner = tag['Value']
                if tag['Key'] == 'CreatedBy':
                    bucket_creator = tag['Value']
            if bucket_owner == self.aws_object.owner and bucket_creator == self.aws_object.created_by:
                owned_buckets.append(bucket.name)
        return owned_buckets



class Route53():
    def __init__(self,aws_object: AwsObject,domain_name):
        self.route53 = boto3.client('route53')
        self.aws_object = aws_object
        self.resourceId = self.create_zone(domain_name)
    
    def create_zone(self, domain_name):
        response = self.route53.create_hosted_zone(
        Name=domain_name,
    )
        resourceId=response['HostedZone']['Id']
        self.route53.change_tags_for_resource(
        ResourceType='healthcheck'|'hostedzone',
        ResourceId=resourceId,
        AddTags=[
            {
                'Key': 'Owner',
                'Value': self.aws_object.owner
            },
             {
                'Key': 'CreatedBy',
                'Value': self.aws_object.created_by
            },
        ]
    )
        return resourceId
    
    def create_record(self, name, ip, dns_type="A", ttl=300):
        response = self.route53.change_resource_record_sets(
            HostedZoneId=self.resourceId,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'CREATE',
                        'ResourceRecordSet': {
                            'Name': name,
                            'Type': dns_type,
                            'TTL': ttl,
                            'ResourceRecords': [{'Value': ip}],
                        },
                    },
                ]
            }
        )
        return response


    def delete_record(self,name):
        response = self.route53.change_resource_record_sets(
        HostedZoneId=self.resourceId,
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'DELETE',
                    'ResourceRecordSet': {
                        'Name': name,
                    },
                },
            ]
        }
    )
        return response

    def update_record(self, name, dns_type, ip=None, ttl=None):
        if ip is None and ttl is None:
            response = "you must update ip or ttl"
        elif ip is None:
            rsrecord = {
            'ResourceRecordSet': {
                'Name': name,
                'Type': dns_type,
                'TTL': ttl,
            },
        }
        elif ttl is None:
            rsrecord = {
            'ResourceRecordSet': {
                'Name': name,
                'Type': dns_type,
                'ResourceRecords': [{'Value': ip}],
            },
        }
        response = self.route53.change_resource_record_sets(
            HostedZoneId=self.resourceId,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': rsrecord
                    },
                ]
            }
        )
        return response
    
    

        

