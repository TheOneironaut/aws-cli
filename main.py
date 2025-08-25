import sys
import click
from aws_object import AwsObject, Ec2, S3, Route53


class AwsContext:
    def __init__(self, aws_obj: AwsObject):
        self.aws_obj = aws_obj


@click.group()
@click.option('--aws-access-key-id', envvar='AWS_ACCESS_KEY_ID', prompt='AWS Access Key ID', hide_input=False, required=False)
@click.option('--aws-secret-access-key', envvar='AWS_SECRET_ACCESS_KEY', prompt='AWS Secret Access Key', hide_input=True, required=False)
@click.option('--owner', envvar='AWS_OWNER', prompt='Owner tag', required=False)
@click.option('--region', 'region_name', envvar='AWS_DEFAULT_REGION', default='us-east-1', show_default=True, help='AWS region to use')
@click.pass_context
def cli(ctx: click.Context, aws_access_key_id: str, aws_secret_access_key: str, owner: str, region_name: str):
    """CLI for managing AWS resources based on aws_object module."""
    aws_obj = AwsObject(aws_access_key_id, aws_secret_access_key, owner, region_name)
    ctx.obj = AwsContext(aws_obj)


@cli.command('add-user')
@click.pass_obj
def add_user_cmd(ctx_obj: AwsContext):
    """Save credentials and validate IAM access."""
    click.echo('Saving credentials and validating user...')
    ok = ctx_obj.aws_obj.add_user()
    click.echo(f'User valid: {ok}')
    if not ok:
        sys.exit(1)


# EC2 commands
@cli.group()
@click.pass_obj
def ec2(ctx_obj: AwsContext):
    """Manage EC2 instances."""
    pass


@ec2.command('create')
@click.option('--type', 'instance_type', default='t3.micro', show_default=True, help='EC2 instance type')
@click.option('--image', 'image_id_or_name', default='ami-020cba7c55df1f615', show_default=True, help='AMI ID or known name (ubuntu/amazon-linux)')
@click.pass_obj
def ec2_create(ctx_obj: AwsContext, instance_type: str, image_id_or_name: str):
    inst = Ec2(ctx_obj.aws_obj)
    res = inst.create_ec2(type=instance_type, image_id_or_name=image_id_or_name)
    if res is True:
        click.echo('EC2 instance created')
    else:
        click.echo(str(res))
        sys.exit(1)


@ec2.command('list')
@click.pass_obj
def ec2_list(ctx_obj: AwsContext):
    inst = Ec2(ctx_obj.aws_obj)
    ids = inst.get_id()
    if not ids:
        click.echo('No instances found')
        return
    for i in ids:
        click.echo(f'instance id: {i}')


@ec2.command('stop')
@click.option('--id', 'instance_id', help='Instance ID to stop; if omitted, all owned instances will be stopped')
@click.pass_obj
def ec2_stop(ctx_obj: AwsContext, instance_id: str | None):
    inst = Ec2(ctx_obj.aws_obj)
    if instance_id:
        inst.stop(instance_id)
        click.echo(f'Stopping {instance_id}')
    else:
        res = inst.stop_all()
        if res is True:
            click.echo('Stopping all owned instances')
        else:
            click.echo(str(res))


@ec2.command('start')
@click.option('--id', 'instance_id', help='Instance ID to start; if omitted, all owned instances will be started')
@click.pass_obj
def ec2_start(ctx_obj: AwsContext, instance_id: str | None):
    inst = Ec2(ctx_obj.aws_obj)
    if instance_id:
        inst.start(instance_id)
        click.echo(f'Starting {instance_id}')
    else:
        res = inst.start_all()
        if res is True:
            click.echo('Starting all owned instances')
        else:
            click.echo(str(res))


# S3 commands
@cli.group()
@click.pass_obj
def s3(ctx_obj: AwsContext):
    """Manage S3 buckets and objects."""
    pass


@s3.command('create-bucket')
@click.argument('bucket_name')
@click.pass_obj
def s3_create_bucket(ctx_obj: AwsContext, bucket_name: str):
    client = S3(ctx_obj.aws_obj)
    ok = client.create_bucket(bucket_name)
    if ok:
        click.echo(f'Bucket {bucket_name} created')
    else:
        click.echo('Failed to create bucket')
        sys.exit(1)


@s3.command('upload')
@click.option('--bucket', 'bucket_name', required=True, help='Bucket name')
@click.argument('file_path')
@click.pass_obj
def s3_upload(ctx_obj: AwsContext, bucket_name: str, file_path: str):
    client = S3(ctx_obj.aws_obj)
    ok = client.upload_file(bucket_name, file_path)
    if ok:
        click.echo(f'Uploaded {file_path} to s3://{bucket_name}/')
    else:
        click.echo('Failed to upload file')
        sys.exit(1)


@s3.command('list-buckets')
@click.pass_obj
def s3_list_buckets(ctx_obj: AwsContext):
    client = S3(ctx_obj.aws_obj)
    buckets = client.list_buckets()
    if not buckets:
        click.echo('No owned buckets found')
        return
    for b in buckets:
        click.echo(b)


# Route53 commands
@cli.group()
@click.pass_obj
def route53(ctx_obj: AwsContext):
    """Manage Route53 hosted zones and records."""
    pass


@route53.command('create-zone')
@click.argument('domain_name')
@click.pass_obj
def r53_create_zone(ctx_obj: AwsContext, domain_name: str):
    r53 = Route53(ctx_obj.aws_obj, domain_name)
    click.echo(f'Hosted zone created: {r53.resourceId}')


@route53.command('create-record')
@click.argument('zone_domain')
@click.argument('name')
@click.argument('ip')
@click.option('--type', 'dns_type', default='A', show_default=True)
@click.option('--ttl', default=300, show_default=True, type=int)
@click.pass_obj
def r53_create_record(ctx_obj: AwsContext, zone_domain: str, name: str, ip: str, dns_type: str, ttl: int):
    r53 = Route53(ctx_obj.aws_obj, zone_domain)
    resp = r53.create_record(name, ip, dns_type=dns_type, ttl=ttl)
    code = resp.get('ResponseMetadata', {}).get('HTTPStatusCode')
    click.echo(f'Record create status: {code}')


@route53.command('update-record')
@click.argument('zone_domain')
@click.argument('name')
@click.option('--type', 'dns_type', default='A', show_default=True)
@click.option('--ip')
@click.option('--ttl', type=int)
@click.pass_obj
def r53_update_record(ctx_obj: AwsContext, zone_domain: str, name: str, dns_type: str, ip: str | None, ttl: int | None):
    r53 = Route53(ctx_obj.aws_obj, zone_domain)
    resp = r53.update_record(name, dns_type, ip=ip, ttl=ttl)
    if isinstance(resp, str):
        click.echo(resp)
        sys.exit(1)
    code = resp.get('ResponseMetadata', {}).get('HTTPStatusCode')
    click.echo(f'Record update status: {code}')


@route53.command('delete-record')
@click.argument('zone_domain')
@click.argument('name')
@click.pass_obj
def r53_delete_record(ctx_obj: AwsContext, zone_domain: str, name: str):
    r53 = Route53(ctx_obj.aws_obj, zone_domain)
    resp = r53.delete_record(name)
    code = resp.get('ResponseMetadata', {}).get('HTTPStatusCode')
    click.echo(f'Record delete status: {code}')


if __name__ == '__main__':
    cli()
