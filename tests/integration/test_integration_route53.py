import os
import time
import boto3
import pytest

if os.getenv("RUN_AWS_INTEGRATION") != "1":
    pytest.skip("Set RUN_AWS_INTEGRATION=1 to run real AWS integration tests", allow_module_level=True)

from aws_object import AwsObject, Route53


@pytest.fixture(scope="session")
def aws_object():
    return AwsObject(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", ""),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
        owner=os.getenv("TEST_OWNER", "integration-test-owner"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    )


def test_route53_zone_record_lifecycle(aws_object, unique_suffix):
    # Some domains are reserved by AWS (like example.com); try a randomized .com subdomain
    domain = f"cli-int-{unique_suffix}.com"
    try:
        r53 = Route53(aws_object, domain)
    except Exception as e:
        import botocore
        if isinstance(e, botocore.exceptions.ClientError) and e.response.get('Error', {}).get('Code') == 'InvalidDomainName':
            pytest.skip(f"Domain reserved or invalid for hosted zone: {domain}")
        raise
    r53_client = boto3.client("route53")

    # Create A record
    name = f"www.{domain}"
    resp = r53.create_record(name, "1.2.3.4")
    assert resp['ResponseMetadata']['HTTPStatusCode'] == 200

    # Upsert to change IP
    resp = r53.update_record(name, "A", ip="5.6.7.8", ttl=60)
    assert resp['ResponseMetadata']['HTTPStatusCode'] == 200

    # Validate record exists with new IP
    sets = r53_client.list_resource_record_sets(HostedZoneId=r53.resourceId)
    a_records = [r for r in sets['ResourceRecordSets'] if r['Type'] == 'A' and r['Name'] == (name if name.endswith('.') else name + '.')]
    assert a_records and a_records[0]['ResourceRecords'][0]['Value'] == '5.6.7.8'

    # Delete the record
    resp = r53.delete_record(name)
    assert resp['ResponseMetadata']['HTTPStatusCode'] == 200

    # Cleanup: delete hosted zone (must remove NS/SOA first)
    try:
        # Delete all non-NS/SOA first (should be none after deletion above)
        sets = r53_client.list_resource_record_sets(HostedZoneId=r53.resourceId)
        for rr in sets['ResourceRecordSets']:
            if rr['Type'] in ('NS', 'SOA'):
                continue
            r53_client.change_resource_record_sets(
                HostedZoneId=r53.resourceId,
                ChangeBatch={
                    'Changes': [
                        {
                            'Action': 'DELETE',
                            'ResourceRecordSet': rr
                        }
                    ]
                }
            )
        # Finally, delete the zone
        # Some propagation time might be needed
        time.sleep(2)
        # r53.resourceId is the full id (/hostedzone/XYZ), delete_hosted_zone expects the short id in Id param
        zone_id_short = r53.resourceId.split('/')[-1]
        r53_client.delete_hosted_zone(Id=zone_id_short)
    except Exception:
        pass
