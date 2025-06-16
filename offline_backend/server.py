from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import statistics
from datetime import datetime, timedelta
import uuid
import json
from pathlib import Path
import os
import logging

# PDF generation imports
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER

# Import our SQLite database
from database import db

# Create FastAPI app
app = FastAPI(title="Offline Broiler Farm Management System")

# Create directories for exports
EXPORTS_DIR = Path("exports")
EXPORTS_DIR.mkdir(exist_ok=True)

# Pydantic Models (same as original)
class RemovalBatch(BaseModel):
    quantity: int
    total_weight_kg: float
    age_days: int

class FeedPhase(BaseModel):
    consumption_kg: float
    cost_per_kg: float

class BroilerCalculationInput(BaseModel):
    # Batch identification
    batch_id: str
    shed_number: str
    handler_name: str
    entry_date: Optional[str] = None
    exit_date: Optional[str] = None
    
    initial_chicks: int
    chick_cost_per_unit: float
    
    # Four feed phases
    pre_starter_feed: FeedPhase  # 0-10 days
    starter_feed: FeedPhase      # 10-24 days
    growth_feed: FeedPhase       # 24-35 days
    final_feed: FeedPhase        # 35+ days
    
    # Enhanced costs
    medicine_costs: float = 0
    miscellaneous_costs: float = 0
    cost_variations: float = 0
    sawdust_bedding_cost: float = 0
    chicken_bedding_sale_revenue: float = 0
    
    chicks_died: int
    removal_batches: List[RemovalBatch]

class CostBreakdown(BaseModel):
    chick_cost: float
    chick_cost_percent: float
    pre_starter_cost: float
    pre_starter_cost_percent: float
    starter_cost: float
    starter_cost_percent: float
    growth_cost: float
    growth_cost_percent: float
    final_cost: float
    final_cost_percent: float
    medicine_cost: float
    medicine_cost_percent: float
    miscellaneous_cost: float
    miscellaneous_cost_percent: float
    sawdust_bedding_cost: float
    sawdust_bedding_cost_percent: float
    cost_variations: float
    cost_variations_percent: float

class BroilerCalculation(BaseModel):
    id: str
    input_data: BroilerCalculationInput
    
    # Key metrics
    feed_conversion_ratio: float
    mortality_rate_percent: float
    weighted_average_age: float
    daily_weight_gain: float
    
    # Financial metrics
    total_cost: float
    total_revenue: float
    net_cost_per_kg: float
    
    # Production metrics
    total_weight_produced_kg: float
    total_feed_consumed_kg: float
    surviving_chicks: int
    removed_chicks: int
    missing_chicks: int
    viability: int  # Total chickens caught
    average_weight_per_chick: float
    
    # Analysis
    cost_breakdown: CostBreakdown
    
    created_at: datetime
    updated_at: Optional[datetime] = None

class CalculationResult(BaseModel):
    calculation: BroilerCalculation
    insights: List[str]

class BatchSummary(BaseModel):
    batch_id: str
    shed_number: str
    handler_name: str
    date: datetime
    initial_chicks: int
    fcr: float
    mortality_percent: float
    cost_per_kg: float

class HandlerPerformance(BaseModel):
    handler_name: str
    total_batches: int
    avg_feed_conversion_ratio: float
    avg_mortality_rate: float
    avg_daily_weight_gain: float
    avg_cost_per_kg: float
    total_chicks_processed: int
    performance_score: float

