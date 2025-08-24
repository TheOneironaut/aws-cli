"""
S3 Test Cleanup Utilities

This module contains helper functions for cleaning up S3 test resources.
These functions should only be used in test environments.
"""

import boto3


def delete_bucket_completely(s3_client, bucket_name):
    """
    Helper function to delete a bucket and all its contents (for tests only).
    
    Args:
        s3_client: boto3 S3 client
        bucket_name (str): Name of the bucket to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # First, delete all objects in the bucket
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' in response:
            # Delete all objects
            objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
            
            # Delete in batches of 1000 (AWS limit)
            for i in range(0, len(objects_to_delete), 1000):
                batch = objects_to_delete[i:i+1000]
                delete_response = s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={'Objects': batch}
                )
                deleted_count = len(delete_response.get('Deleted', []))
                if deleted_count > 0:
                    print(f"Deleted {deleted_count} objects")
        
        # Delete all object versions (if versioning is enabled)
        try:
            versions_response = s3_client.list_object_versions(Bucket=bucket_name)
            versions_to_delete = []
            
            # Add all versions
            if 'Versions' in versions_response:
                for version in versions_response['Versions']:
                    versions_to_delete.append({
                        'Key': version['Key'],
                        'VersionId': version['VersionId']
                    })
            
            # Add all delete markers
            if 'DeleteMarkers' in versions_response:
                for marker in versions_response['DeleteMarkers']:
                    versions_to_delete.append({
                        'Key': marker['Key'],
                        'VersionId': marker['VersionId']
                    })
            
            # Delete versions in batches
            if versions_to_delete:
                for i in range(0, len(versions_to_delete), 1000):
                    batch = versions_to_delete[i:i+1000]
                    s3_client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': batch}
                    )
        except Exception:
            # Versioning might not be enabled, continue
            pass
        
        # Finally, delete the bucket itself
        s3_client.delete_bucket(Bucket=bucket_name)
        print(f"✓ Bucket {bucket_name} deleted")
        return True
        
    except Exception as e:
        print(f"Error deleting bucket {bucket_name}: {e}")
        return False


def cleanup_test_buckets_by_prefix(s3_client, prefix="test-bucket"):
    """
    Helper function to delete all buckets with given prefix (for tests only).
    
    Args:
        s3_client: boto3 S3 client
        prefix (str): Bucket name prefix to search for
        
    Returns:
        bool: True if all buckets deleted successfully, False otherwise
    """
    try:
        response = s3_client.list_buckets()
        test_buckets = [bucket['Name'] for bucket in response['Buckets'] 
                      if bucket['Name'].startswith(prefix)]
        
        if not test_buckets:
            print(f"No buckets found with prefix '{prefix}'")
            return True
            
        print(f"Found {len(test_buckets)} buckets to delete:")
        for bucket in test_buckets:
            print(f"  - {bucket}")
        
        deleted_count = 0
        for bucket_name in test_buckets:
            print(f"\nCleaning up bucket: {bucket_name}")
            if delete_bucket_completely(s3_client, bucket_name):
                deleted_count += 1
            else:
                print(f"✗ Failed to delete bucket {bucket_name}")
        
        print(f"\n✓ Cleanup completed: {deleted_count}/{len(test_buckets)} buckets deleted")
        return deleted_count == len(test_buckets)
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        return False


def cleanup_all_test_buckets():
    """
    Clean up all test buckets - for use in tests only.
    
    Returns:
        bool: True if cleanup successful, False otherwise
    """
    print("=" * 60)
    print("S3 TEST CLEANUP UTILITY")
    print("=" * 60)
    
    try:
        # Try to get credentials from environment or file
        import os
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        if not aws_access_key_id or not aws_secret_access_key:
            # Try to read from credentials file
            credentials_path = os.path.join(os.path.expanduser('~'), '.aws', 'credentials')
            try:
                with open(credentials_path, 'r') as f:
                    content = f.read()
                    
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('aws_access_key_id'):
                        aws_access_key_id = line.split('=', 1)[1].strip()
                    elif line.startswith('aws_secret_access_key'):
                        aws_secret_access_key = line.split('=', 1)[1].strip()
            except Exception:
                pass
        
        if not aws_access_key_id or not aws_secret_access_key:
            print("Error: AWS credentials not found")
            return False
        
        # Create S3 client
        s3_client = boto3.client('s3')
        
        # Clean up different types of test buckets
        test_prefixes = [
            "test-bucket",
            "test-s3-",
            "test-integration-",
            "test-tagging-"
        ]
        
        total_cleaned = 0
        for prefix in test_prefixes:
            print(f"\nChecking for buckets with prefix: {prefix}")
            if cleanup_test_buckets_by_prefix(s3_client, prefix):
                print(f"✓ Cleanup completed for prefix: {prefix}")
            else:
                print(f"⚠ Some issues during cleanup for prefix: {prefix}")
        
        print("\n" + "=" * 60)
        print("TEST CLEANUP COMPLETE")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        return False


if __name__ == "__main__":
    # Allow direct execution for cleanup
    cleanup_all_test_buckets()