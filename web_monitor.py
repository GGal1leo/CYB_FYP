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
from contextlib import asynccontextmanager
from fastapi import WebSocketDisconnect
import requests
from bs4 import BeautifulSoup

# Create necessary directories
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Store recent articles and analyses
recent_articles = []
active_connections = set()

async def broadcast_message(message: dict):
    """Broadcast a message to all connected WebSocket clients."""
    disconnected = set()
    for connection in active_connections:
        try:
            # Ensure all datetime objects are serialized
            if 'data' in message and 'article' in message['data']:
                message['data']['article'] = monitor.serialize_article(message['data']['article'])
            await connection.send_json(message)
        except Exception as e:
            print(f"Error broadcasting message to client: {e}")
            disconnected.add(connection)
    
    # Remove disconnected clients
    for connection in disconnected:
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global monitor, ioc_analyzer
    monitor = CyberMonitor()
    ioc_analyzer = IOCAnalyzer()
    asyncio.create_task(monitor_thread())
    yield
    # Shutdown
    # Clean up resources if needed

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections."""
    try:
        await websocket.accept()
        active_connections.add(websocket)
        
        # Send initial data to the new connection
        try:
            await websocket.send_json({
                "type": "initial_data",
                "data": recent_articles
            })
        except Exception as e:
            print(f"Error sending initial data: {e}")
            active_connections.remove(websocket)
            return
        
        # Keep the connection alive and handle messages
        while True:
            try:
                # Wait for a message from the client
                data = await websocket.receive_text()
                # Send a ping response to keep the connection alive
                await websocket.send_json({"type": "pong"})
            except WebSocketDisconnect:
                print("Client disconnected")
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                break
                
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        if websocket in active_connections:
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

@app.post("/analyze_article")
async def analyze_article(request: Request):
    """Handle article analysis requests."""
    try:
        data = await request.json()
        title = data.get('title')
        link = data.get('link')
        iocs = data.get('iocs', [])
        
        if not title or not link:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required article data"}
            )
        
        # Fetch and analyze the article content
        try:
            article_response = requests.get(link, headers=monitor.headers)
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            
            # Extract the main content
            content = article_soup.find('article') or article_soup.find('main') or article_soup.find('div', class_='content')
            if content:
                article_text = content.get_text(strip=True)
            else:
                article_text = article_soup.get_text(strip=True)
            
            # Get article analysis from AI
            article_analysis = ioc_analyzer.analyze_article_content(article_text)
            if not article_analysis:
                print(f"Failed to analyze article content for: {title}")
                article_analysis = {
                    "html": "<div class='alert alert-warning'>Unable to analyze article content. Please try again later.</div>"
                }
        except Exception as e:
            print(f"Error analyzing article content: {e}")
            article_analysis = {
                "html": f"<div class='alert alert-danger'>Error analyzing article content: {str(e)}</div>"
            }
        
        # Analyze any IOCs found in the article
        ioc_analysis = []
        for ioc in iocs:
            try:
                report = ioc_analyzer.generate_report(ioc)
                html_report = ioc_analyzer.display_report(report)
                ioc_analysis.append({
                    'ioc': ioc,
                    'html_analysis': html_report,
                    'raw_analysis': report['ai_analysis']['analysis'],
                    'threat_data': report['threatfox_data']
                })
            except Exception as e:
                print(f"Error analyzing IOC {ioc}: {e}")
                ioc_analysis.append({
                    'ioc': ioc,
                    'error': str(e)
                })
        
        # Format the combined analysis as HTML
        html_output = []
        html_output.append("<div class='analysis-container'>")
        
        if article_analysis:
            html_output.append("<div class='article-analysis-section'>")
            html_output.append("<h4>Article Analysis</h4>")
            html_output.append(article_analysis['html'])
            html_output.append("</div>")
        
        if ioc_analysis:
            html_output.append("<div class='ioc-analysis-section'>")
            html_output.append("<h4>IOC Analysis</h4>")
            for analysis in ioc_analysis:
                if 'error' in analysis:
                    html_output.append(f"<div class='alert alert-warning'>Error analyzing {analysis['ioc']}: {analysis['error']}</div>")
                else:
                    html_output.append(analysis['html_analysis'])
            html_output.append("</div>")
        
        html_output.append("</div>")
        
        return JSONResponse({
            "html": "\n".join(html_output)
        })
        
    except Exception as e:
        print(f"Error in analyze_article endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 