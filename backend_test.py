import requests
import sys
import json
from datetime import datetime

class MDFFeasibilityTester:
    def __init__(self, base_url="https://mdf-feasibility-pro.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.project_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    return True, response_data
                except:
                    print(f"   Response: {response.text[:200]}...")
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_create_project(self):
        """Test creating a new project"""
        project_data = {
            "project_name": f"مصنع MDF اختبار - {datetime.now().strftime('%H:%M:%S')}"
        }
        
        success, response = self.run_test(
            "Create New Project",
            "POST",
            "projects",
            200,
            data=project_data
        )
        
        if success and 'id' in response:
            self.project_id = response['id']
            print(f"   Created project ID: {self.project_id}")
        
        return success

    def test_get_projects(self):
        """Test getting all projects"""
        success, response = self.run_test(
            "Get All Projects",
            "GET",
            "projects",
            200
        )
        return success

    def test_get_project_by_id(self):
        """Test getting a specific project"""
        if not self.project_id:
            print("❌ No project ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get Project by ID",
            "GET",
            f"projects/{self.project_id}",
            200
        )
        return success

    def test_update_financial_data(self):
        """Test updating project with financial data"""
        if not self.project_id:
            print("❌ No project ID available for testing")
            return False

        # Sample financial data as specified in the request
        financial_data = {
            "land_cost": 500000,
            "building_construction": 2000000,
            "machinery_equipment": 3000000,
            "installation_cost": 200000,
            "pre_operational_expenses": 100000,
            "working_capital": 300000,
            "palm_fronds_cost_per_ton": 150,
            "adhesive_cost": 50000,
            "chemicals_cost": 30000,
            "energy_cost_per_unit": 0.5,
            "labor_cost_monthly": 50000,
            "maintenance_cost_monthly": 15000,
            "utilities_cost_monthly": 20000,
            "administrative_cost_monthly": 10000,
            "mdf_price_per_cubic_meter": 800,
            "production_capacity_monthly": 1000,
            "project_life_years": 10,
            "discount_rate": 10.0,
            "tax_rate": 15.0
        }

        update_data = {
            "financial_data": financial_data
        }

        success, response = self.run_test(
            "Update Financial Data",
            "PUT",
            f"projects/{self.project_id}",
            200,
            data=update_data
        )
        return success

    def test_update_technical_data(self):
        """Test updating project with technical data"""
        if not self.project_id:
            print("❌ No project ID available for testing")
            return False

        technical_data = {
            "daily_production_capacity": 40,
            "working_days_per_month": 26,
            "palm_fronds_requirement_per_cubic_meter": 1.2,
            "factory_area_required": 5000,
            "electricity_requirement_kw": 500,
            "water_requirement_daily": 10000,
            "labor_requirement": 25,
            "machinery_list": [
                {"name": "آلة التقطيع", "cost": 500000},
                {"name": "آلة الضغط", "cost": 800000}
            ],
            "production_process_steps": [
                "تجميع سعف النخيل",
                "التقطيع والطحن",
                "الخلط مع المواد اللاصقة",
                "الضغط والتشكيل",
                "التجفيف",
                "التشطيب والتعبئة"
            ],
            "quality_standards": ["ISO 9001", "SASO"]
        }

        update_data = {
            "technical_data": technical_data
        }

        success, response = self.run_test(
            "Update Technical Data",
            "PUT",
            f"projects/{self.project_id}",
            200,
            data=update_data
        )
        return success

    def test_update_market_data(self):
        """Test updating project with market data"""
        if not self.project_id:
            print("❌ No project ID available for testing")
            return False

        market_data = {
            "target_market_size": 50000000,
            "market_growth_rate": 5.5,
            "market_share_target": 2.0,
            "pricing_strategy": "تسعير تنافسي مع التركيز على الجودة",
            "distribution_channels": ["موزعون محليون", "بيع مباشر", "متاجر إلكترونية"],
            "demand_seasonality": "مستقر على مدار السنة مع زيادة في فصل الشتاء",
            "competition_level": "متوسط",
            "market_barriers": ["رأس المال المطلوب", "الحصول على التراخيص"],
            "competitor_analysis": [
                {"name": "شركة الألواح المتقدمة", "market_share": 15, "strengths": "خبرة طويلة"},
                {"name": "مصنع الخشب الحديث", "market_share": 10, "strengths": "أسعار منافسة"}
            ]
        }

        update_data = {
            "market_data": market_data
        }

        success, response = self.run_test(
            "Update Market Data",
            "PUT",
            f"projects/{self.project_id}",
            200,
            data=update_data
        )
        return success

    def test_complete_project_update(self):
        """Test updating project with all data types at once"""
        if not self.project_id:
            print("❌ No project ID available for testing")
            return False

        # Complete data for all three categories
        complete_data = {
            "financial_data": {
                "land_cost": 500000,
                "building_construction": 2000000,
                "machinery_equipment": 3000000,
                "installation_cost": 200000,
                "pre_operational_expenses": 100000,
                "working_capital": 300000,
                "palm_fronds_cost_per_ton": 150,
                "adhesive_cost": 50000,
                "chemicals_cost": 30000,
                "energy_cost_per_unit": 0.5,
                "labor_cost_monthly": 50000,
                "maintenance_cost_monthly": 15000,
                "utilities_cost_monthly": 20000,
                "administrative_cost_monthly": 10000,
                "mdf_price_per_cubic_meter": 800,
                "production_capacity_monthly": 1000,
                "project_life_years": 10,
                "discount_rate": 10.0,
                "tax_rate": 15.0
            },
            "technical_data": {
                "daily_production_capacity": 40,
                "working_days_per_month": 26,
                "palm_fronds_requirement_per_cubic_meter": 1.2,
                "factory_area_required": 5000,
                "electricity_requirement_kw": 500,
                "water_requirement_daily": 10000,
                "labor_requirement": 25
            },
            "market_data": {
                "target_market_size": 50000000,
                "market_growth_rate": 5.5,
                "market_share_target": 2.0,
                "pricing_strategy": "تسعير تنافسي",
                "demand_seasonality": "مستقر",
                "competition_level": "متوسط"
            }
        }

        success, response = self.run_test(
            "Complete Project Update (All Data)",
            "PUT",
            f"projects/{self.project_id}",
            200,
            data=complete_data
        )
        return success

    def test_get_financial_results(self):
        """Test getting financial calculation results"""
        if not self.project_id:
            print("❌ No project ID available for testing")
            return False

        success, response = self.run_test(
            "Get Financial Results",
            "GET",
            f"projects/{self.project_id}/financial-results",
            200
        )

        if success and response:
            print("\n📊 Financial Calculation Results:")
            print(f"   Total Investment: {response.get('total_investment', 0):,.0f} ريال")
            print(f"   Annual Revenue: {response.get('annual_revenue', 0):,.0f} ريال")
            print(f"   Annual Costs: {response.get('annual_costs', 0):,.0f} ريال")
            print(f"   Annual Profit: {response.get('annual_profit', 0):,.0f} ريال")
            print(f"   NPV: {response.get('npv', 0):,.0f} ريال")
            print(f"   IRR: {response.get('irr', 0):.1f}%")
            print(f"   Payback Period: {response.get('payback_period', 0):.1f} years")
            print(f"   ROI: {response.get('roi', 0):.1f}%")
            print(f"   Is Feasible: {'Yes' if response.get('is_feasible', False) else 'No'}")

        return success

    def test_delete_project(self):
        """Test deleting a project"""
        if not self.project_id:
            print("❌ No project ID available for testing")
            return False

        success, response = self.run_test(
            "Delete Project",
            "DELETE",
            f"projects/{self.project_id}",
            200
        )
        return success

def main():
    print("🚀 Starting MDF Feasibility Study API Tests")
    print("=" * 60)
    
    tester = MDFFeasibilityTester()
    
    # Run all tests in sequence
    tests = [
        tester.test_root_endpoint,
        tester.test_create_project,
        tester.test_get_projects,
        tester.test_get_project_by_id,
        tester.test_update_financial_data,
        tester.test_update_technical_data,
        tester.test_update_market_data,
        tester.test_complete_project_update,
        tester.test_get_financial_results,
        tester.test_delete_project
    ]
    
    for test in tests:
        test()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the backend implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())