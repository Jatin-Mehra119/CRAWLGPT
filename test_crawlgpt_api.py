#!/usr/bin/env python3
# filepath: test_crawlgpt_api.py
import requests
import time
import json
import random
import string
import argparse
import sys
from pprint import pprint

class CrawlGPTTester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.username = None
        self.test_data = {}

    def generate_random_string(self, length=8):
        """Generate a random string for test data"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def print_response(self, response, label):
        """Pretty print API responses"""
        print(f"\n{'=' * 80}")
        print(f"✅ {label} - Status Code: {response.status_code}")
        print(f"{'=' * 80}")
        try:
            pprint(response.json())
        except:
            print(response.text)
        print(f"{'=' * 80}\n")
        sys.stdout.flush()

    def print_error(self, response, label):
        """Pretty print API error responses"""
        print(f"\n{'=' * 80}")
        print(f"❌ {label} - Status Code: {response.status_code}")
        print(f"{'=' * 80}")
        try:
            pprint(response.json())
        except:
            print(response.text)
        print(f"{'=' * 80}\n")
        sys.stdout.flush()

    def test_welcome(self):
        """Test welcome endpoint"""
        response = requests.get(f"{self.base_url}/")
        if response.status_code == 200:
            self.print_response(response, "Welcome Endpoint")
            return True
        else:
            self.print_error(response, "Welcome Endpoint")
            return False

    def test_register(self):
        """Test user registration"""
        self.username = f"testuser_{self.generate_random_string()}"
        password = "Test123!"
        email = f"{self.username}@test.com"
        
        data = {
            "username": self.username,
            "password": password,
            "email": email
        }
        
        response = requests.post(f"{self.base_url}/api/register", json=data)
        if response.status_code == 200:
            self.print_response(response, "User Registration")
            self.test_data["registration"] = data
            return True
        else:
            self.print_error(response, "User Registration")
            return False

    def test_login(self):
        """Test user login"""
        if not self.username:
            print("Error: No user registered to log in with")
            return False
            
        data = {
            "username": self.username,
            "password": self.test_data["registration"]["password"]
        }
        
        response = requests.post(f"{self.base_url}/api/login", json=data)
        if response.status_code == 200:
            self.print_response(response, "User Login")
            response_data = response.json()
            self.token = response_data.get("token")
            self.user_id = response_data.get("user", {}).get("id")
            if not self.token:
                print("Error: No token received from login")
                return False
            return True
        else:
            self.print_error(response, "User Login")
            return False

    def test_process_url(self, url="https://www.teachermagazine.com/in_en/articles/research-news-disability-inclusion-in-classroom-assessments"):
        """Test URL processing"""
        if not self.token:
            print("Error: Not logged in")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"url": url}
        
        print(f"Processing URL: {url}")
        response = requests.post(f"{self.base_url}/api/process-url", headers=headers, json=data)
        
        if response.status_code == 200:
            self.print_response(response, "Process URL")
            return True
        else:
            self.print_error(response, "Process URL")
            return False

    def test_chat(self, message="What is the main topic of this page?"):
        """Test chat endpoint"""
        if not self.token:
            print("Error: Not logged in")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "message": message,
            "temperature": 0.7,
            "max_tokens": 1000,
            "model_id": "llama-3.1-8b-instant",
            "use_summary": False
        }
        
        print(f"Sending chat message: {message}")
        response = requests.post(f"{self.base_url}/api/chat", headers=headers, json=data)
        
        if response.status_code == 200:
            self.print_response(response, "Chat")
            return True
        else:
            self.print_error(response, "Chat")
            return False

    def test_get_history(self):
        """Test getting chat history"""
        if not self.token:
            print("Error: Not logged in")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/api/chat/history", headers=headers)
        
        if response.status_code == 200:
            self.print_response(response, "Get History")
            return True
        else:
            self.print_error(response, "Get History")
            return False

    def test_export_data(self):
        """Test data export"""
        if not self.token:
            print("Error: Not logged in")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/api/export", headers=headers)
        
        if response.status_code == 200:
            self.print_response(response, "Export Data")
            self.test_data["export"] = response.json().get("data")
            return True
        else:
            self.print_error(response, "Export Data")
            return False

    def test_clear_history(self):
        """Test clearing chat history"""
        if not self.token:
            print("Error: Not logged in")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{self.base_url}/api/chat/clear", headers=headers)
        
        if response.status_code == 200:
            self.print_response(response, "Clear History")
            return True
        else:
            self.print_error(response, "Clear History")
            return False

    def test_import_data(self):
        """Test data import"""
        if not self.token or "export" not in self.test_data:
            print("Error: No exported data to import")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"data": self.test_data["export"]}
        
        response = requests.post(f"{self.base_url}/api/import", headers=headers, json=data)
        
        if response.status_code == 200:
            self.print_response(response, "Import Data")
            return True
        else:
            self.print_error(response, "Import Data")
            return False

    def test_metrics(self):
        """Test getting metrics"""
        if not self.token:
            print("Error: Not logged in")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/api/metrics", headers=headers)
        
        if response.status_code == 200:
            self.print_response(response, "Get Metrics")
            return True
        else:
            self.print_error(response, "Get Metrics")
            return False

    def test_update_settings(self):
        """Test updating settings"""
        if not self.token:
            print("Error: Not logged in")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"use_summary": True}
        
        response = requests.post(f"{self.base_url}/api/settings", headers=headers, json=data)
        
        if response.status_code == 200:
            self.print_response(response, "Update Settings")
            return True
        else:
            self.print_error(response, "Update Settings")
            return False
            
    def test_clear_all(self):
        """Test clearing all data"""
        if not self.token:
            print("Error: Not logged in")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{self.base_url}/api/clear-all", headers=headers)
        
        if response.status_code == 200:
            self.print_response(response, "Clear All Data")
            return True
        else:
            self.print_error(response, "Clear All Data")
            return False

    def test_error_cases(self):
        """Test various error cases"""
        results = []
        
        # Test invalid URL
        if not self.token:
            print("Error: Not logged in")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        print("\nTesting error cases...")
        
        # Invalid URL
        data = {"url": "not-a-valid-url"}
        response = requests.post(f"{self.base_url}/api/process-url", headers=headers, json=data)
        self.print_response(response, "Invalid URL Test")
        results.append(response.status_code == 400)
        
        # Chat without processing URL
        await_clear = requests.post(f"{self.base_url}/api/clear-all", headers=headers)
        data = {"message": "This should fail"}
        response = requests.post(f"{self.base_url}/api/chat", headers=headers, json=data)
        self.print_response(response, "Chat Without URL Test")
        results.append(response.status_code == 400)
        
        # Invalid token
        bad_headers = {"Authorization": "Bearer invalid-token"}
        response = requests.get(f"{self.base_url}/api/chat/history", headers=bad_headers)
        self.print_response(response, "Invalid Token Test")
        results.append(response.status_code == 401)
        
        return all(results)

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("Starting CRAWLGPT API Tests...")
        
        tests = [
            ("Welcome Endpoint", self.test_welcome),
            ("User Registration", self.test_register),
            ("User Login", self.test_login),
            ("Process URL", self.test_process_url),
            ("Chat", self.test_chat),
            ("Get History", self.test_get_history),
            ("Export Data", self.test_export_data),
            ("Clear History", self.test_clear_history),
            ("Import Data", self.test_import_data),
            ("Get Metrics", self.test_metrics),
            ("Update Settings", self.test_update_settings),
            ("Error Cases", self.test_error_cases),
            ("Clear All Data", self.test_clear_all)
        ]
        
        results = {}
        
        for name, test_func in tests:
            print(f"\n{'=' * 80}")
            print(f"Running test: {name}")
            print(f"{'=' * 80}")
            
            try:
                success = test_func()
                results[name] = success
                if not success:
                    print(f"❌ Test '{name}' failed.")
                    time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test '{name}' threw an exception: {str(e)}")
                results[name] = False
                
            time.sleep(1)  # Brief pause between tests
        
        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        for name, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{status} - {name}")
        print("=" * 80)
        
        success_rate = sum(1 for success in results.values() if success) / len(results) * 100
        print(f"Overall success rate: {success_rate:.2f}%")
        
        return all(results.values())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the CRAWLGPT API")
    parser.add_argument("--url", default="http://127.0.0.1:5000", help="Base URL for the API")
    args = parser.parse_args()
    
    tester = CrawlGPTTester(base_url=args.url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)