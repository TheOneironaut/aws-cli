# AWS CLI Tool

��� ����� ������ ����� AWS - ����� ������ �� ������� ������� EC2.

## ������

- **����� ������� AWS**: ����� ������� ����� ������ �������
- **����� EC2**: �����, ����� ������ �� ������ EC2
- **����� ����� ����**: ����� ������ ����� ����� credentials
- **������ ������**: Unit tests ���������� tests

## �����

`ash
# ����� ��������
git clone https://github.com/your-username/aws-cli.git
cd aws-cli

# ����� dependencies
uv sync
`

## ����� ���� AWS

 **����**: �� ����� ���� AWS ����! ����� ��������� ������� �����:

### ������ 1: ����� ����� (�����)
`powershell
# PowerShell
$env:AWS_ACCESS_KEY_ID="your_access_key_here"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key_here"
`

### ������ 2: ���� .env
��� ���� .env ����� ��������:
`
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
`

## �����

`ash
# ���� ������
uv run python main.py
`

## ������

### ������ ����� (����� ������)
`ash
uv run python -m unittest tests.test_aws_object -v
`

### ������ ��������� (������ - ������ AWS!)
`ash
uv run python -c "from tests.test_aws_integration import run_integration_tests; run_integration_tests()"
`

## �����

-  ��� ���� AWS ����
-  gitignore ���� ��� �� ����� ������
-  ������ ��������� �� pre-commit hooks

## ������

-  ������ ��������� ������ ������ ������� �-AWS
-  �� ���� �� ��� ������ AWS ����
-  ����� ������� ����� ������ ����
