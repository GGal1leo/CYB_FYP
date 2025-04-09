from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import json
from cyber_monitor import CyberMonitor
from ioc_analyzer import IOCAnalyzer
import os
from datetime import datetime

# Create necessary directories
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize the cyber monitor
monitor = CyberMonitor()
ioc_analyzer = IOCAnalyzer()

# Store recent articles and analyses
recent_articles = []
active_connections = set()

async def broadcast_message(message: dict):
    """Broadcast a message to all connected WebSocket clients."""
    for connection in active_connections:
        try:
            # Ensure all datetime objects are serialized
            if 'data' in message and 'article' in message['data']:
                message['data']['article'] = monitor.serialize_article(message['data']['article'])
            await connection.send_json(message)
        except Exception as e:
            print(f"Error broadcasting message: {e}")
            active_connections.remove(connection)

async def monitor_thread():
    """Background thread for monitoring articles."""
    while True:
        try:
            articles = monitor.get_articles()
            for article in articles:
                # Check if we've seen this article before
                article_key = f"{article['title']}_{article['link']}"
                if article_key not in monitor.seen_articles:
                    # Process and analyze the article
                    analysis = monitor.analyze_article(article)
                    
                    # Add to recent articles
                    recent_articles.append({
                        'article': monitor.serialize_article(article),
                        'analysis': analysis
                    })
                    if len(recent_articles) > 50:  # Keep last 50 articles
                        recent_articles.pop(0)
                    
                    # Broadcast the new article and analysis
                    await broadcast_message({
                        "type": "new_article",
                        "data": {
                            "article": monitor.serialize_article(article),
                            "analysis": analysis
                        }
                    })
                    
                    # Mark as seen
                    monitor.seen_articles.add(article_key)
        except Exception as e:
            print(f"Error in monitor thread: {e}")
        await asyncio.sleep(60)  # Check every minute

@app.on_event("startup")
async def startup_event():
    """Start the monitoring thread when the application starts."""
    asyncio.create_task(monitor_thread())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections."""
    await websocket.accept()
    active_connections.add(websocket)
    
    try:
        # Send initial data to the new connection
        await websocket.send_json({
            "type": "initial_data",
            "data": recent_articles
        })
        
        # Keep the connection alive
        while True:
            await websocket.receive_text()
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        active_connections.remove(websocket)

@app.get("/")
async def read_root(request: Request):
    """Render the main page."""
    return templates.TemplateResponse("monitor.html", {
        "request": request,
        "recent_articles": recent_articles
    })

@app.post("/analyze")
async def analyze_ioc(request: Request):
    """Handle manual IOC analysis requests."""
    try:
        data = await request.json()
        ioc = data.get("ioc")
        
        if not ioc:
            return JSONResponse(
                status_code=400,
                content={"error": "No IOC provided"}
            )
        
        # Generate the report
        report = ioc_analyzer.generate_report(ioc)
        
        # Get the HTML formatted report
        html_report = ioc_analyzer.display_report(report)
        
        return JSONResponse({
            "html": html_report,
            "raw_data": {
                "ioc": ioc,
                "analysis": report['ai_analysis']['analysis'],
                "threat_data": report['threatfox_data']
            }
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 