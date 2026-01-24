#!/usr/bin/env python3
import urllib.request
import json

print("="*60)
print("فحص حالة Railway")
print("="*60)

url = "https://academic-paraphrasing-saas-production.up.railway.app/api/health"

print(f"\nجاري الاتصال بـ: {url}")

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode())
        print("\n✅ الـ API يعمل!")
        print(f"الحالة: {data.get('status')}")
        print(f"الرسالة: {data.get('message')}")
except urllib.error.HTTPError as e:
    print(f"\n❌ HTTP Error: {e.code}")
    print(f"السبب: {e.reason}")
except urllib.error.URLError as e:
    print(f"\n❌ URL Error: {e.reason}")
except Exception as e:
    print(f"\n❌ خطأ: {e}")

print("\n" + "="*60)
print("التوصيات:")
print("="*60)
print("""
1. تحقق من Railway Logs
2. قد يكون Railway ما زال يبني المشروع
3. قد تحتاج إلى إعادة تشغيل Service

للتحقق:
- اذهب إلى Railway Dashboard
- اضغط على Settings → Restart Service
""")

input("\nاضغط Enter للخروج...")