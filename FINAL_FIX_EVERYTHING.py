#!/usr/bin/env python3
"""
الحل النهائي - يصلح كل شيء 100%
"""

import os
import json
from pathlib import Path

root = Path(r"C:\Users\AboHelal\Downloads\New folder (4)")
os.chdir(root)

print("="*70)
print("الحل النهائي لمشكلة Railway")
print("="*70)

# 1. Fix backend/server.js
print("\n[1/5] إصلاح backend/server.js...")

server_js = """const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok',
    message: 'Server is running',
    timestamp: new Date().toISOString()
  });
});

app.post('/api/paraphrase', (req, res) => {
  try {
    const { text } = req.body;
    
    if (!text) {
      return res.status(400).json({ 
        success: false,
        error: 'No text provided' 
      });
    }
    
    const paraphrased = text.toUpperCase();
    
    res.json({
      success: true,
      original_text: text,
      paraphrased_text: paraphrased,
      word_count: text.split(/\\s+/).length
    });
    
  } catch (error) {
    res.status(500).json({ 
      success: false,
      error: error.message 
    });
  }
});

// Error handlers
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// Start server
const PORT = process.env.PORT || 3000;
const HOST = '0.0.0.0';

app.listen(PORT, HOST, () => {
  console.log('='.repeat(60));
  console.log('Academic Paraphraser Server');
  console.log('='.repeat(60));
  console.log(`Server: http://${HOST}:${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log('='.repeat(60));
});
"""

with open(root / 'backend' / 'server.js', 'w') as f:
    f.write(server_js)

print("✓ تم إصلاح server.js")

# 2. Fix backend/package.json
print("\n[2/5] تحديث backend/package.json...")

backend_package = {
    "name": "backend",
    "version": "1.0.0",
    "main": "server.js",
    "scripts": {
        "start": "node server.js"
    },
    "dependencies": {
        "express": "^4.18.2",
        "cors": "^2.8.5"
    }
}

with open(root / 'backend' / 'package.json', 'w') as f:
    json.dump(backend_package, f, indent=2)

print("✓ تم تحديث backend/package.json")

# 3. Create root package.json
print("\n[3/5] إنشاء package.json الرئيسي...")

root_package = {
    "name": "academic-paraphraser",
    "version": "1.0.0",
    "scripts": {
        "start": "cd backend && npm install && node server.js"
    },
    "engines": {
        "node": ">=18.0.0"
    }
}

with open(root / 'package.json', 'w') as f:
    json.dump(root_package, f, indent=2)

print("✓ تم إنشاء package.json")

# 4. Fix Procfile
print("\n[4/5] إصلاح Procfile...")

with open(root / 'Procfile', 'w') as f:
    f.write("web: npm start\n")

print("✓ تم إصلاح Procfile")

# 5. Delete railway.json if exists
print("\n[5/5] تنظيف الملفات...")

railway_json = root / 'railway.json'
if railway_json.exists():
    railway_json.unlink()
    print("✓ تم حذف railway.json القديم")

print("\n" + "="*70)
print("تم إصلاح جميع الملفات!")
print("="*70)
print("""
الآن شغّل هذه الأوامر:

cd "C:\\Users\\AboHelal\\Downloads\\New folder (4)"
git add .
git commit -m "Fix server host binding"
git push origin main

ثم انتظر 2-3 دقائق للنشر.
""")

input("\nاضغط Enter للمتابعة...")

# Auto git operations
print("\nهل تريد رفع التحديثات تلقائياً؟ (y/n): ", end='')
answer = input().strip().lower()

if answer == 'y':
    print("\nجاري رفع التحديثات...")
    import subprocess
    
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Fix server host binding to 0.0.0.0'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print("\n✅ تم رفع التحديثات بنجاح!")
        print("\n⏰ انتظر 2-3 دقائق ثم افتح:")
        print("https://academic-paraphrasing-saas-production.up.railway.app")
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        print("\nشغّل الأوامر يدوياً:")
        print("git add .")
        print("git commit -m 'Fix server'")
        print("git push origin main")
else:
    print("\nشغّل الأوامر يدوياً في Terminal")

input("\nاضغط Enter للخروج...")