import requests
import sys

def test_pdf_report():
    """Test PDF report generation"""
    base_url = "https://mdf-feasibility-pro.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔍 Testing PDF Report Generation...")
    
    # First create a project with complete data
    project_data = {
        "project_name": "مشروع اختبار التقرير"
    }
    
    try:
        # Create project
        response = requests.post(f"{api_url}/projects", json=project_data)
        if response.status_code != 200:
            print(f"❌ Failed to create project: {response.status_code}")
            return False
            
        project = response.json()
        project_id = project['id']
        print(f"✅ Created test project: {project_id}")
        
        # Add complete data
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
        
        # Update project with complete data
        response = requests.put(f"{api_url}/projects/{project_id}", json=complete_data)
        if response.status_code != 200:
            print(f"❌ Failed to update project: {response.status_code}")
            return False
        print("✅ Updated project with complete data")
        
        # Test PDF report generation
        response = requests.get(f"{api_url}/projects/{project_id}/report")
        if response.status_code == 200:
            print("✅ PDF report generated successfully")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            
            # Save the PDF for verification
            with open('/app/test_report.pdf', 'wb') as f:
                f.write(response.content)
            print("✅ PDF saved as test_report.pdf")
            
        else:
            print(f"❌ Failed to generate PDF report: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
        
        # Clean up - delete the test project
        requests.delete(f"{api_url}/projects/{project_id}")
        print("✅ Cleaned up test project")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during PDF test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_pdf_report()
    sys.exit(0 if success else 1)