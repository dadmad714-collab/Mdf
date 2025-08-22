from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from fastapi.responses import StreamingResponse
import json
import io

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models for MDF Feasibility Study

class FinancialData(BaseModel):
    # Initial Investment Costs
    land_cost: float = 0
    building_construction: float = 0
    machinery_equipment: float = 0
    installation_cost: float = 0
    pre_operational_expenses: float = 0
    working_capital: float = 0
    
    # Raw Material Costs (per unit)
    palm_fronds_cost_per_ton: float = 0
    adhesive_cost: float = 0
    chemicals_cost: float = 0
    energy_cost_per_unit: float = 0
    
    # Operational Costs (monthly)
    labor_cost_monthly: float = 0
    maintenance_cost_monthly: float = 0
    utilities_cost_monthly: float = 0
    administrative_cost_monthly: float = 0
    
    # Revenue Data
    mdf_price_per_cubic_meter: float = 0
    production_capacity_monthly: float = 0
    
    # Financial Parameters
    project_life_years: int = 10
    discount_rate: float = 10.0
    tax_rate: float = 15.0

class TechnicalData(BaseModel):
    # Production Specifications
    daily_production_capacity: float = 0
    working_days_per_month: int = 26
    palm_fronds_requirement_per_cubic_meter: float = 0
    
    # Machinery Information
    machinery_list: List[Dict[str, Any]] = []
    production_process_steps: List[str] = []
    quality_standards: List[str] = []
    
    # Technical Requirements
    factory_area_required: float = 0
    electricity_requirement_kw: float = 0
    water_requirement_daily: float = 0
    labor_requirement: int = 0

class MarketData(BaseModel):
    # Market Analysis
    target_market_size: float = 0
    market_growth_rate: float = 0
    competitor_analysis: List[Dict[str, Any]] = []
    
    # Market Positioning
    market_share_target: float = 0
    pricing_strategy: str = ""
    distribution_channels: List[str] = []
    
    # Market Risks
    demand_seasonality: str = ""
    competition_level: str = "متوسط"
    market_barriers: List[str] = []

class FeasibilityProject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    financial_data: Optional[FinancialData] = None
    technical_data: Optional[TechnicalData] = None
    market_data: Optional[MarketData] = None
    
    # Calculated Results
    financial_results: Optional[Dict[str, Any]] = None
    is_completed: bool = False

class ProjectCreate(BaseModel):
    project_name: str

class ProjectUpdate(BaseModel):
    financial_data: Optional[FinancialData] = None
    technical_data: Optional[TechnicalData] = None
    market_data: Optional[MarketData] = None

# Financial Calculation Functions
def calculate_total_investment(financial_data: FinancialData) -> float:
    return (financial_data.land_cost + 
            financial_data.building_construction + 
            financial_data.machinery_equipment + 
            financial_data.installation_cost + 
            financial_data.pre_operational_expenses + 
            financial_data.working_capital)

def calculate_annual_costs(financial_data: FinancialData) -> float:
    monthly_costs = (financial_data.labor_cost_monthly + 
                    financial_data.maintenance_cost_monthly + 
                    financial_data.utilities_cost_monthly + 
                    financial_data.administrative_cost_monthly)
    
    # Raw material costs
    annual_production = financial_data.production_capacity_monthly * 12
    raw_material_cost = annual_production * financial_data.palm_fronds_cost_per_ton
    
    return (monthly_costs * 12) + raw_material_cost

def calculate_annual_revenue(financial_data: FinancialData) -> float:
    annual_production = financial_data.production_capacity_monthly * 12
    return annual_production * financial_data.mdf_price_per_cubic_meter

def calculate_npv(financial_data: FinancialData) -> float:
    total_investment = calculate_total_investment(financial_data)
    annual_revenue = calculate_annual_revenue(financial_data)
    annual_costs = calculate_annual_costs(financial_data)
    annual_net_cash_flow = annual_revenue - annual_costs
    
    # Calculate NPV
    npv = -total_investment
    for year in range(1, financial_data.project_life_years + 1):
        discount_factor = (1 + financial_data.discount_rate / 100) ** year
        npv += annual_net_cash_flow / discount_factor
    
    return npv

def calculate_irr(financial_data: FinancialData) -> float:
    # Simplified IRR calculation
    total_investment = calculate_total_investment(financial_data)
    annual_revenue = calculate_annual_revenue(financial_data)
    annual_costs = calculate_annual_costs(financial_data)
    annual_net_cash_flow = annual_revenue - annual_costs
    
    if annual_net_cash_flow <= 0 or total_investment <= 0:
        return 0
    
    # Approximate IRR using trial and error method
    for rate in range(1, 100):
        npv_test = -total_investment
        for year in range(1, financial_data.project_life_years + 1):
            discount_factor = (1 + rate / 100) ** year
            npv_test += annual_net_cash_flow / discount_factor
        
        if npv_test <= 0:
            return rate - 1
    
    return 99

def calculate_payback_period(financial_data: FinancialData) -> float:
    total_investment = calculate_total_investment(financial_data)
    annual_revenue = calculate_annual_revenue(financial_data)
    annual_costs = calculate_annual_costs(financial_data)
    annual_net_cash_flow = annual_revenue - annual_costs
    
    if annual_net_cash_flow <= 0:
        return float('inf')
    
    return total_investment / annual_net_cash_flow

def calculate_financial_results(financial_data: FinancialData) -> Dict[str, Any]:
    total_investment = calculate_total_investment(financial_data)
    annual_revenue = calculate_annual_revenue(financial_data)
    annual_costs = calculate_annual_costs(financial_data)
    annual_profit = annual_revenue - annual_costs
    
    npv = calculate_npv(financial_data)
    irr = calculate_irr(financial_data)
    payback_period = calculate_payback_period(financial_data)
    
    roi = (annual_profit / total_investment) * 100 if total_investment > 0 else 0
    
    return {
        "total_investment": total_investment,
        "annual_revenue": annual_revenue,
        "annual_costs": annual_costs,
        "annual_profit": annual_profit,
        "npv": npv,
        "irr": irr,
        "payback_period": payback_period,
        "roi": roi,
        "is_feasible": npv > 0 and irr > financial_data.discount_rate
    }

# API Routes
@api_router.get("/")
async def root():
    return {"message": "نظام دراسة الجدوى لمصنع ألواح MDF من سعف النخيل"}

@api_router.post("/projects", response_model=FeasibilityProject)
async def create_project(project_data: ProjectCreate):
    project = FeasibilityProject(project_name=project_data.project_name)
    project_dict = project.dict()
    project_dict['created_at'] = project_dict['created_at'].isoformat()
    project_dict['updated_at'] = project_dict['updated_at'].isoformat()
    
    await db.feasibility_projects.insert_one(project_dict)
    return project

@api_router.get("/projects", response_model=List[FeasibilityProject])
async def get_projects():
    projects = await db.feasibility_projects.find().to_list(1000)
    
    for project in projects:
        if isinstance(project.get('created_at'), str):
            project['created_at'] = datetime.fromisoformat(project['created_at'])
        if isinstance(project.get('updated_at'), str):
            project['updated_at'] = datetime.fromisoformat(project['updated_at'])
    
    return [FeasibilityProject(**project) for project in projects]

@api_router.get("/projects/{project_id}", response_model=FeasibilityProject)
async def get_project(project_id: str):
    project = await db.feasibility_projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="المشروع غير موجود")
    
    if isinstance(project.get('created_at'), str):
        project['created_at'] = datetime.fromisoformat(project['created_at'])
    if isinstance(project.get('updated_at'), str):
        project['updated_at'] = datetime.fromisoformat(project['updated_at'])
    
    return FeasibilityProject(**project)

@api_router.put("/projects/{project_id}", response_model=FeasibilityProject)
async def update_project(project_id: str, update_data: ProjectUpdate):
    project = await db.feasibility_projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="المشروع غير موجود")
    
    update_dict = {}
    if update_data.financial_data:
        update_dict['financial_data'] = update_data.financial_data.dict()
        # Calculate financial results
        financial_results = calculate_financial_results(update_data.financial_data)
        update_dict['financial_results'] = financial_results
    
    if update_data.technical_data:
        update_dict['technical_data'] = update_data.technical_data.dict()
    
    if update_data.market_data:
        update_dict['market_data'] = update_data.market_data.dict()
    
    # Check if project is completed (has all three data types)
    if update_data.financial_data and update_data.technical_data and update_data.market_data:
        update_dict['is_completed'] = True
    
    update_dict['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.feasibility_projects.update_one(
        {"id": project_id}, 
        {"$set": update_dict}
    )
    
    # Fetch updated project
    updated_project = await db.feasibility_projects.find_one({"id": project_id})
    
    if isinstance(updated_project.get('created_at'), str):
        updated_project['created_at'] = datetime.fromisoformat(updated_project['created_at'])
    if isinstance(updated_project.get('updated_at'), str):
        updated_project['updated_at'] = datetime.fromisoformat(updated_project['updated_at'])
    
    return FeasibilityProject(**updated_project)

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    result = await db.feasibility_projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="المشروع غير موجود")
    return {"message": "تم حذف المشروع بنجاح"}

@api_router.get("/projects/{project_id}/financial-results")
async def get_financial_results(project_id: str):
    project = await db.feasibility_projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="المشروع غير موجود")
    
    if not project.get('financial_data'):
        raise HTTPException(status_code=400, detail="البيانات المالية غير مكتملة")
    
    financial_data = FinancialData(**project['financial_data'])
    results = calculate_financial_results(financial_data)
    
    return results

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()