class Handler(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class HandlerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None

class HandlerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None

class Shed(BaseModel):
    id: str
    number: str
    capacity: Optional[int] = None
    location: Optional[str] = None
    status: str = "active"
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ShedCreate(BaseModel):
    number: str
    capacity: Optional[int] = None
    location: Optional[str] = None
    status: str = "active"
    notes: Optional[str] = None

class ShedUpdate(BaseModel):
    number: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

# Business Logic Functions (same as original)
def calculate_enhanced_broiler_metrics(input_data: BroilerCalculationInput) -> BroilerCalculation:
    """
    Calculate comprehensive broiler production metrics
    """
    # Parse dates if provided
    entry_date = None
    exit_date = None
    if input_data.entry_date:
        try:
            entry_date = datetime.fromisoformat(input_data.entry_date.replace('Z', '+00:00'))
        except:
            entry_date = datetime.now()
    if input_data.exit_date:
        try:
            exit_date = datetime.fromisoformat(input_data.exit_date.replace('Z', '+00:00'))
        except:
            exit_date = datetime.now()
    
    # Update input_data with parsed dates
    if entry_date:
        input_data.entry_date = entry_date
    if exit_date:
        input_data.exit_date = exit_date
    
    # Basic calculations
    surviving_chicks = input_data.initial_chicks - input_data.chicks_died
    removed_chicks = sum(batch.quantity for batch in input_data.removal_batches)
    missing_chicks = max(0, surviving_chicks - removed_chicks)
    viability = removed_chicks  # Total chickens successfully caught
    
    # Production metrics
    total_weight_produced_kg = sum(batch.total_weight_kg for batch in input_data.removal_batches)
    average_weight_per_chick = total_weight_produced_kg / removed_chicks if removed_chicks > 0 else 0
    
    # Feed calculations
    total_feed_consumed_kg = (
        input_data.pre_starter_feed.consumption_kg +
        input_data.starter_feed.consumption_kg +
        input_data.growth_feed.consumption_kg +
        input_data.final_feed.consumption_kg
    )
    
    # Feed Conversion Ratio (FCR)
    feed_conversion_ratio = total_feed_consumed_kg / total_weight_produced_kg if total_weight_produced_kg > 0 else 0
    
    # Mortality rate
    mortality_rate_percent = (input_data.chicks_died / input_data.initial_chicks) * 100
    
    # Weighted average age calculation
    total_age_weight = sum(batch.quantity * batch.age_days for batch in input_data.removal_batches)
    weighted_average_age = total_age_weight / removed_chicks if removed_chicks > 0 else 0
    
    # Daily weight gain
    daily_weight_gain = average_weight_per_chick / weighted_average_age if weighted_average_age > 0 else 0
    
    # Cost calculations
    chick_cost = input_data.initial_chicks * input_data.chick_cost_per_unit
    pre_starter_cost = input_data.pre_starter_feed.consumption_kg * input_data.pre_starter_feed.cost_per_kg
    starter_cost = input_data.starter_feed.consumption_kg * input_data.starter_feed.cost_per_kg
    growth_cost = input_data.growth_feed.consumption_kg * input_data.growth_feed.cost_per_kg
    final_cost = input_data.final_feed.consumption_kg * input_data.final_feed.cost_per_kg
    
    total_cost = (
        chick_cost + pre_starter_cost + starter_cost + growth_cost + final_cost +
        input_data.medicine_costs + input_data.miscellaneous_costs + 
        input_data.cost_variations + input_data.sawdust_bedding_cost
    )
    
    total_revenue = input_data.chicken_bedding_sale_revenue
    net_cost_per_kg = (total_cost - total_revenue) / total_weight_produced_kg if total_weight_produced_kg > 0 else 0
    
    # Cost breakdown with percentages
    cost_breakdown = CostBreakdown(
        chick_cost=chick_cost,
        chick_cost_percent=round((chick_cost / total_cost) * 100, 1) if total_cost > 0 else 0,
        pre_starter_cost=pre_starter_cost,
        pre_starter_cost_percent=round((pre_starter_cost / total_cost) * 100, 1) if total_cost > 0 else 0,
        starter_cost=starter_cost,
        starter_cost_percent=round((starter_cost / total_cost) * 100, 1) if total_cost > 0 else 0,
        growth_cost=growth_cost,
        growth_cost_percent=round((growth_cost / total_cost) * 100, 1) if total_cost > 0 else 0,
        final_cost=final_cost,
        final_cost_percent=round((final_cost / total_cost) * 100, 1) if total_cost > 0 else 0,
        medicine_cost=input_data.medicine_costs,
        medicine_cost_percent=round((input_data.medicine_costs / total_cost) * 100, 1) if total_cost > 0 else 0,
        miscellaneous_cost=input_data.miscellaneous_costs,
        miscellaneous_cost_percent=round((input_data.miscellaneous_costs / total_cost) * 100, 1) if total_cost > 0 else 0,
        sawdust_bedding_cost=input_data.sawdust_bedding_cost,
        sawdust_bedding_cost_percent=round((input_data.sawdust_bedding_cost / total_cost) * 100, 1) if total_cost > 0 else 0,
        cost_variations=input_data.cost_variations,
        cost_variations_percent=round((input_data.cost_variations / total_cost) * 100, 1) if total_cost > 0 else 0,
    )
    
    return BroilerCalculation(
        id=str(uuid.uuid4()),
        input_data=input_data,
        feed_conversion_ratio=round(feed_conversion_ratio, 2),
        mortality_rate_percent=round(mortality_rate_percent, 2),
        weighted_average_age=round(weighted_average_age, 1),
        daily_weight_gain=round(daily_weight_gain, 3),
        total_cost=round(total_cost, 2),
        total_revenue=round(total_revenue, 2),
        net_cost_per_kg=round(net_cost_per_kg, 3),
        total_weight_produced_kg=round(total_weight_produced_kg, 1),
        total_feed_consumed_kg=round(total_feed_consumed_kg, 1),
        surviving_chicks=surviving_chicks,
        removed_chicks=removed_chicks,
        missing_chicks=missing_chicks,
        viability=viability,
        average_weight_per_chick=round(average_weight_per_chick, 3),
        cost_breakdown=cost_breakdown,
        created_at=datetime.now(),
        updated_at=None
    )

def generate_enhanced_insights(calculation: BroilerCalculation) -> List[str]:
    """
    Generate enhanced business insights from calculation results
    """
    insights = []
    
    # Feed conversion analysis
    if calculation.feed_conversion_ratio <= 1.6:
        insights.append("🎯 Excellent FCR! Your feed efficiency is outstanding.")
    elif calculation.feed_conversion_ratio <= 1.8:
        insights.append("✅ Very good FCR. Feed management is effective.")
    elif calculation.feed_conversion_ratio <= 2.2:
        insights.append("⚠️ FCR is acceptable but could be improved with better feed management.")
    else:
        insights.append("🚨 High FCR indicates poor feed efficiency. Review feed quality and management.")
    
    # Mortality analysis
    if calculation.mortality_rate_percent <= 3:
        insights.append("🏆 Excellent mortality rate! Your flock management is superb.")
    elif calculation.mortality_rate_percent <= 7:
        insights.append("👍 Good mortality rate. Flock health management is effective.")
    elif calculation.mortality_rate_percent <= 12:
        insights.append("⚠️ Moderate mortality. Consider improving health protocols.")
    else:
        insights.append("🚨 High mortality rate. Urgent review of health management needed.")
    
    # Daily weight gain analysis
    if calculation.daily_weight_gain >= 0.065:
        insights.append("🚀 Excellent daily weight gain! Birds are growing optimally.")
    elif calculation.daily_weight_gain >= 0.055:
        insights.append("✅ Good daily weight gain. Growth performance is satisfactory.")
    elif calculation.daily_weight_gain >= 0.045:
        insights.append("⚠️ Moderate weight gain. Consider nutrition optimization.")
    else:
        insights.append("🚨 Low daily weight gain. Review nutrition and management practices.")
    
    # Cost efficiency analysis
    if calculation.net_cost_per_kg <= 1.5:
        insights.append("💰 Excellent cost efficiency! Very profitable operation.")
    elif calculation.net_cost_per_kg <= 2.0:
        insights.append("💚 Good cost management. Solid profit margins.")
    elif calculation.net_cost_per_kg <= 2.5:
        insights.append("⚠️ Moderate costs. Look for optimization opportunities.")
    else:
        insights.append("🚨 High production costs. Review all cost components.")
    
    # Missing chicks analysis
    if calculation.missing_chicks > 0:
        missing_percent = (calculation.missing_chicks / calculation.input_data.initial_chicks) * 100
        if missing_percent > 5:
            insights.append(f"⚠️ {calculation.missing_chicks} missing chicks ({missing_percent:.1f}%). Investigate potential issues.")
        else:
            insights.append(f"📊 {calculation.missing_chicks} missing chicks ({missing_percent:.1f}%) - within acceptable range.")
    
    # Age analysis
    if calculation.weighted_average_age < 35:
        insights.append("⏰ Early harvesting detected. Consider market timing optimization.")
    elif calculation.weighted_average_age > 50:
        insights.append("⏰ Extended growth period. Analyze cost-benefit of longer cycles.")
    
    return insights

async def calculate_handler_performance(handler_name: str) -> Optional[HandlerPerformance]:
    """
    Calculate performance metrics for a specific handler
    """
    calculations = await db.get_calculations_by_handler(handler_name)
    
    if not calculations:
        return None
    
    # Extract metrics
    fcr_values = [calc["feed_conversion_ratio"] for calc in calculations]
    mortality_values = [calc["mortality_rate_percent"] for calc in calculations]
    daily_gain_values = [calc["daily_weight_gain"] for calc in calculations]
    cost_per_kg_values = [calc["net_cost_per_kg"] for calc in calculations]
    total_chicks = sum(calc["input_data"]["initial_chicks"] for calc in calculations)
    
    avg_fcr = statistics.mean(fcr_values)
    avg_mortality = statistics.mean(mortality_values)
    avg_daily_gain = statistics.mean(daily_gain_values)
    avg_cost_per_kg = statistics.mean(cost_per_kg_values)
    
    # Calculate performance score (0-100, higher is better)
    fcr_score = max(0, min(100, (2.8 - avg_fcr) / (2.8 - 1.6) * 100))
    mortality_score = max(0, min(100, (12 - avg_mortality) / (12 - 3) * 100))
    gain_score = max(0, min(100, (avg_daily_gain - 0.045) / (0.065 - 0.045) * 100))
    performance_score = (fcr_score * 0.35 + mortality_score * 0.35 + gain_score * 0.30)
    
    return HandlerPerformance(
        handler_name=handler_name,
        total_batches=len(calculations),
        avg_feed_conversion_ratio=round(avg_fcr, 2),
        avg_mortality_rate=round(avg_mortality, 2),
        avg_daily_weight_gain=round(avg_daily_gain, 3),
        avg_cost_per_kg=round(avg_cost_per_kg, 2),
        total_chicks_processed=total_chicks,
        performance_score=round(performance_score, 1)
    )

async def export_batch_report(calculation: BroilerCalculation) -> str:
    """
    Export batch calculation to a JSON file
    """
    filename = f"batch_{calculation.input_data.batch_id}_{calculation.input_data.shed_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = EXPORTS_DIR / filename
    
    # Create export data
    export_data = {
        "batch_info": {
            "batch_id": calculation.input_data.batch_id,
            "shed_number": calculation.input_data.shed_number,
            "handler_name": calculation.input_data.handler_name,
            "date": calculation.created_at.isoformat()
        },
        "performance_metrics": {
            "feed_conversion_ratio": calculation.feed_conversion_ratio,
            "mortality_rate_percent": calculation.mortality_rate_percent,
            "weighted_average_age": calculation.weighted_average_age,
            "daily_weight_gain": calculation.daily_weight_gain,
            "cost_per_kg": calculation.net_cost_per_kg
        },
        "production_data": {
            "initial_chicks": calculation.input_data.initial_chicks,
            "surviving_chicks": calculation.surviving_chicks,
            "removed_chicks": calculation.removed_chicks,
            "missing_chicks": calculation.missing_chicks,
            "total_weight_produced_kg": calculation.total_weight_produced_kg,
            "total_feed_consumed_kg": calculation.total_feed_consumed_kg
        },
        "financial_summary": {
            "total_cost": calculation.total_cost,
            "total_revenue": calculation.total_revenue,
            "net_cost_per_kg": calculation.net_cost_per_kg,
            "cost_breakdown": calculation.cost_breakdown.dict()
        },
        "removal_batches": [batch.dict() for batch in calculation.input_data.removal_batches]
    }
    
    # Write to file
    with open(filepath, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    return filename

def generate_pdf_report(calculation: BroilerCalculation) -> str:
    """
    Generate a professional PDF report for batch closure
    """
    filename = f"batch_report_{calculation.input_data.batch_id}_{calculation.input_data.shed_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = EXPORTS_DIR / filename
    
    # Create PDF document
    doc = SimpleDocTemplate(str(filepath), pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkgreen
    )
    
    # Title and Header
    story.append(Paragraph("BROILER BATCH CLOSURE REPORT", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Batch Information
    story.append(Paragraph("BATCH IDENTIFICATION", heading_style))
    batch_data = [
        ['Batch ID:', calculation.input_data.batch_id],
        ['Shed Number:', calculation.input_data.shed_number],
        ['Handler:', calculation.input_data.handler_name],
        ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M')],
    ]
    
    # Add dates if available
    if hasattr(calculation.input_data, 'entry_date') and calculation.input_data.entry_date:
        if isinstance(calculation.input_data.entry_date, datetime):
            batch_data.insert(-1, ['Entry Date:', calculation.input_data.entry_date.strftime('%Y-%m-%d')])
        else:
            batch_data.insert(-1, ['Entry Date:', str(calculation.input_data.entry_date)])
    
    if hasattr(calculation.input_data, 'exit_date') and calculation.input_data.exit_date:
        if isinstance(calculation.input_data.exit_date, datetime):
            batch_data.insert(-1, ['Exit Date:', calculation.input_data.exit_date.strftime('%Y-%m-%d')])
        else:
            batch_data.insert(-1, ['Exit Date:', str(calculation.input_data.exit_date)])
    
    batch_table = Table(batch_data, colWidths=[2*inch, 3*inch])
    batch_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    story.append(batch_table)
    story.append(Spacer(1, 20))
    
    # Performance Summary
    story.append(Paragraph("PERFORMANCE SUMMARY", heading_style))
    performance_data = [
        ['Metric', 'Value', 'Status'],
        ['Feed Conversion Ratio', f"{calculation.feed_conversion_ratio}", 
         'Excellent' if calculation.feed_conversion_ratio <= 1.8 else 'Good' if calculation.feed_conversion_ratio <= 2.2 else 'Average'],
        ['Mortality Rate', f"{calculation.mortality_rate_percent}%",
         'Excellent' if calculation.mortality_rate_percent <= 3 else 'Good' if calculation.mortality_rate_percent <= 7 else 'Needs Attention'],
        ['Weighted Average Age', f"{calculation.weighted_average_age} days", 'Optimal'],
        ['Daily Weight Gain', f"{calculation.daily_weight_gain} kg", 
         'Excellent' if calculation.daily_weight_gain >= 0.065 else 'Good' if calculation.daily_weight_gain >= 0.055 else 'Average'],
        ['Net Cost per kg', f"${calculation.net_cost_per_kg:.2f}", 'Calculated']
    ]
    
    perf_table = Table(performance_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    perf_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
    ]))
    story.append(perf_table)
    story.append(Spacer(1, 20))
    
    # Production Data
    story.append(Paragraph("PRODUCTION DATA", heading_style))
    production_data = [
        ['Parameter', 'Count/Amount'],
        ['Initial Chicks', f"{calculation.input_data.initial_chicks:,}"],
        ['Chicks Died', f"{calculation.input_data.chicks_died:,}"],
        ['Surviving Chicks', f"{calculation.surviving_chicks:,}"],
        ['Viability (Caught)', f"{calculation.viability:,}"],
        ['Missing Chicks', f"{calculation.missing_chicks:,}"],
        ['Total Weight Produced', f"{calculation.total_weight_produced_kg:,} kg"],
        ['Total Feed Consumed', f"{calculation.total_feed_consumed_kg:,} kg"],
        ['Average Weight per Chick', f"{calculation.average_weight_per_chick:.2f} kg"],
        ['Viability Rate', f"{(calculation.viability / calculation.input_data.initial_chicks * 100):.1f}%"],
    ]
    
    prod_table = Table(production_data, colWidths=[3*inch, 2*inch])
    prod_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
    ]))
    story.append(prod_table)
    
    # Generate PDF
    doc.build(story)
    
    return filename

