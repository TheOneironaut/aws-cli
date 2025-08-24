# תיקיית בדיקות (Tests)

תיקייה זו מכילה שני סוגים של בדיקות עבור הפרויקט:

## 1. בדיקות יחידה (Unit Tests) - `test_aws_object.py`

בדיקות אלה **לא** יוצרות משאבים אמיתיים ב-AWS. הן משתמשות ב-mocking כדי לדמות את התגובות מ-AWS.

### מתי להשתמש:
- פיתוח ובדיקה רגילה
- בדיקה לפני העלאה לגרסה חדשה (CI/CD)
- כשאתה רוצה לבדוק את הלוגיקה בלי לשלם כסף

### איך להריץ:
```bash
# הרצת כל הבדיקות
uv run python -m unittest discover tests

# הרצת בדיקות יחידה בלבד
uv run python -m unittest tests.test_aws_object -v
```

## 2. בדיקות אינטגרציה (Integration Tests) - `test_aws_integration.py`

⚠️ **אזהרה: בדיקות אלה יוצרות משאבים אמיתיים ב-AWS ועלולות לעלות כסף!** ⚠️

### מתי להשתמש:
- כשאתה רוצה לוודא שהקוד באמת עובד עם AWS
- לפני שחרור גרסה חדשה לייצור
- כשיש שינויים משמעותיים בקוד

### הכנה לפני הרצה:

הבדיקות יחפשו את פרטי ה-AWS בשלוש דרכים (לפי סדר עדיפות):

#### אפשרות 1: קובץ .env בתיקיית tests (הכי קל!)
צור קובץ `.env` בתיקיית `tests` עם התוכן:
```
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
```
הבדיקות יטענו את זה אוטומטית!

#### אפשרות 2: משתני סביבה
```bash
# ב-PowerShell:
$env:AWS_ACCESS_KEY_ID="your_access_key_here"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key_here"

# או ב-CMD:
set AWS_ACCESS_KEY_ID=your_access_key_here
set AWS_SECRET_ACCESS_KEY=your_secret_key_here
```

#### אפשרות 3: קובץ ~/.aws/credentials (גיבוי אוטומטי)
אם לא נמצאו בשתי הדרכים הקודמות, הבדיקות יחפשו בקובץ:
```
C:\Users\your_username\.aws\credentials
```

הקובץ צריך להכיל:
```
[default]
aws_access_key_id = your_access_key_here
aws_secret_access_key = your_secret_key_here
```

💡 **טיפ:** אם כבר הרצת את הפונקציה `save_creadencial()` בקוד שלך, הקובץ כבר קיים!

2. **וודא שיש לך הרשאות ב-AWS:**
   - יצירת ומחיקת מכונות EC2
   - קריאת פרטי IAM user

### איך להריץ:

#### דרך בטוחה (מומלצת):
```bash
uv run python -c "from tests.test_aws_integration import run_integration_tests; run_integration_tests()"
```
הפקודה הזו תבקש ממך אישור לפני שהיא מתחילה ליצור משאבים.

#### דרך ישירה (למתקדמים):
```bash
uv run python -m unittest tests.test_aws_integration -v
```

### בדיקות זמינות:

1. **`test_aws_credentials_validation`** - בודק שהפרטים שלך ל-AWS תקינים
2. **`test_save_credentials_file`** - בודק שמירת קובץ הפרטים (יכול להחליף את הקובץ הקיים!)
3. **`test_create_ec2_instance`** - 🚨 **מושבת כברירת מחדל** - יוצר מכונת EC2 אמיתית
4. **`test_list_existing_instances`** - מציג מכונות קיימות
5. **`test_instance_start_stop`** - 🚨 **מושבת כברירת מחדל** - מפעיל/עוצר מכונות
6. **`test_add_user_workflow`** - בודק את תהליך הוספת המשתמש

### הפעלת בדיקות מסוכנות:

הבדיקות שיוצרות או משנות משאבים מושבתות כברירת מחדל. כדי להפעיל אותן, הסר את השורה:
```python
@unittest.skip("Skipped by default - uncomment to run...")
```

### ניקוי אוטומטי:

הבדיקות מנסות לנקות אחריהן אוטומטית (למחוק מכונות שנוצרו), אבל **תמיד בדוק ידנית** ב-AWS Console שלא נשארו משאבים.

**חשוב:** הבדיקות יוצרות מכונות עם התגיות:
- `CreatedBy: platform-cli`
- `Owner: amitay` (תואם לפונקציה `get_id()` בקוד שלך)

## דוגמאות שימוש:

### בדיקה מהירה שהכל עובד:
```bash
uv run python -m unittest tests.test_aws_object
```

### בדיקת חיבור ל-AWS (בלי יצירת משאבים):
```bash
uv run python -m unittest tests.test_aws_integration.TestAwsIntegration.test_aws_credentials_validation -v
```

### בדיקה מלאה לפני הפצה:
```bash
# קודם בדיקות יחידה
uv run python -m unittest tests.test_aws_object -v

# אחר כך (בזהירות) בדיקות אינטגרציה
uv run python -c "from tests.test_aws_integration import run_integration_tests; run_integration_tests()"
```

## טיפים חשובים:

1. **תמיד הריץ בדיקות יחידה לפני בדיקות אינטגרציה**
2. **בדוק את החשבון שלך ב-AWS אחרי בדיקות אינטגרציה**
3. **השתמש ב-region זול (כמו us-east-1) לבדיקות**
4. **אל תשכח לעצור/למחוק משאבים אחרי הבדיקה**
5. **שמור גיבוי של קובץ ה-credentials שלך לפני הרצת בדיקות שמשנות אותו**

## פתרון בעיות:

### "AWS credentials not found":
```bash
# ודא שהגדרת את משתני הסביבה:
echo $env:AWS_ACCESS_KEY_ID    # PowerShell
echo %AWS_ACCESS_KEY_ID%       # CMD
```

### "Permission denied":
- בדוק שיש לך הרשאות מתאימות ב-AWS IAM

### מכונות לא נמחקות:
- לך ל-AWS Console > EC2 > Instances
- חפש מכונות עם התגיות: `CreatedBy: platform-cli` ו-`Owner: integration-test`
- מחק אותן ידנית