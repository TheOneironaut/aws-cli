# AWS CLI Tool

כלי פשוט לניהול שירותי AWS, כולל EC2, S3 ו-Route53.

## תכונות

- **ניהול EC2**: יצירה, עצירה, הפעלה, ומחיקה של מכונות וירטואליות.
- **ניהול S3**: יצירת באקטים, העלאת קבצים ורשימת באקטים בבעלותך.
- **ניהול Route53**: יצירה וניהול של Hosted Zones ורשומות DNS.
- **ניהול זהויות מאובטח**: טיפול בטוח בפרטי גישה של AWS.
- **בדיקות אוטומטיות**: מערך בדיקות יחידה מקיף המשתמש ב-`moto` לסימולציה של שירותי AWS.
- **Pre-commit Hooks**: הרצת בדיקות אוטומטית לפני כל commit כדי להבטיח את תקינות הקוד.

## התקנה

1.  **שכפול הפרויקט:**
    ```bash
    git clone https://github.com/your-username/aws-cli.git
    cd aws-cli
    ```

2.  **התקנת תלויות:**
    הפרויקט משתמש ב-`uv` לניהול סביבות ותלויות.
    ```bash
    uv sync --dev
    ```

3.  **הגדרת Pre-commit Hooks:**
    כדי להפעיל את הבדיקות האוטומטיות לפני כל commit:
    ```bash
    pre-commit install
    ```

## הגדרת פרטי גישה ל-AWS

הכלי דורש פרטי גישה ל-AWS. ניתן להגדיר אותם באמצעות משתני סביבה:

```powershell
# PowerShell
$env:AWS_ACCESS_KEY_ID="your_access_key_here"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key_here"
```

לחלופין, ניתן ליצור קובץ `.env` בתיקיית הפרויקט.

## הרצה

להרצת הכלי:
```bash
uv run python main.py
```

## בדיקות

הפרויקט כולל מערך בדיקות יחידה מקיף המדמה את שירותי AWS באמצעות `moto`.

להרצת הבדיקות באופן ידני:
```bash
uv run pytest
```

הבדיקות ירוצו גם באופן אוטומטי לפני כל `commit` לאחר התקנת ה-hooks. כיסוי הקוד המינימלי הנדרש הוא 80%.

## מבנה הפרויקט

```
.
├── .pre-commit-config.yaml # הגדרות עבור pre-commit hooks
├── aws_object.py           # לוגיקה לניהול משאבי AWS
Use pytest to run the unit tests. Real AWS integration tests are provided under `tests/integration` and are skipped by default.

### Unit tests
Run all fast, mocked tests:

```powershell
uv run pytest -q
```

### Real AWS integration tests (optional)
These tests create real AWS resources (EC2, S3 buckets/objects, Route53 hosted zones/records). They are skipped unless you explicitly opt in. They attempt to clean up after themselves, but you should still run them in a dedicated account or sandbox project.

Requirements:
- Valid AWS credentials configured (env vars or `~/.aws`)
- Set `TEST_OWNER` to tag created resources (defaults to `integration-test-owner`)

PowerShell example:

```powershell
$env:RUN_AWS_INTEGRATION = "1"; `
$env:AWS_DEFAULT_REGION = "us-east-1"; `
# Optionally provide creds if not using shared config/profile
# $env:AWS_ACCESS_KEY_ID = "..."; $env:AWS_SECRET_ACCESS_KEY = "..."; `
$env:TEST_OWNER = "your-name"; `
uv run pytest -q tests/integration
```

Notes:
- S3 bucket names are randomized per run to avoid collisions.
- EC2 test launches a single `t3.micro` in the chosen region and terminates it at the end.
- Route53 test creates a temporary hosted zone under a randomized subdomain and deletes it (including records).
- If a cleanup step fails due to eventual consistency, you may need to remove the resource manually.
├── pyproject.toml          # הגדרות פרויקט ותלויות
├── README.md               # קובץ זה
└── tests/                  # תיקיית הבדיקות
    ├── test_aws_object.py
    ├── test_ec2.py
    ├── test_route53.py
    └── test_s3.py
```