# API Routes
@app.get("/")
async def root():
    return {"message": "Offline Broiler Farm Management System API", "status": "running"}

@app.post("/calculate", response_model=CalculationResult)
async def calculate_broiler_costs(input_data: BroilerCalculationInput):
    """Calculate enhanced broiler chicken production costs and metrics"""
    # Validate input
    if input_data.initial_chicks <= 0:
        raise HTTPException(status_code=400, detail="Initial chicks must be greater than 0")
    if input_data.chicks_died > input_data.initial_chicks:
        raise HTTPException(status_code=400, detail="Chicks died cannot be more than initial chicks")
    if not input_data.removal_batches:
        raise HTTPException(status_code=400, detail="At least one removal batch is required")
    
    # Check if batch ID already exists
    existing_batch = await db.find_calculation_by_batch_id(input_data.batch_id)
    if existing_batch:
        raise HTTPException(status_code=400, detail=f"Batch ID '{input_data.batch_id}' already exists")
    
    # Validate removal batches
    total_removed = sum(batch.quantity for batch in input_data.removal_batches)
    surviving_chicks = input_data.initial_chicks - input_data.chicks_died
    if total_removed > surviving_chicks:
        raise HTTPException(status_code=400, detail="Total removed chicks cannot exceed surviving chicks")
    
    # Validate removal batches
    for i, batch in enumerate(input_data.removal_batches):
        if batch.quantity <= 0:
            raise HTTPException(status_code=400, detail=f"Batch {i+1}: Quantity must be greater than 0")
        if batch.total_weight_kg <= 0:
            raise HTTPException(status_code=400, detail=f"Batch {i+1}: Weight must be greater than 0")
    
    try:
        # Calculate metrics
        calculation = calculate_enhanced_broiler_metrics(input_data)
        
        # Generate insights
        insights = generate_enhanced_insights(calculation)
        
        # Add handler to database if not exists
        existing_handler = await db.find_handler_by_name(input_data.handler_name)
        if not existing_handler:
            handler_data = {"name": input_data.handler_name}
            await db.insert_handler(handler_data)
        
        # Save calculation to database
        calculation_dict = calculation.dict()
        await db.insert_calculation(calculation_dict)
        
        # Export batch report (JSON and PDF)
        json_filename = await export_batch_report(calculation)
        pdf_filename = generate_pdf_report(calculation)
        
        # Add export info to insights
        insights.append(f"📄 JSON report exported as: {json_filename}")
        insights.append(f"📄 PDF report exported as: {pdf_filename}")
        
        return CalculationResult(calculation=calculation, insights=insights)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@app.get("/calculations", response_model=List[BatchSummary])
