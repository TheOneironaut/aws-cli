import os
import boto3
import pytest

if os.getenv("RUN_AWS_INTEGRATION") != "1":
    pytest.skip("Set RUN_AWS_INTEGRATION=1 to run real AWS integration tests", allow_module_level=True)

from aws_object import AwsObject, S3


@pytest.fixture(scope="session")
def region():
    return os.getenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture(scope="session")
def aws_object(region):
    # Assumes AWS creds are configured on the machine (env vars or shared config)
    return AwsObject(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", ""),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
        owner=os.getenv("TEST_OWNER", "integration-test-owner"),
        region_name=region,
    )


def test_s3_create_upload_list_delete_bucket(aws_object, unique_suffix):
    s3_wrapper = S3(aws_object)
    bucket_name = f"cli-int-{unique_suffix}-{aws_object.region_name}".lower()

    s3_client = boto3.client("s3", region_name=aws_object.region_name)

    try:
        # Create
        assert s3_wrapper.create_bucket(bucket_name) is True

        # Upload tiny object
        test_key = "hello.txt"
        test_body = b"hello world"
        from io import BytesIO
        s3_client.upload_fileobj(BytesIO(test_body), bucket_name, test_key)

        # List via wrapper (filter by tags)
        buckets = s3_wrapper.list_buckets()
        assert bucket_name in buckets

        # Fetch object to verify
        obj = s3_client.get_object(Bucket=bucket_name, Key=test_key)
        assert obj["Body"].read() == test_body
    finally:
        # Cleanup: delete object(s) and bucket
        try:
            resp = s3_client.list_object_versions(Bucket=bucket_name)
            to_delete = []
            for v in resp.get("Versions", []) + resp.get("DeleteMarkers", []):
                to_delete.append({"Key": v["Key"], "VersionId": v.get("VersionId")})
            if to_delete:
                s3_client.delete_objects(Bucket=bucket_name, Delete={"Objects": to_delete})
        except Exception:
            pass
        try:
            s3_client.delete_bucket(Bucket=bucket_name)
        except Exception:
            pass
