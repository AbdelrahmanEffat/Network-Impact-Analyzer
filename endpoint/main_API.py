# main.py (updated)
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Literal, Dict, Any
import pandas as pd
from unified_network_analyzer import UnifiedNetworkImpactAnalyzer
import logging
import io
import zipfile
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Network Impact Analysis API",
    description="API for analyzing network impact from node or exchange failures",
    version="1.0.0"
)

# Request model
class AnalysisRequest(BaseModel):
    identifier: str
    identifier_type: Optional[Literal['node', 'exchange', 'auto']] = 'auto'

# Response models
class AnalysisResponse(BaseModel):
    status: str
    message: str
    total_records: int
    unique_msans: int
    analysis_type: str
    execution_time_seconds: float
    results_preview: dict
    impact_summary: dict

# Global analyzer instances (initialized on startup)
we_analyzer = None
others_analyzer = None

@app.on_event("startup")
async def startup_event():
    """Initialize the analyzers with CSV files on startup"""
    global we_analyzer, others_analyzer
    
    try:
        logger.info("Loading CSV files...")
        
        # Load your CSV files
        df_report_we = pd.read_csv('Report(11).csv')  # WE data
        df_report_others = pd.read_csv('Report(12).csv')  # Others data
        df_res_ospf = pd.read_csv('res_ospf.csv')
        df_wan = pd.read_csv('wan.csv')
        df_agg = pd.read_csv('agg.csv')
        
        # Initialize analyzers for both data types
        we_analyzer = UnifiedNetworkImpactAnalyzer(df_report_we, df_res_ospf, df_wan, df_agg)
        others_analyzer = UnifiedNetworkImpactAnalyzer(df_report_others, df_res_ospf, df_wan, df_agg)
        
        logger.info(f"Data loaded successfully. WE shape: {df_report_we.shape}, Others shape: {df_report_others.shape}")
        
    except Exception as e:
        logger.error(f"Failed to load data: {str(e)}")
        raise

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Network Impact Analysis API", 
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "POST - Analyze network impact for both WE and Others",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if we_analyzer is None or others_analyzer is None:
        raise HTTPException(status_code=503, detail="Service not ready - analyzers not initialized")
    
    return {"status": "healthy", "we_analyzer_ready": we_analyzer is not None, "others_analyzer_ready": others_analyzer is not None}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_network_impact(request: AnalysisRequest):
    """
    Analyze network impact from node or exchange failure for both WE and Others data
    """
    if we_analyzer is None or others_analyzer is None:
        raise HTTPException(
            status_code=503, 
            detail="Service not ready - analyzers not initialized"
        )
    
    try:
        logger.info(f"Starting analysis for {request.identifier} (type: {request.identifier_type})")
        
        import time
        start_time = time.time()
        
        # Run the analysis on both data types
        we_results = we_analyzer.run_complete_analysis(
            request.identifier, 
            request.identifier_type
        )
        
        others_results = others_analyzer.run_complete_analysis(
            request.identifier, 
            request.identifier_type
        )
        
        execution_time = time.time() - start_time
        
        # Create impact summaries
        we_impact_summary = _create_impact_summary(we_results)
        others_impact_summary = _create_impact_summary(others_results)
        
        # Get previews
        we_preview = _get_results_preview(we_results)
        others_preview = _get_results_preview(others_results)
        
        # Determine analysis type
        analysis_type = "Exchange" if request.identifier_type == 'exchange' else "Node"
        if request.identifier_type == 'auto':
            analysis_type = "Exchange" if ('.' in request.identifier or len(request.identifier.split('-')) < 4) else "Node"
        
        # Combine results
        combined_impact_summary = {
            "we": we_impact_summary,
            "others": others_impact_summary,
            "total_records": we_impact_summary.get("total_records", 0) + others_impact_summary.get("total_records", 0),
            "total_unique_msans": we_impact_summary.get("unique_msans", 0) + others_impact_summary.get("unique_msans", 0)
        }
        
        return AnalysisResponse(
            status="success",
            message=f"Analysis completed successfully for {request.identifier}",
            total_records=combined_impact_summary["total_records"],
            unique_msans=combined_impact_summary["total_unique_msans"],
            analysis_type=analysis_type,
            execution_time_seconds=round(execution_time, 3),
            results_preview={
                "we": we_preview,
                "others": others_preview
            },
            impact_summary=combined_impact_summary
        )
        
    except Exception as e:
        logger.error(f"Analysis failed for {request.identifier}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@app.post("/analyze/csv", response_class=StreamingResponse)
async def analyze_and_return_csv(request: AnalysisRequest):
    """
    Analyze network impact and return results as a zip file containing both WE and Others CSVs
    """
    if we_analyzer is None or others_analyzer is None:
        raise HTTPException(
            status_code=503, 
            detail="Service not ready - analyzers not initialized"
        )
    
    try:
        logger.info(f"Starting Impact Analysis for {request.identifier} (type: {request.identifier_type})")
        
        # Run analysis on both data types
        we_results = we_analyzer.run_complete_analysis(
            request.identifier, 
            request.identifier_type
        )
        
        others_results = others_analyzer.run_complete_analysis(
            request.identifier, 
            request.identifier_type
        )
        
        # Create zip file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            # Add WE results
            we_csv = we_results.to_csv(index=False)
            zip_file.writestr(f"we_impact_{request.identifier}.csv", we_csv)
            
            # Add Others results
            others_csv = others_results.to_csv(index=False)
            zip_file.writestr(f"others_impact_{request.identifier}.csv", others_csv)
        
        zip_buffer.seek(0)
        
        # Generate filename
        safe_identifier = request.identifier.replace('/', '_').replace('\\', '_').replace('.', '_')
        filename = f"network_impact_{safe_identifier}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        # Return as downloadable zip
        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
        
    except Exception as e:
        logger.error(f"CSV analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"CSV analysis failed: {str(e)}"
        )

def _get_results_preview(results_df, num_records=5):
    """Get preview of results with key columns"""
    if results_df.empty:
        return []
    
    preview_columns = [
        'MSANCODE', 'EDGE', 'distribution_hostname', 'BNG_HOSTNAME', 
        'STATUS', 'CUST', 'cir_type', 'Impact'
    ]
    
    # Adjust columns based on available data
    available_preview_cols = [col for col in preview_columns if col in results_df.columns]
    
    # Add BITSTREAM_HOSTNAME if available
    if 'BITSTREAM_HOSTNAME' in results_df.columns and 'distribution_hostname' not in available_preview_cols:
        available_preview_cols.append('BITSTREAM_HOSTNAME')
    
    return results_df[available_preview_cols].head(num_records).to_dict('records')

def _create_impact_summary(results_df):
    """Create impact summary statistics"""
    if results_df.empty:
        return {"total_records": 0, "unique_msans": 0, "impact_breakdown": {}}
    
    summary = {
        "total_records": len(results_df),
        "unique_msans": len(results_df['MSANCODE'].unique()) if 'MSANCODE' in results_df.columns else 0,
    }
    
    # Impact breakdown
    if 'Impact' in results_df.columns:
        impact_counts = results_df['Impact'].value_counts().to_dict()
        summary["impact_breakdown"] = impact_counts
    
    # Status breakdown
    if 'STATUS' in results_df.columns:
        status_counts = results_df['STATUS'].value_counts().to_dict()
        summary["status_breakdown"] = status_counts
    
    # Circuit type breakdown
    if 'cir_type' in results_df.columns:
        cir_type_counts = results_df['cir_type'].value_counts().to_dict()
        summary["circuit_type_breakdown"] = cir_type_counts
    
    return summary

if __name__ == "__main__":
    import uvicorn
    
    # Run the API
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )