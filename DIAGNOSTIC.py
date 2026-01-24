#!/usr/bin/env python3
import urllib.request
import json
from pathlib import Path

class Diagnostics:
    def __init__(self):
        self.issues = []
        self.root = Path(__file__).parent
    
    def check_files(self):
        print("\n[CHECK] Checking files...")
        
        required = [
            "backend/server.js",
            "backend/package.json",
            "public/index.html",
            "Procfile"
        ]
        
        for filepath in required:
            path = self.root / filepath
            if path.exists():
                print("  OK " + filepath)
            else:
                print("  MISSING " + filepath)
                self.issues.append("Missing: " + filepath)
    
    def check_api(self):
        print("\n[CHECK] Testing API...")
        url = "https://academic-paraphrasing-saas-production.up.railway.app/api/health"
        
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                if data.get("status") == "ok":
                    print("  OK API is responding")
                    return True
                else:
                    print("  FAILED API unhealthy")
                    return False
        except Exception as e:
            print("  FAILED API error: " + str(e))
            return False
    
    def run(self):
        print("="*60)
        print("DIAGNOSTIC TOOL")
        print("="*60)
        
        self.check_files()
        self.check_api()
        
        print("\n" + "="*60)
        if self.issues:
            print("ISSUES FOUND:")
            for issue in self.issues:
                print("  " + issue)
        else:
            print("ALL CHECKS PASSED!")
            print("Site: https://academic-paraphrasing-saas-production.up.railway.app")
        print("="*60)

if __name__ == "__main__":
    diag = Diagnostics()
    diag.run()