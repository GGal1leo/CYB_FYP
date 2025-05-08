from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from ioc_analyzer import IOCAnalyzer
import uvicorn
from pathlib import Path

app = FastAPI(title="Cyber Incident Monitoring Tool")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize IOC Analyzer
analyzer = IOCAnalyzer()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Cyber Incident Monitor"}
    )

@app.post("/analyze")
async def analyze_ioc(request: Request, ioc: str = Form(...)):
    try:
        report = analyzer.generate_report(ioc)
        return templates.TemplateResponse(
            "results.html",
            {
                "request": request,
                "report": report,
                "title": f"Analysis Results for {ioc}"
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": str(e),
                "title": "Error"
            }
        )

if __name__ == "__main__":
    # Create necessary directories
    Path("templates").mkdir(exist_ok=True)
    Path("static").mkdir(exist_ok=True)
    
    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=8000) 