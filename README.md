# AWS CLI Tool

כלי פיתון לניהול משאבי AWS - יצירה וניהול של משתמשים ומכונות EC2.

## תכונות

- **ניהול משתמשים AWS**: הוספת משתמשים חדשים ובדיקת תקינותם
- **ניהול EC2**: יצירה, עצירה והפעלה של מכונות EC2
- **ניהול פרטים בטוח**: תמיכה במשתני סביבה וקבצי credentials
- **בדיקות מקיפות**: Unit tests ואינטגרציה tests

## התקנה

`ash
# שכפול הפרוייקט
git clone https://github.com/your-username/aws-cli.git
cd aws-cli

# התקנת dependencies
uv sync
`

## הגדרת פרטי AWS

 **חשוב**: אל תשמור פרטי AWS בקוד! השתמש באפשרויות הבטוחות הבאות:

### אפשרות 1: משתני סביבה (מומלץ)
`powershell
# PowerShell
$env:AWS_ACCESS_KEY_ID="your_access_key_here"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key_here"
`

### אפשרות 2: קובץ .env
צור קובץ .env בשורש הפרוייקט:
`
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
`

## שימוש

`ash
# הרצה בסיסית
uv run python main.py
`

## בדיקות

### בדיקות יחידה (מומלץ לפיתוח)
`ash
uv run python -m unittest tests.test_aws_object -v
`

### בדיקות אינטגרציה (זהירות - עלויות AWS!)
`ash
uv run python -c "from tests.test_aws_integration import run_integration_tests; run_integration_tests()"
`

## אבטחה

-  אין פרטי AWS בקוד
-  gitignore מקיף מגן על קבצים רגישים
-  בדיקות אוטומטיות עם pre-commit hooks

## אזהרות

-  בדיקות אינטגרציה יוצרות משאבים אמיתיים ב-AWS
-  אל תעלה אף פעם מפתחות AWS לגיט
-  השתמש בבדיקות יחידה לפיתוח שוטף
