# Academic Paraphraser — 5 Models 📚

> **إزاي تشغّل الكود؟ / How to run the code?**

---

## 🇦🇪 تعليمات التشغيل (عربي)

### المتطلبات
- [Node.js](https://nodejs.org/) نسخة **18 أو أحدث**
- اتصال بالإنترنت لتحميل المكتبات

### خطوات التشغيل المحلي

```bash
# 1. افتح مجلد المشروع
cd academic-paraphrasing-saas

# 2. ثبّت المكتبات (مرة واحدة فقط)
npm install

# 3. شغّل السيرفر
npm start
```

بعد ما يشتغل السيرفر، افتح المتصفح وروح على:

```
http://localhost:3000
```

> **ملاحظة:** لو حبيت تغيير رقم البورت، اعمل ملف `.env` في المجلد الرئيسي وحط فيه:
> ```
> PORT=5000
> ```
> وبعدين افتح `http://localhost:5000`

---

## 🇬🇧 Run Instructions (English)

### Prerequisites
- [Node.js](https://nodejs.org/) version **18 or newer**
- Internet connection (first install only)

### Local development

```bash
# 1. Enter the project folder
cd academic-paraphrasing-saas

# 2. Install dependencies (only once)
npm install

# 3. Start the server
npm start
```

Then open your browser at:

```
http://localhost:3000
```

> **Tip:** To change the port, create a `.env` file in the project root:
> ```
> PORT=5000
> ```
> Then browse to `http://localhost:5000`

### Deploy to Railway / Render / Heroku

The project is ready to deploy with zero configuration:

| Platform | Steps |
|----------|-------|
| **Railway** | Push to GitHub → New Project → Deploy from repo |
| **Render** | New Web Service → connect repo → Build: `npm install` · Start: `npm start` |
| **Heroku** | `git push heroku main` (Procfile already included) |

The `Procfile` is already configured: `web: node server.js`

---

## 📡 API Reference

### `GET /api/health`
Returns server status.

```json
{ "status": "ok", "message": "Server running", "ts": "..." }
```

### `POST /api/paraphrase`

**Request body:**
```json
{
  "text": "Your academic text here...",
  "level": "maximum"
}
```

**Response:**
```json
{
  "success": true,
  "models": [
    { "style": "Passive Evidence",        "text": "It has been established that..." },
    { "style": "Evidence-Led",            "text": "The weight of evidence suggests..." },
    { "style": "Theoretical / Analytical","text": "From a theoretical standpoint..." },
    { "style": "Literature Attribution",  "text": "The scholarly literature converges..." },
    { "style": "Temporal & Critical",     "text": "In the contemporary scholarly context..." }
  ]
}
```

---

## 📁 Project Structure

```
academic-paraphrasing-saas/
├── server.js          ← Express server + paraphrasing logic
├── public/
│   └── index.html     ← Two-panel UI (Arabic + English, RTL-ready)
├── package.json
├── Procfile           ← For Heroku/Railway deployment
└── .env               ← Local environment variables (not committed)
```

---

Contact: search.one011@gmail.com