async def get_calculations():
    """Get all saved calculations summary"""
    calculations = await db.get_all_calculations()
    summaries = []
    
    for calc in calculations:
        try:
            summary = BatchSummary(
                batch_id=calc["input_data"]["batch_id"],
                shed_number=calc["input_data"]["shed_number"],
                handler_name=calc["input_data"]["handler_name"],
                date=datetime.fromisoformat(calc["created_at"]),
                initial_chicks=calc["input_data"]["initial_chicks"],
                fcr=calc["feed_conversion_ratio"],
                mortality_percent=calc["mortality_rate_percent"],
                cost_per_kg=calc["net_cost_per_kg"]
            )
            summaries.append(summary)
        except (KeyError, TypeError, ValueError):
            continue
    
    return summaries

@app.get("/handlers/names")
async def get_handler_names():
    """Get all handler names for dropdown"""
    return await db.get_handler_names()

@app.get("/handlers/performance")
async def get_handlers_performance():
    """Get performance analysis for all handlers"""
    handlers = await db.get_all_handlers()
    performances = []
    
    for handler in handlers:
        performance = await calculate_handler_performance(handler["name"])
        if performance:
            performances.append(performance)
    
    # Sort by performance score (descending)
    performances.sort(key=lambda x: x.performance_score, reverse=True)
    
    return performances

