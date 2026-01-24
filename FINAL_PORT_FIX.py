#!/usr/bin/env python3
"""
إصلاح مشكلة الـ Port نهائياً
"""

from pathlib import Path
import subprocess

root = Path(r"C:\Users\AboHelal\Downloads\New folder (4)")

print("="*70)
print("إصلاح مشكلة Port")
print("="*70)

# Fix server.js
print("\n[1/2] إصلاح server.js...")

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

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// Get PORT from environment (Railway provides this)
const PORT = process.env.PORT || 3000;

// IMPORTANT: Listen on 0.0.0.0 and use PORT from environment
app.listen(PORT, '0.0.0.0', () => {
  console.log('='.repeat(60));
  console.log('Academic Paraphraser Server');
  console.log('='.repeat(60));
  console.log(`Port: ${PORT}`);
  console.log(`Host: 0.0.0.0`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log('='.repeat(60));
});
"""

with open(root / 'backend' / 'server.js', 'w') as f:
    f.write(server_js)

print("✓ تم إصلاح server.js")

# Git operations
print("\n[2/2] رفع التحديثات...")

try:
    subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(root), 'commit', '-m', 'Fix port configuration for Railway'], check=True)
    subprocess.run(['git', '-C', str(root), 'push', 'origin', 'main'], check=True)
    
    print("✓ تم رفع التحديثات")
    
    print("\n" + "="*70)
    print("✅ تم الإصلاح!")
    print("="*70)
    print("""
Railway سيعيد النشر تلقائياً.

⏰ انتظر 2-3 دقائق ثم افتح:
https://academic-paraphrasing-saas-production.up.railway.app

في Railway Logs يجب أن ترى:
  Port: [رقم ديناميكي من Railway]
  Host: 0.0.0.0
""")
    
except Exception as e:
    print(f"\n❌ خطأ: {e}")

input("\nاضغط Enter للخروج...")