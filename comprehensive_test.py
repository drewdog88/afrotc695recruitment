#!/usr/bin/env python3
"""
AFROTC 695 Recruitment System - Comprehensive Testing Script
This script systematically tests every feature, link, and functionality of the system.
"""

import requests
import time
import json
from datetime import datetime

class ComprehensiveTester:
    def __init__(self):
        self.local_base = "http://localhost:5000"
        self.prod_base = "https://afrotc695recruitment.vercel.app"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "local_results": {},
            "production_results": {},
            "issues": []
        }
        
    def log_issue(self, environment, test_name, issue, details=""):
        """Log an issue found during testing"""
        issue_record = {
            "environment": environment,
            "test": test_name,
            "issue": issue,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results["issues"].append(issue_record)
        print(f"❌ {environment.upper()} - {test_name}: {issue}")
        
    def log_success(self, environment, test_name):
        """Log a successful test"""
        print(f"✅ {environment.upper()} - {test_name}: PASSED")
        
    def test_endpoint(self, environment, endpoint, expected_status=200, check_content=None, allow_redirects=True):
        """Test a single endpoint"""
        base_url = self.local_base if environment == "local" else self.prod_base
        url = f"{base_url}{endpoint}"
        
        try:
            if environment == "production":
                response = requests.get(url, timeout=10, allow_redirects=allow_redirects)
            else:
                response = requests.get(url, allow_redirects=allow_redirects)
                
            if response.status_code != expected_status:
                # Special handling for authentication redirects
                if expected_status == 302 and response.status_code == 200:
                    # This means the redirect was followed and we got the login page
                    if 'login' in response.text.lower() or 'username' in response.text.lower():
                        self.log_success(environment, f"GET {endpoint} (redirected to login)")
                        return True
                    else:
                        self.log_issue(environment, f"GET {endpoint}", 
                                     f"Expected 302 redirect, got 200 but not login page")
                        return False
                elif expected_status == 302 and response.status_code == 302:
                    # This is a proper redirect (not followed)
                    if 'Location' in response.headers and 'login' in response.headers['Location']:
                        self.log_success(environment, f"GET {endpoint} (302 redirect to login)")
                        return True
                    else:
                        self.log_issue(environment, f"GET {endpoint}", 
                                     f"Expected 302 redirect to login, got 302 to {response.headers.get('Location', 'unknown')}")
                        return False
                else:
                    self.log_issue(environment, f"GET {endpoint}", 
                                 f"Expected status {expected_status}, got {response.status_code}")
                    return False
                
            if check_content and check_content not in response.text:
                self.log_issue(environment, f"GET {endpoint}", 
                             f"Expected content '{check_content}' not found")
                return False
                
            self.log_success(environment, f"GET {endpoint}")
            return True
            
        except Exception as e:
            self.log_issue(environment, f"GET {endpoint}", f"Request failed: {str(e)}")
            return False
    
    def test_phase_1_authentication(self):
        """Phase 1: Authentication & Basic Navigation"""
        print("\n" + "="*60)
        print("PHASE 1: AUTHENTICATION & BASIC NAVIGATION TESTING")
        print("="*60)
        
        # Test login page access
        print("\n1.1 LOGIN PAGE ACCESS")
        self.test_endpoint("local", "/login", 200, "username")
        self.test_endpoint("production", "/login", 200, "username")
        
        # Test homepage redirect
        print("\n1.2 HOMEPAGE REDIRECT")
        self.test_endpoint("local", "/", 302)  # Should redirect to login
        self.test_endpoint("production", "/", 302)  # Should redirect to login
        
        # Test forgot password
        print("\n1.3 FORGOT PASSWORD")
        self.test_endpoint("local", "/forgot-password", 200)
        self.test_endpoint("production", "/forgot-password", 200)
        
    def test_phase_2_protected_pages(self):
        """Phase 2: Protected Pages (should redirect to login when not authenticated)"""
        print("\n" + "="*60)
        print("PHASE 2: PROTECTED PAGES (UNAUTHENTICATED)")
        print("="*60)
        
        protected_pages = [
            "/dashboard",
            "/recruits", 
            "/contacts",
            "/calendar",
            "/materials",
            "/profile",
            "/admin",
            "/admin/users",
            "/admin/database",
            "/admin/activity-log",
            "/admin/system-statistics",
            "/admin/code-coverage",
            "/admin/quality-analysis",
            "/admin/vulnerability-scan"
        ]
        
        for page in protected_pages:
            print(f"\nTesting {page}")
            self.test_endpoint("local", page, 302)  # Should redirect to login
            self.test_endpoint("production", page, 302)  # Should redirect to login
            
    def test_phase_3_forms_and_add_pages(self):
        """Phase 3: Add/Edit Forms (should redirect to login when not authenticated)"""
        print("\n" + "="*60)
        print("PHASE 3: FORMS & ADD PAGES (UNAUTHENTICATED)")
        print("="*60)
        
        form_pages = [
            "/recruits/add",
            "/recruits/edit/1",
            "/cadet/add", 
            "/cadet/edit/1",
            "/contacts/add",
            "/contacts/edit/1",
            "/calendar/add",
            "/materials/add-link",
            "/materials/add-document",
            "/admin/users/add",
            "/admin/users/edit/1",
            "/change-password"
        ]
        
        for page in form_pages:
            print(f"\nTesting {page}")
            self.test_endpoint("local", page, 302)  # Should redirect to login
            self.test_endpoint("production", page, 302)  # Should redirect to login
            
    def test_phase_4_export_endpoints(self):
        """Phase 4: Export Endpoints (should redirect to login when not authenticated)"""
        print("\n" + "="*60)
        print("PHASE 4: EXPORT ENDPOINTS (UNAUTHENTICATED)")
        print("="*60)
        
        export_endpoints = [
            "/download/recruits/csv",
            "/download/recruits/excel", 
            "/download/recruits/pdf",
            "/download/cadet/csv",
            "/download/cadet/excel",
            "/download/cadet/pdf", 
            "/download/contacts/csv",
            "/download/contacts/excel",
            "/download/contacts/pdf",
            "/download/activity-log/csv",
            "/download/activity-log/excel",
            "/download/activity-log/pdf"
        ]
        
        for endpoint in export_endpoints:
            print(f"\nTesting {endpoint}")
            self.test_endpoint("local", endpoint, 302)  # Should redirect to login
            self.test_endpoint("production", endpoint, 302)  # Should redirect to login
            
    def test_phase_5_api_endpoints(self):
        """Phase 5: API Endpoints"""
        print("\n" + "="*60)
        print("PHASE 5: API ENDPOINTS")
        print("="*60)
        
        api_endpoints = [
            "/api/recruits",
            "/api/cadet"
        ]
        
        for endpoint in api_endpoints:
            print(f"\nTesting {endpoint}")
            self.test_endpoint("local", endpoint, 401)  # Should return 401 for JSON API
            self.test_endpoint("production", endpoint, 401)  # Should return 401 for JSON API
            
    def test_phase_6_error_pages(self):
        """Phase 6: Error Pages"""
        print("\n" + "="*60)
        print("PHASE 6: ERROR PAGES")
        print("="*60)
        
        # Test 404 page
        print("\nTesting 404 page")
        self.test_endpoint("local", "/nonexistent-page", 404)
        self.test_endpoint("production", "/nonexistent-page", 404)
        
    def test_phase_7_static_files(self):
        """Phase 7: Static Files"""
        print("\n" + "="*60)
        print("PHASE 7: STATIC FILES")
        print("="*60)
        
        static_files = [
            "/static/detachment695.jpg",
            "/static/js/analytics.js"
        ]
        
        for file in static_files:
            print(f"\nTesting {file}")
            self.test_endpoint("local", file, 200)
            self.test_endpoint("production", file, 200)
            
    def test_phase_8_performance(self):
        """Phase 8: Performance Testing"""
        print("\n" + "="*60)
        print("PHASE 8: PERFORMANCE TESTING")
        print("="*60)
        
        # Test response times
        endpoints_to_test = ["/login", "/forgot-password"]
        
        for endpoint in endpoints_to_test:
            print(f"\nTesting response time for {endpoint}")
            
            # Local
            start_time = time.time()
            try:
                response = requests.get(f"{self.local_base}{endpoint}")
                local_time = time.time() - start_time
                if local_time > 3.0:
                    self.log_issue("local", f"Performance {endpoint}", 
                                 f"Response time {local_time:.2f}s exceeds 3s threshold")
                else:
                    print(f"✅ LOCAL - {endpoint}: {local_time:.2f}s")
            except Exception as e:
                self.log_issue("local", f"Performance {endpoint}", f"Request failed: {str(e)}")
                
            # Production
            start_time = time.time()
            try:
                response = requests.get(f"{self.prod_base}{endpoint}", timeout=10)
                prod_time = time.time() - start_time
                if prod_time > 5.0:
                    self.log_issue("production", f"Performance {endpoint}", 
                                 f"Response time {prod_time:.2f}s exceeds 5s threshold")
                else:
                    print(f"✅ PRODUCTION - {endpoint}: {prod_time:.2f}s")
            except Exception as e:
                self.log_issue("production", f"Performance {endpoint}", f"Request failed: {str(e)}")
                
    def run_all_tests(self):
        """Run all testing phases"""
        print("🚀 STARTING COMPREHENSIVE TESTING")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        try:
            self.test_phase_1_authentication()
            self.test_phase_2_protected_pages()
            self.test_phase_3_forms_and_add_pages()
            self.test_phase_4_export_endpoints()
            self.test_phase_5_api_endpoints()
            self.test_phase_6_error_pages()
            self.test_phase_7_static_files()
            self.test_phase_8_performance()
            
        except KeyboardInterrupt:
            print("\n⚠️ Testing interrupted by user")
        except Exception as e:
            print(f"\n❌ Testing failed with error: {str(e)}")
            
        self.generate_report()
        
    def generate_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE TESTING REPORT")
        print("="*60)
        
        total_issues = len(self.results["issues"])
        
        print(f"\n📊 SUMMARY:")
        print(f"Total Issues Found: {total_issues}")
        print(f"Testing Completed: {datetime.now().isoformat()}")
        
        if total_issues > 0:
            print(f"\n🚨 ISSUES FOUND:")
            for i, issue in enumerate(self.results["issues"], 1):
                print(f"{i}. {issue['environment'].upper()} - {issue['test']}: {issue['issue']}")
                if issue['details']:
                    print(f"   Details: {issue['details']}")
        else:
            print("\n🎉 NO ISSUES FOUND - ALL TESTS PASSED!")
            
        # Save detailed report
        report_file = f"comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return total_issues == 0

if __name__ == "__main__":
    tester = ComprehensiveTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