@app.get("/handlers/{handler_name}/performance")
async def get_handler_performance_endpoint(handler_name: str):
    """Get performance analysis for a specific handler"""
    performance = await calculate_handler_performance(handler_name)
    if not performance:
        raise HTTPException(status_code=404, detail="Handler not found or no batches recorded")
    
    return performance

@app.get("/handlers")
async def get_handlers():
    """Get all handlers"""
    handlers_data = await db.get_all_handlers()
    return [Handler(**handler) for handler in handlers_data]

@app.post("/handlers", response_model=Handler)
async def create_handler(handler_data: HandlerCreate):
    """Create a new handler"""
    # Check if handler name already exists
    existing_handler = await db.find_handler_by_name(handler_data.name)
    if existing_handler:
        raise HTTPException(status_code=400, detail=f"Handler '{handler_data.name}' already exists")
    
    handler_dict = handler_data.dict()
    handler_id = await db.insert_handler(handler_dict)
    handler_dict['id'] = handler_id
    handler_dict['created_at'] = datetime.now()
    handler_dict['updated_at'] = datetime.now()
    
    return Handler(**handler_dict)

@app.get("/handlers/{handler_id}", response_model=Handler)
async def get_handler(handler_id: str):
    """Get a specific handler"""
    handler = await db.find_handler_by_id(handler_id)
    if not handler:
        raise HTTPException(status_code=404, detail="Handler not found")
    return Handler(**handler)

