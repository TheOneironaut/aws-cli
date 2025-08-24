# AWS CLI T## התקנה

```bash
# שכפול הפרויקט
gi## הרצה

```## בדיקות

### בדיקות יחידה (ללא תקשורת)
```bash
uv run python -m unittest tests.test_aws_object -v
```

### בדיקות אינטגרציה (זהירות - צריכות AWS!)
```bash
uv run python -c "from tests.test_aws_integration import run_integration_tests; run_integration_tests()"
``` התוכנה
uv run python main.py
```e https://github.com/your-username/aws-cli.git
cd aws-cli

# התקנת תלויות
uv sync
```יתון פשוט לניהול AWS - מתמחה במציאת ומחיקת אינסטנסים של EC2.

## תכונות

- **חיבור לשירותי AWS**: חיבור מאובטח לשירותי הענן של אמזון
- **ניהול EC2**: הצגה, חיפוש וניהול של אינסטנסי EC2
- **ניהול זהויות בטוח**: טיפול מאובטח בפרטי גישה (credentials)
- **בדיקות יחידה**: מערכת Unit tests תחת תיקיית tests

## �����

`ash
# ����� ��������
git clone https://github.com/your-username/aws-cli.git
cd aws-cli

# ����� dependencies
uv sync
`

## הגדרת זהות AWS

⚠️ **חשוב**: אל תשמור זהות AWS בקוד! השתמש באחת השיטות הבאות:

### שיטה 1: משתני סביבה (מומלץ)
```powershell
# PowerShell
$env:AWS_ACCESS_KEY_ID="your_access_key_here"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key_here"
```

### שיטה 2: קובץ .env
צור קובץ .env בתיקיית הפרויקט:
```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
```

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

## מטלות

- [ ] הוספת זהות AWS חסרה
- [ ] הוספת gitignore כדי למנוע דליפת סודות
- [ ] הוספת בדיקות אוטומטיות עם pre-commit hooks

## זהירות

- ⚠️ בדיקות האינטגרציה עלולות לגרום לחיובים ב-AWS
- 🔐 אל תשתף את פרטי הגישה AWS שלך
- 🧪 הריצו בדיקות בסביבת פיתוח בלבד

## מבנה הפרויקט

```
├── aws_object.py          # המחלקה הראשית לניהול AWS
├── main.py               # נקודת הכניסה לתוכנה
├── pyproject.toml        # הגדרות פרויקט ותלויות
├── tests/                # תיקיית בדיקות
│   ├── test_aws_object.py
│   └── test_aws_integration.py
└── README.md            # קובץ זה
```

## רישיון

פרויקט זה מוגש תחת רישיון MIT.
