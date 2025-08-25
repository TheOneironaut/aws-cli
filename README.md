# AWS CLI Tool

A simple command-line tool for managing common AWS services like EC2, S3, and Route53.

## Installation

Make sure you have Docker and Git installed on your system.

Run the following command in your terminal to install the tool:

```bash
curl -fsSL https://raw.githubusercontent.com/TheOneironaut/aws-cli/master/scripts/install.sh | sudo bash
```

## Initial Setup

Before using the tool, you need to configure your AWS credentials:

```bash
awsctl add-user
```

You will be prompted to enter your AWS Access Key ID, Secret Access Key, and an "Owner" tag, which helps in identifying resources created by this tool.

## Running Tests

To run the integration tests, use the following command:

```bash
uv run pytest -q tests/integration
```

## Commands

Here is a list of available commands and how to use them.

### General

- **`add-user`**: Save and validate AWS credentials.
  ```bash
  awsctl add-user
  ```

### EC2 - Virtual Machines

- **`ec2 create`**: Create a new EC2 instance.
  ```bash
  # Create a default t3.micro instance
  awsctl ec2 create

  # Create a specific type of instance
  awsctl ec2 create --type t2.large --image ami-0abcdef1234567890
  ```

- **`ec2 list`**: List all your EC2 instances.
  ```bash
  awsctl ec2 list
  ```

- **`ec2 stop`**: Stop an EC2 instance.
  ```bash
  # Stop a specific instance
  awsctl ec2 stop --id i-0123456789abcdef0

  # Stop all instances managed by you
  awsctl ec2 stop
  ```

- **`ec2 start`**: Start an EC2 instance.
  ```bash
  # Start a specific instance
  awsctl ec2 start --id i-0123456789abcdef0

  # Start all instances managed by you
  awsctl ec2 start
  ```

### S3 - Object Storage

- **`s3 create-bucket`**: Create a new S3 bucket.
  ```bash
  awsctl s3 create-bucket my-unique-bucket-name
  ```

- **`s3 upload`**: Upload a file to an S3 bucket.
  ```bash
  awsctl s3 upload --bucket my-unique-bucket-name ./local-file.txt
  ```

- **`s3 list-buckets`**: List all S3 buckets you own.
  ```bash
  awsctl s3 list-buckets
  ```

### Route53 - DNS Management

- **`route53 create-zone`**: Create a new hosted zone for a domain.
  ```bash
  awsctl route53 create-zone example.com
  ```

- **`route53 create-record`**: Create a DNS record in a hosted zone.
  ```bash
  awsctl route53 create-record example.com www 192.0.2.1 --type A --ttl 300
  ```

- **`route53 update-record`**: Update an existing DNS record.
  ```bash
  awsctl route53 update-record example.com www --ip 198.51.100.1
  ```

- **`route53 delete-record`**: Delete a DNS record.
  ```bash
  awsctl route53 delete-record example.com www
  ```