@app.put("/handlers/{handler_id}", response_model=Handler)
async def update_handler(handler_id: str, handler_data: HandlerUpdate):
    """Update a handler"""
    # Check if handler exists
    existing_handler = await db.find_handler_by_id(handler_id)
    if not existing_handler:
        raise HTTPException(status_code=404, detail="Handler not found")
    
    # Check if new name conflicts with existing handler
    if handler_data.name:
        name_conflict = await db.find_handler_by_name(handler_data.name)
        if name_conflict and name_conflict['id'] != handler_id:
            raise HTTPException(status_code=400, detail=f"Handler name '{handler_data.name}' already exists")
    
    # Update handler
    update_data = {k: v for k, v in handler_data.dict().items() if v is not None}
    update_data.update(existing_handler)  # Merge with existing data
    
    await db.update_handler(handler_id, update_data)
    
    # Return updated handler
    updated_handler = await db.find_handler_by_id(handler_id)
    return Handler(**updated_handler)

@app.delete("/handlers/{handler_id}")
async def delete_handler(handler_id: str):
    """Delete a handler"""
    # Check if handler has any batches
    handler = await db.find_handler_by_id(handler_id)
    if not handler:
        raise HTTPException(status_code=404, detail="Handler not found")
    
    batch_count = await db.count_calculations_by_handler(handler['name'])
    if batch_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete handler. They have {batch_count} batches recorded."
        )
    
    deleted = await db.delete_handler(handler_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Handler not found")
    
    return {"message": "Handler deleted successfully"}

# Shed Management Endpoints
@app.get("/admin/sheds", response_model=List[Shed])
async def get_all_sheds():
    """Get all sheds with full details"""
    sheds_data = await db.get_all_sheds()
    return [Shed(**shed) for shed in sheds_data]

@app.post("/admin/sheds", response_model=Shed)
async def create_shed(shed_data: ShedCreate):
    """Create a new shed"""
    # Check if shed number already exists
    existing_shed = await db.find_shed_by_number(shed_data.number)
    if existing_shed:
        raise HTTPException(status_code=400, detail=f"Shed '{shed_data.number}' already exists")
    
    shed_dict = shed_data.dict()
    shed_id = await db.insert_shed(shed_dict)
    shed_dict['id'] = shed_id
    shed_dict['created_at'] = datetime.now()
    shed_dict['updated_at'] = datetime.now()
    
    return Shed(**shed_dict)

@app.get("/admin/sheds/{shed_id}", response_model=Shed)
async def get_shed(shed_id: str):
    """Get a specific shed"""
    shed = await db.find_shed_by_id(shed_id)
    if not shed:
        raise HTTPException(status_code=404, detail="Shed not found")
    return Shed(**shed)

@app.put("/admin/sheds/{shed_id}", response_model=Shed)
async def update_shed(shed_id: str, shed_data: ShedUpdate):
    """Update a shed"""
    # Check if shed exists
    existing_shed = await db.find_shed_by_id(shed_id)
    if not existing_shed:
        raise HTTPException(status_code=404, detail="Shed not found")
    
    # Check if new number conflicts with existing shed
    if shed_data.number:
        number_conflict = await db.find_shed_by_number(shed_data.number)
        if number_conflict and number_conflict['id'] != shed_id:
            raise HTTPException(status_code=400, detail=f"Shed number '{shed_data.number}' already exists")
    
    # Update shed
    update_data = {k: v for k, v in shed_data.dict().items() if v is not None}
    update_data.update(existing_shed)  # Merge with existing data
    
    await db.update_shed(shed_id, update_data)
    
    # Return updated shed
    updated_shed = await db.find_shed_by_id(shed_id)
    return Shed(**updated_shed)

@app.delete("/admin/sheds/{shed_id}")
async def delete_shed(shed_id: str):
    """Delete a shed"""
    # Check if shed has any batches (this would need a custom query in real implementation)
    shed = await db.find_shed_by_id(shed_id)
    if not shed:
        raise HTTPException(status_code=404, detail="Shed not found")
    
    deleted = await db.delete_shed(shed_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Shed not found")
    
    return {"message": "Shed deleted successfully"}

@app.put("/batches/{batch_id}")
async def update_batch(batch_id: str, input_data: BroilerCalculationInput):
    """Update an existing batch calculation"""
    # Check if batch exists
    existing_batch = await db.find_calculation_by_batch_id(batch_id)
    if not existing_batch:
        raise HTTPException(status_code=404, detail=f"Batch ID '{batch_id}' not found")
    
    # Validate input (same as create)
    if input_data.initial_chicks <= 0:
        raise HTTPException(status_code=400, detail="Initial chicks must be greater than 0")
    if input_data.chicks_died > input_data.initial_chicks:
        raise HTTPException(status_code=400, detail="Chicks died cannot be more than initial chicks")
    if not input_data.removal_batches:
        raise HTTPException(status_code=400, detail="At least one removal batch is required")
    
    # Validate removal batches
    total_removed = sum(batch.quantity for batch in input_data.removal_batches)
    surviving_chicks = input_data.initial_chicks - input_data.chicks_died
    if total_removed > surviving_chicks:
        raise HTTPException(status_code=400, detail="Total removed chicks cannot exceed surviving chicks")
    
    # Validate removal batches
    for i, batch in enumerate(input_data.removal_batches):
        if batch.quantity <= 0:
            raise HTTPException(status_code=400, detail=f"Batch {i+1}: Quantity must be greater than 0")
        if batch.total_weight_kg <= 0:
            raise HTTPException(status_code=400, detail=f"Batch {i+1}: Weight must be greater than 0")
    
    try:
        # Calculate metrics
        calculation = calculate_enhanced_broiler_metrics(input_data)
        calculation.id = existing_batch["id"]  # Keep the same ID
        calculation.created_at = datetime.fromisoformat(existing_batch["created_at"])  # Keep original creation date
        
        # Generate insights
        insights = generate_enhanced_insights(calculation)
        
        # Update handler if name changed
        if input_data.handler_name != existing_batch["input_data"]["handler_name"]:
            existing_handler = await db.find_handler_by_name(input_data.handler_name)
            if not existing_handler:
                handler_data = {"name": input_data.handler_name}
                await db.insert_handler(handler_data)
        
        # Update the batch in database
        calculation_dict = calculation.dict()
        await db.update_calculation(batch_id, calculation_dict)
        
        # Export updated batch report
        json_filename = await export_batch_report(calculation)
        pdf_filename = generate_pdf_report(calculation)
        
        # Add export info to insights
        insights.append(f"📄 Updated JSON report exported as: {json_filename}")
        insights.append(f"📄 Updated PDF report exported as: {pdf_filename}")
        
        return CalculationResult(calculation=calculation, insights=insights)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update error: {str(e)}")

@app.get("/batches/{batch_id}")
async def get_batch_details(batch_id: str):
    """Get detailed information for a specific batch"""
    calculation = await db.find_calculation_by_batch_id(batch_id)
    if not calculation:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return BroilerCalculation(**calculation)

@app.get("/batches/{batch_id}/export-pdf")
async def regenerate_batch_pdf(batch_id: str):
    """Regenerate PDF report for an existing batch"""
    calculation = await db.find_calculation_by_batch_id(batch_id)
    if not calculation:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Convert back to calculation object
    calc_obj = BroilerCalculation(**calculation)
    
    # Generate new PDF
    pdf_filename = generate_pdf_report(calc_obj)
    
    return {"message": "PDF regenerated successfully", "filename": pdf_filename}

@app.get("/export/{filename}")
async def download_export(filename: str):
    """Download exported batch report (JSON or PDF)"""
    filepath = EXPORTS_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Export file not found")
    
    # Determine content type based on file extension
    if filename.endswith('.pdf'):
        media_type = 'application/pdf'
    else:
        media_type = 'application/json'
    
    return FileResponse(filepath, filename=filename, media_type=media_type)

@app.get("/sheds")
async def get_sheds():
    """Get all shed numbers"""
    return await db.get_shed_numbers()

@app.delete("/batches/{batch_id}")
async def delete_batch_by_id(batch_id: str):
    """Delete a batch by batch ID"""
    deleted = await db.delete_calculation_by_batch_id(batch_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Batch not found")
    return {"message": "Batch deleted successfully"}

@app.delete("/calculations/{calculation_id}")
async def delete_calculation(calculation_id: str):
    """Delete a specific calculation"""
    deleted = await db.delete_calculation_by_id(calculation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return {"message": "Calculation deleted successfully"}

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)