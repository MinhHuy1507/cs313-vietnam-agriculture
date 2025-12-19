"""
File: backend/main.py
Description:
    This is the main entry point for the Backend (FastAPI) application.
    This file is responsible for:
    1. Initializing the FastAPI application.
    2. Defining the 'startup' event to create database tables (from model.py).
    3. Defining all API endpoints (routes) that the Frontend will call:
        - GET /: Welcome page.
        - GET /db-test: Database connection verification.
        - GET /api/v1/statistics/provinces: Retrieve list of provinces.
        - GET /api/v1/statistics/agriculture-data: Retrieve agricultural data (with filtering).
        - GET /api/v1/statistics/climate-data: Retrieve climate data (with JOIN).
        - GET /api/v1/statistics/soil-data: Retrieve soil data (with JOIN).
        - POST /api/v1/predict: Accept 21 features and return predictions (currently using mock logic).
"""
from fastapi import FastAPI, Depends
from utils.connect_database import get_session, get_db_and_tables
from sqlmodel import Session, select

from typing import Annotated, List, Optional

from model import AgricultureData, ClimateData, Province, SoilData
from schemas import AgricultureDataRead, ClimateDataRead, ProvinceRead, SoilDataRead
from dependencies import AgricultureQuery, ClimateQuery, SoilQuery, PredictionInput, PredictionOutput
from ml_engine.pipeline import run_pipeline

# --- 1. APPLICATION INITIALIZATION ---
app = FastAPI(
    title="Vietnam Agriculture API",
    description="API for querying agricultural, climate, and soil data, as well as yield prediction in Vietnam.",
    version="1.0.0"
)

# --- 2. STARTUP EVENT CONFIGURATION ---
@app.on_event("startup")
def start_up():
    """Invoke create_db_and_tables to initialize database and tables on startup event."""
    get_db_and_tables()

# --- 3. BASIC API ENDPOINTS ---
@app.get("/")
def init():
    return {"Welcome to Agriculture App"}

@app.get("/db-test")
def get_db_connection(session: Session = Depends(get_session)):
    """Endpoint to verify successful database connection."""
    try: 
        result= session.exec(select(1)).one()
        if result == 1:
                return {"status": "success", "message": "Database connection successful!", "result": result}
        else:
            return {"status": "fail", "message": "Connection successful but result is unexpected."}
        
    except Exception as e:
        return {"status": "error", "message": "Database connection failed.", "error_details": str(e)}
    
# --- 4. DATA RETRIEVAL API ENDPOINTS ---
@app.get("/api/v1/statistics/agriculture-data", response_model=list[AgricultureDataRead])
def get_agriculture_data(*, session: Annotated[Session, Depends(get_session)],
                         # Pagination parameters
                         skip: int = 0, # Skip first 'skip' records
                         limit: Optional[int] = 1000, # Retrieve maximum 'limit' records (default is 1000)
                         query_params: AgricultureQuery = Depends()):
    """
    API endpoint for retrieving agricultural data with filtering and pagination support.
    """
    query = select(AgricultureData)
    if query_params.year:
        query = query.where(AgricultureData.year == query_params.year)
    if query_params.commodity:
        query = query.where(AgricultureData.commodity == query_params.commodity)
    if query_params.season:
        query = query.where(AgricultureData.season == query_params.season)
    if query_params.region_name:
        query = query.where(AgricultureData.region_name == query_params.region_name)
    if query_params.region_level:
        query = query.where(AgricultureData.region_level == query_params.region_level)
    agriculture_data = session.exec(query.offset(skip).limit(limit)).all()
    return agriculture_data
    
@app.get("/api/v1/statistics/climate-data", response_model=list[ClimateDataRead])
def get_climate_data(*, session: Annotated[Session, Depends(get_session)],
                       # Pagination parameters
                       skip: int = 0,
                       limit: Optional[int] = 1000,
                       query_params: ClimateQuery = Depends()):
    """
    API endpoint for retrieving climate data.
    Automatically performs JOIN with Province table to retrieve 'province_name'.
    """
    query = select(ClimateData, Province).join(Province, ClimateData.province_id == Province.id)

    if query_params.year:
        query = query.where(ClimateData.year == query_params.year)
    
    if query_params.province_name:
        query = query.where(Province.province_name == query_params.province_name)
        
    query = query.offset(skip).limit(limit)
    
    # results_from_db is a list of tuples: [(climate1, province1), (climate2, province2), ...]
    results_from_db = session.exec(query).all()
    
    response = []
    for climate, province in results_from_db:
        data = climate.model_dump() 
        data['province_name'] = province.province_name 
        response.append(data)
    
    return response

@app.get("/api/v1/statistics/soil-data", response_model=List[SoilDataRead])
def get_soil_data(*, session: Annotated[Session, Depends(get_session)],
                  # Pagination parameters
                  skip: int = 0,
                  limit: Optional[int] = 1000,
                  query_params: SoilQuery = Depends()):
    """
    API endpoint for retrieving detailed soil data for each province.
    Automatically performs JOIN with Province table to retrieve 'province_name'.
    """
    query = select(SoilData, Province).join(Province, SoilData.province_id == Province.id)

    if query_params.province_name:
        query = query.where(Province.province_name == query_params.province_name)
        
    query = query.offset(skip).limit(limit)

    # results_from_db is a list of tuples: [(soil1, province1), (soil2, province2), ...]
    results_from_db = session.exec(query).all()
    
    response = []
    for soil, province in results_from_db:
        data = soil.model_dump()
        data['province_name'] = province.province_name 
        response.append(data)
    
    return response

@app.get("/api/v1/statistics/provinces", response_model=List[ProvinceRead])
def get_provinces(*, session: Annotated[Session, Depends(get_session)],
                  # Pagination parameters
                  skip: int = 0,
                  limit: Optional[int] = 100):
    """
    API endpoint for retrieving the list of all provinces/cities.
    """
    provinces = session.exec(select(Province).offset(skip).limit(limit)).all()
    return provinces

# --- 5. PREDICTION API ENDPOINT (POST) ---
@app.post("/api/v1/predict", response_model=PredictionOutput)
def post_prediction(
    *, 
    session: Annotated[Session, Depends(get_session)],
    input_data: PredictionInput
):
    """
    Prediction endpoint using ML Pipeline.
    Accepts input features and returns predicted production and yield.
    """
    # Convert Pydantic model to dict
    input_dict = input_data.dict()
    
    try:
        # Run ML Pipeline
        result = run_pipeline(input_dict)
        
        if result:
            return PredictionOutput(
                predicted_production=result['production_tonnes'],
                predicted_yield=result['yield_ton_per_ha'],
                predicted_area=input_data.area_thousand_ha
            )
        else:
            # Handle case where prediction returns None (e.g. error in pipeline)
            # For now return 0s or raise HTTP exception
            return PredictionOutput(
                predicted_production=0.0,
                predicted_yield=0.0,
                predicted_area=input_data.area_thousand_ha
            )
    except Exception as e:
        print(f"Prediction Error: {e}")
        # Return 0s on error for now, or raise HTTPException
        return PredictionOutput(
            predicted_production=0.0,
            predicted_yield=0.0,
            predicted_area=input_data.area_thousand_ha
        )