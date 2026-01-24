#!/usr/bin/env python3
"""
إصلاح مشكلة Railway Deploy
"""

import os
import json
from pathlib import Path

root = Path(r"C:\Users\AboHelal\Downloads\New folder (4)")
os.chdir(root)

print("="*60)
print("إصلاح Railway Deployment")
print("="*60)

# 1. Create package.json in root
print("\n[1/4] إنشاء package.json في المجلد الرئيسي...")

root_package = {
    "name": "academic-paraphraser",
    "version": "1.0.0",
    "description": "Academic Paraphrasing SaaS",
    "main": "backend/server.js",
    "scripts": {
        "start": "node backend/server.js",
        "build": "cd backend && npm install"
    },
    "keywords": ["paraphraser", "academic", "saas"],
    "author": "search.one011@gmail.com",
    "license": "MIT",
    "dependencies": {
        "express": "^4.18.2",
        "cors": "^2.8.5",
        "dotenv": "^16.3.1"
    },
    "engines": {
        "node": ">=18.0.0",
        "npm": ">=9.0.0"
    }
}

with open(root / 'package.json', 'w') as f:
    json.dump(root_package, f, indent=2)

print("✓ تم إنشاء package.json")

# 2. Update Procfile
print("\n[2/4] تحديث Procfile...")

with open(root / 'Procfile', 'w') as f:
    f.write("web: npm start")

print("✓ تم تحديث Procfile")

# 3. Create railway.json
print("\n[3/4] إنشاء railway.json...")

railway_config = {
    "build": {
        "builder": "NIXPACKS",
        "buildCommand": "npm install && cd backend && npm install"
    },
    "deploy": {
        "startCommand": "npm start",
        "restartPolicyType": "ON_FAILURE",
        "restartPolicyMaxRetries": 10
    }
}

with open(root / 'railway.json', 'w') as f:
    json.dump(railway_config, f, indent=2)

print("✓ تم إنشاء railway.json")

# 4. Git operations
print("\n[4/4] رفع التحديثات إلى GitHub...")

try:
    import subprocess
    
    subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
    subprocess.run(['git', 'commit', '-m', 'Fix Railway deployment'], 
                  check=True, capture_output=True)
    subprocess.run(['git', 'push', 'origin', 'main'], 
                  check=True, capture_output=True)
    
    print("✓ تم رفع التحديثات")
    
except Exception as e:
    print(f"⚠ خطأ في Git: {e}")

print("\n" + "="*60)
print("تم الإصلاح!")
print("="*60)
print("""
الآن Railway سيعيد النشر تلقائياً.

⏰ انتظر 3-4 دقائق ثم:

1. زر الموقع:
   https://academic-paraphrasing-saas-production.up.railway.app

2. أو تحقق من Railway Dashboard:
   https://railway.app/dashboard

3. أو شغّل:
   python DIAGNOSTIC.py

إذا استمرت المشكلة، تحقق من Railway Logs!
""")

input("\nاضغط Enter للخروج...")