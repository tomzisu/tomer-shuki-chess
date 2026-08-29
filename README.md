# ♟️ Tomer & Shuki Daily Chess Web App

משחק שחמט יומי אינטראקטיבי ומותאם למובייל בין **תומר** (לבן) לבין **שוקי** (שחור), הפועל כ-Web App מעל Google Apps Script, מסתנכרן בזמן אמת ל-Google Sheets ומנוהל על ידי מנוע AI אוטונומי.

---

## 🌟 תכונות מרכזיות (Key Features)

1. **ממשק משתמש מתקדם (Mobile-First Web App):**
   - מותאם במיוחד למכשירי אייפון (iOS Safari) ואנדרואיד.
   - תמיכה מלאה בהוספה למסך הבית (PWA / Add to Home Screen) עם סמליל (Apple Touch Icon) ייעודי וסרגל סטטוס מותאם (Black-Translucent).
   - ממשק כהה (Dark Theme) בעיצוב נקי ויוקרתי.
   - לוח שחמט רספונסיבי מבוסס `chessboard.js` ו-`chess.js`.

2. **אנימציות והחלקה חלקה (Smooth Piece Animation):**
   - אנימציית החלקה ויזואלית מלאה בכל מהלך.
   - חצים וסרגל ניווט לצפייה בהיסטוריית מהלכים קדימה ואחורה עם חיווי צבע ברור: `מהלך X: (לבן)` ו-`מהלך Y: (שחור)`.

3. **סנכרון ענן מלא ל-Google Sheets:**
   - לוח המשחק נשמר בגיליון Google Sheets (גיליונות `GameState` ו-`MoveHistory`).
   - מעקב אחר מצב הלוח (FEN), היסטוריית מהלכים ב-PGN וב-UCI, שחקן נוכחי וזמני ביצוע.

4. **אבטחה ופרטיות (Security & Privacy):**
   - אפליקציית ה-Web App מוגדרת ברמת הרשאה `MYSELF` (רק החשבון המורשה של תומר יכול לגשת).
   - ללא שמירת סודות, מפתחות API או טוקנים בקוד.

5. **מנוע בינה מלאכותית אוטונומי לשוקי (AI Engine & Watcher):**
   - סקריפט פייתון אוטונומי (`chess_manager.py`) המנטר את הגיליון, מחשב מהלכים טקטיים ברמת חובב טבעית ומעדכן את המהלך של שוקי.

---

## 📁 מבנה הקבצים בפרויקט

| קובץ | תיאור |
|---|---|
| `Code.js` | קוד השרת של Google Apps Script המנהל את ה-Web App, קריאות ה-API ועדכון ה-Google Sheets. |
| `index.html` | ממשק ה-Web App המלא (HTML, CSS, JS), כולל סמלילי Base64, מנוע הלוח, והאנימציות. |
| `appsscript.json` | קובץ ה-Manifest של Google Apps Script עם הגדרות אזור זמן ורמת הרשאת Web App. |
| `chess_manager.py` | מנוע הפייתון של שוקי לחישוב מהלכים, איפוס וניטור המשחק ב-Google Sheets. |
| `.gitignore` | חסימת העלאת קובצי סודות, קונפיגורציות מקומיות וסביבות וירטואליות. |

---

## 🚀 פריסה והרצה (Deployment)

### פריסת ה-Web App ב-Google Apps Script
1. ניתן לערוך ולפרוס באמצעות [Google Clasp](https://github.com/google/clasp):
   ```bash
   clasp push
   clasp deploy --description "Release"
   ```
2. או להעתיק את `Code.js`, `index.html` ו-`appsscript.json` ישירות לעורך ה-Apps Script.

### הרצת מנוע השחמט של שוקי (Python)
דרישות קדם:
```bash
pip install python-chess
```

פקודות ניהול:
- בדיקת מצב המשחק הנוכחי:
  ```bash
  python chess_manager.py status
  ```
- ביצוע מהלך עבור שוקי:
  ```bash
  python chess_manager.py move
  ```
- איפוס המשחק ללוח פתיחה:
  ```bash
  python chess_manager.py reset w
  ```
- הפעלת שירות ניטור (Watcher):
  ```bash
  python chess_manager.py watch 10
  ```

---

## 📱 הוספת האפליקציה למסך הבית באייפון (iOS)

1. פתח את קישור ה-Web App בדפדפן **Safari**.
2. לחץ על כפתור השיתוף (Share Icon) בתחתית המסך.
3. בחר באפשרות **"הוסף למסך הבית"** (Add to Home Screen).
4. האפליקציה תישמר עם הסמליל הכהה הייעודי ותיפתח כמסך מלא וחלק.
