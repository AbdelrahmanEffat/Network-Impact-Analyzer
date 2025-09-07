from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import pandas as pd
import json
from datetime import datetime
import io
import zipfile

app = FastAPI(
    title="Network Impact Analysis Web Interface",
    description="Web interface for visualizing network impact analysis results",
    version="1.1.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Configuration - update with your API URL
API_BASE_URL = "http://localhost:8000"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with analysis form"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_network_impact(
    request: Request,
    identifier: str = Form(...),
    identifier_type: str = Form("auto")
):
    """Analyze network impact and display results"""
    try:
        # Call the analysis API
        api_url = f"{API_BASE_URL}/analyze"
        response = requests.post(
            api_url,
            json={"identifier": identifier, "identifier_type": identifier_type}
        )
        
        if response.status_code != 200:
            error_msg = f"API request failed: {response.status_code} - {response.text}"
            return templates.TemplateResponse(
                "error.html", 
                {"request": request, "error": error_msg}
            )
        
        # Parse the API response
        result = response.json()
        
        # Get detailed data for both WE and Others
        we_data = get_detailed_data(identifier, identifier_type, "we")
        others_data = get_detailed_data(identifier, identifier_type, "others")
        
        # Prepare data for the template
        template_data = {
            "request": request,
            "identifier": identifier,
            "identifier_type": identifier_type,
            "result": result,
            "we_data": we_data,
            "others_data": others_data,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return templates.TemplateResponse("results.html", template_data)
        
    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "error": error_msg}
        )

@app.post("/api/analyze")
async def api_analyze_network_impact(identifier: str, identifier_type: str = "auto"):
    """API endpoint to get analysis results"""
    try:
        # Call the analysis API
        api_url = f"{API_BASE_URL}/analyze"
        response = requests.post(
            api_url,
            json={"identifier": identifier, "identifier_type": identifier_type}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        return response.json()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/download")
async def download_results(identifier: str, identifier_type: str = "auto"):
    """Download analysis results as CSV"""
    try:
        # Call the CSV API
        api_url = f"{API_BASE_URL}/analyze/csv"
        response = requests.post(
            api_url,
            json={"identifier": identifier, "identifier_type": identifier_type}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        # Create a zip file with both WE and Others data
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            # Get WE data
            we_data = get_detailed_data(identifier, identifier_type, "we")
            we_csv = we_data.to_csv(index=False)
            zip_file.writestr(f"we_impact_{identifier}.csv", we_csv)
            
            # Get Others data
            others_data = get_detailed_data(identifier, identifier_type, "others")
            others_csv = others_data.to_csv(index=False)
            zip_file.writestr(f"others_impact_{identifier}.csv", others_csv)
        
        zip_buffer.seek(0)
        
        # Generate filename
        safe_identifier = identifier.replace('/', '_').replace('\\', '_').replace('.', '_')
        filename = f"network_impact_{safe_identifier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        # Return as downloadable zip
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

# Replaced
def get_detailed_data(identifier, identifier_type, data_type):
    """Get detailed data from the API"""
    try:
        api_url = f"{API_BASE_URL}/analyze/detailed"
        response = requests.post(
            api_url,
            json={"identifier": identifier, "identifier_type": identifier_type}
        )
        
        if response.status_code != 200:
            return pd.DataFrame()
            
        result = response.json()
        if data_type == "we":
            return pd.DataFrame(result['we_results'])
        else:
            return pd.DataFrame(result['others_results'])
            
    except Exception as e:
        print(f"Error getting detailed data: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)