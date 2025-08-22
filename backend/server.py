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
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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

def generate_pdf_report(project: dict) -> io.BytesIO:
    """Generate PDF report for the project"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.darkgreen
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    # Build content
    content = []
    
    # Title
    content.append(Paragraph("دراسة الجدوى الاقتصادية", title_style))
    content.append(Paragraph("مصنع ألواح MDF من سعف النخيل", title_style))
    content.append(Spacer(1, 20))
    
    # Project Info
    content.append(Paragraph("معلومات المشروع", heading_style))
    project_info = [
        ["اسم المشروع:", project.get('project_name', 'غير محدد')],
        ["تاريخ الإنشاء:", datetime.fromisoformat(project['created_at']).strftime('%Y-%m-%d') if isinstance(project.get('created_at'), str) else project.get('created_at', '').strftime('%Y-%m-%d')],
        ["حالة المشروع:", "مكتمل" if project.get('is_completed') else "قيد التنفيذ"]
    ]
    
    project_table = Table(project_info, colWidths=[4*cm, 8*cm])
    project_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(project_table)
    content.append(Spacer(1, 20))
    
    # Financial Results
    if project.get('financial_results'):
        results = project['financial_results']
        content.append(Paragraph("النتائج المالية", heading_style))
        
        financial_data = [
            ["إجمالي الاستثمار:", f"{results.get('total_investment', 0):,.0f} ريال"],
            ["الإيرادات السنوية:", f"{results.get('annual_revenue', 0):,.0f} ريال"],
            ["التكاليف السنوية:", f"{results.get('annual_costs', 0):,.0f} ريال"],
            ["الربح السنوي:", f"{results.get('annual_profit', 0):,.0f} ريال"],
            ["صافي القيمة الحالية (NPV):", f"{results.get('npv', 0):,.0f} ريال"],
            ["معدل العائد الداخلي (IRR):", f"{results.get('irr', 0):.1f}%"],
            ["فترة الاسترداد:", f"{results.get('payback_period', 0):.1f} سنة"],
            ["العائد على الاستثمار (ROI):", f"{results.get('roi', 0):.1f}%"],
            ["الجدوى الاقتصادية:", "مجدي اقتصادياً" if results.get('is_feasible') else "غير مجدي اقتصادياً"]
        ]
        
        financial_table = Table(financial_data, colWidths=[6*cm, 6*cm])
        financial_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.lightyellow),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(financial_table)
        content.append(Spacer(1, 20))
    
    # Technical Data
    if project.get('technical_data'):
        tech_data = project['technical_data']
        content.append(Paragraph("البيانات الفنية", heading_style))
        
        technical_info = [
            ["الطاقة الإنتاجية اليومية:", f"{tech_data.get('daily_production_capacity', 0)} متر مكعب"],
            ["أيام العمل الشهرية:", f"{tech_data.get('working_days_per_month', 0)} يوم"],
            ["المساحة المطلوبة:", f"{tech_data.get('factory_area_required', 0)} متر مربع"],
            ["الطاقة الكهربائية المطلوبة:", f"{tech_data.get('electricity_requirement_kw', 0)} كيلو واط"],
            ["عدد العمال المطلوب:", f"{tech_data.get('labor_requirement', 0)} عامل"]
        ]
        
        technical_table = Table(technical_info, colWidths=[6*cm, 6*cm])
        technical_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(technical_table)
        content.append(Spacer(1, 20))
    
    # Market Data
    if project.get('market_data'):
        market_data = project['market_data']
        content.append(Paragraph("بيانات السوق", heading_style))
        
        market_info = [
            ["حجم السوق المستهدف:", f"{market_data.get('target_market_size', 0):,.0f} ريال"],
            ["معدل نمو السوق:", f"{market_data.get('market_growth_rate', 0):.1f}%"],
            ["الحصة السوقية المستهدفة:", f"{market_data.get('market_share_target', 0):.1f}%"],
            ["استراتيجية التسعير:", market_data.get('pricing_strategy', 'غير محدد')],
            ["مستوى المنافسة:", market_data.get('competition_level', 'غير محدد')]
        ]
        
        market_table = Table(market_info, colWidths=[6*cm, 6*cm])
        market_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightcoral),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(market_table)
    
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    return buffer

@api_router.get("/projects/{project_id}/report")
async def generate_project_report(project_id: str):
    """Generate and download PDF report for the project"""
    project = await db.feasibility_projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="المشروع غير موجود")
    
    # Generate PDF
    try:
        pdf_buffer = generate_pdf_report(project)
        
        return StreamingResponse(
            io.BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=feasibility_report_{project_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"فشل في إنتاج التقرير: {str(e)}")

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