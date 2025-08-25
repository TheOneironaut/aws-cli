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

להרצת ה-CLI עם `uv` (ללא התקנה):

```powershell
# עזרה כללית
uv run python main.py --help

# שימוש עם משתני סביבה (מומלץ)
$env:AWS_ACCESS_KEY_ID = "..."; $env:AWS_SECRET_ACCESS_KEY = "..."; $env:AWS_OWNER = "your-name"; `
uv run python main.py ec2 list

# או העברת פרמטרים בשורת הפקודה
uv run python main.py --aws-access-key-id "..." --aws-secret-access-key "..." --owner "your-name" ec2 list
```

הערה: הוגדר גם entry point בשם `aws-cli` ב-`pyproject.toml`, אבל כדי להשתמש בו כפקודה גלובלית יש להתקין את החבילה ל-venv:

```powershell
uv pip install -e .
aws-cli --help
```

### דוגמאות שימוש

```powershell
# הוספת משתמש (שומר credentials לקובץ ומשתמש ב-IAM GetUser לאימות)
uv run python main.py add-user

# EC2
uv run python main.py ec2 create --type t3.micro --image ubuntu
uv run python main.py ec2 list
uv run python main.py ec2 stop           # עוצר את כל המכונות המתויגות בבעלותך
uv run python main.py ec2 stop --id i-0123456789abcdef0
uv run python main.py ec2 start          # מפעיל את כל המכונות המתויגות בבעלותך

# S3
uv run python main.py s3 create-bucket my-bucket-name
uv run python main.py s3 upload --bucket my-bucket-name ./path/to/file.txt
uv run python main.py s3 list-buckets

# Route53
uv run python main.py route53 create-zone example.com
uv run python main.py route53 create-record example.com www.example.com 1.2.3.4 --type A --ttl 60
uv run python main.py route53 update-record example.com www.example.com --type A --ip 2.2.2.2 --ttl 120
uv run python main.py route53 delete-record example.com www.example.com
```

## הרצה בקונטיינר (Docker) באופן אינטראקטיבי

כעת הקונטיינר נפתח ל-shell, ואתה יכול להריץ בתוכו את `awsctl` ישירות ולקבל פרומפט להזנת פרטים (אין חובה להעביר משתני סביבה):

```powershell
# Build image (מריצים מתיקיית הפרויקט)
docker build -t awsctl:latest .

# פתיחת shell אינטראקטיבי בתוך הקונטיינר ומיפוי התיקייה הנוכחית לעבודה נוחה
docker run --rm -it -v ${PWD}:/work -w /work awsctl:latest

# בתוך ה-shell שנפתח:
awsctl --help
awsctl ec2 list
# במידה ואין משתני סביבה, תתבקש/י להזין: AWS Access Key ID, Secret, Owner וכו'
```

טיפים:
- כדי לשמור קובץ credentials ביציאה מחוץ לקונטיינר, ניתן למפות את תיקיית ה-Home:
    - בלינוקס/מק: `-v ${HOME}:/root`
    - ב-Windows (PowerShell): `-v ${env:USERPROFILE}:/root`
- אפשר גם להמשיך להעביר משתני סביבה אם נוח יותר: `-e AWS_ACCESS_KEY_ID=... -e AWS_SECRET_ACCESS_KEY=... -e AWS_OWNER=...`.

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

## הרצה כפקודה מקומית שמריצה Docker מאחורי הקלעים

כדי להריץ `awsctl` ישירות מהמחשב אבל בפועל בתוך הקונטיינר, צור/השתמש בעוטפים שבפרויקט:

1) ודא שבנית את האימג׳:
```powershell
docker build -t awsctl:latest .
```

2) Windows PowerShell:
     - הפעל:
         ```powershell
         .\scripts\awsctl.ps1 --help
         .\scripts\awsctl.ps1 ec2 list
         ```
     - כדי לקרוא לפקודה כ-`awsctl` מכל מקום, הוסף Alias ב-Profile:
         ```powershell
         notepad $PROFILE
         # הוסף שורה:
         Set-Alias awsctl "C:\\path\\to\\repo\\scripts\\awsctl.ps1"
         ```

3) Linux/Mac:
     - עשה את הסקריפט להרצה והעתק לנתיב ב-PATH:
         ```bash
         chmod +x scripts/awsctl
         sudo cp scripts/awsctl /usr/local/bin/awsctl
         awsctl --help
         awsctl ec2 list
         ```

הסקריפטים ממפים אוטומטית את התיקייה הנוכחית ל-`/work` ואת תיקיית ה-Home ל-`/root`, כך שקבצי `~/.aws/credentials` יישמרו מחוץ לקונטיינר ותוכל/י לעבוד עם קבצים מקומיים.
