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
import subprocess
import re

# Create necessary directories
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Store recent articles and analyses
recent_articles = []
active_connections = set()

# Demo article that will always be at the bottom
DEMO_ARTICLE = {
    'title': 'Demo: Critical Security Vulnerability Found in Popular Software',
    'link': 'https://blog.sekoia.io/tycoon-2fa-an-in-depth-analysis-of-the-latest-version-of-the-aitm-phishing-kit/',
    'time': datetime.now().isoformat(),
    'potential_iocs': ['www.normanwaddell.com']
}

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
    # Add demo article to recent_articles if it's not already there
    demo_article_key = f"{DEMO_ARTICLE['title']}_{DEMO_ARTICLE['link']}"
    if not any(article['article']['title'] == DEMO_ARTICLE['title'] for article in recent_articles):
        analysis = monitor.analyze_article(DEMO_ARTICLE)
        recent_articles.insert(0, {
            'article': monitor.serialize_article(DEMO_ARTICLE),
            'analysis': analysis
        })
        monitor.seen_articles.add(demo_article_key)
    
    while True:
        print("Fetching Articles")
        try:
            articles = monitor.get_articles()
            for article in articles:
                # Check if we've seen this article before
                article_key = f"{article['title']}_{article['link']}"
                # print(f"Article key: {article_key}")
                if article_key not in monitor.seen_articles:
                    # Process and analyze the article
                    analysis = monitor.analyze_article(article)
                    
                    # Add to recent articles (after the demo article)
                    recent_articles.append({
                        'article': monitor.serialize_article(article),
                        'analysis': analysis
                    })
                    if len(recent_articles) > 51:  # Keep last 50 articles + demo article
                        recent_articles.pop(1)  # Remove the oldest non-demo article
                    
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
        print("Fetching new articles")
        await asyncio.sleep(600)  # Check every minute

print("Done Awaiting")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global monitor, ioc_analyzer
    print("Initialising CyberMonitor")
    monitor = CyberMonitor()
    print("Initialising IOCAnalyzer")
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

@app.get("/recent_iocs")
async def get_recent_iocs():
    """Fetch recent IOCs from ThreatFox API."""
    try:
        # Make request to ThreatFox API
        response = requests.post(
            'https://threatfox-api.abuse.ch/api/v1/',
            json={
                "query": "get_iocs",
                "days": 1
            }
        )
        
        # Check if request was successful
        if response.status_code != 200:
            return JSONResponse(
                status_code=500,
                content={"error": f'ThreatFox API returned status code {response.status_code}'}
            )
        
        # Parse response
        data = response.json()
        
        # Check query status
        if data.get('query_status') != 'ok':
            return JSONResponse(
                status_code=500,
                content={"error": 'ThreatFox API query failed'}
            )
        
        # Get the IOCs data and limit to last 10
        iocs_data = data.get('data', [])
        limited_iocs = iocs_data[0:10] if len(iocs_data) > 10 else iocs_data
        
        # Return the limited IOCs data
        return JSONResponse({
            "data": limited_iocs
        })
        
    except requests.exceptions.RequestException as e:
        return JSONResponse(
            status_code=500,
            content={"error": f'Failed to fetch data from ThreatFox API: {str(e)}'}
        )
    except json.JSONDecodeError as e:
        return JSONResponse(
            status_code=500,
            content={"error": f'Failed to parse ThreatFox API response: {str(e)}'}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f'An unexpected error occurred: {str(e)}'}
        )

def check_pcap_for_ioc(ioc):
    """Check if an IOC is present in the PCAP file."""
    try:
        # Get the PCAP file from the root directory
        pcap_file = None
        for file in os.listdir('.'):
            if file.endswith('.pcapng'):
                pcap_file = file
                break
        
        if not pcap_file:
            return {
                'found': False,
                'details': 'No PCAP file found in the root directory.'
            }
        
        # magician agic
        search_ioc = ioc.replace('www.', '')
        
        # search for the IOC in the network
        cmd = ['tshark', '-r', pcap_file, '-Y', f'frame contains "{search_ioc}"']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            return {
                'found': True,
                'details': f'IOC found in {pcap_file}. Matches found in packet(s):\n{result.stdout.strip().replace(search_ioc, f"<strong>{search_ioc}</strong>")}'
            }
        else:
            return {
                'found': False,
                'details': f'IOC not found in {pcap_file}.'
            }
            
    except Exception as e:
        return {
            'found': False,
            'details': f'Error analyzing PCAP: {str(e)}'
        }

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
        
        report = ioc_analyzer.generate_report(ioc)
        
        pcap_data = check_pcap_for_ioc(ioc)
        
        html_report = ioc_analyzer.display_report(report)
        
        # HTML for PCAP analysis
        pcap_html = f"""
        <div class="pcap-analysis {pcap_data['found'] and 'found' or 'not-found'}">
            <i class="fas {pcap_data['found'] and 'fa-exclamation-triangle' or 'fa-check-circle'} pcap-icon"></i>
            {pcap_data['found'] and f'This IOC (<strong>{ioc}</strong>) was found in the PCAP file!' or f'This IOC (<strong>{ioc}</strong>) was not found in the PCAP file.'}
            <div class="mt-2">{pcap_data['details'].replace(ioc, f'<strong>{ioc}</strong>')}</div>
        </div>
        """
        
        combined_html = f"{html_report}{pcap_html}"
        
        return JSONResponse({
            "html": combined_html,
            "raw_data": {
                "ioc": ioc,
                "analysis": report['ai_analysis']['analysis'],
                "threat_data": report['threatfox_data'],
                "pcap_data": pcap_data
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
            
            # Get IOCs from the article's potential_iocs if it's the demo article
            if title == DEMO_ARTICLE['title'] and link == DEMO_ARTICLE['link']:
                print("Processing demo article IOCs")
                iocs.extend(DEMO_ARTICLE['potential_iocs'])
            
            # Remove duplicates while preserving order
            iocs = list(dict.fromkeys(iocs))
            print(f"Total IOCs to analyze: {iocs}")
            
        except Exception as e:
            print(f"Error analyzing article content: {e}")
            article_analysis = {
                "html": f"<div class='alert alert-danger'>Error analyzing article content: {str(e)}</div>"
            }
        
        # Analyze any IOCs found in the article
        ioc_analysis = []
        for ioc in iocs:
            try:
                print(f"Analyzing IOC: {ioc}")
                report = ioc_analyzer.generate_report(ioc)
                html_report = ioc_analyzer.display_report(report)
                
                # Check PCAP for the IOC
                pcap_data = check_pcap_for_ioc(ioc)
                
                # Create PCAP analysis HTML
                pcap_html = f"""
                <div class="pcap-analysis {pcap_data['found'] and 'found' or 'not-found'}">
                    <i class="fas {pcap_data['found'] and 'fa-exclamation-triangle' or 'fa-check-circle'} pcap-icon"></i>
                    {pcap_data['found'] and f'This IOC (<strong>{ioc}</strong>) was found in the PCAP file!' or f'This IOC (<strong>{ioc}</strong>) was not found in the PCAP file.'}
                    <div class="mt-2">{pcap_data['details'].replace(ioc, f'<strong>{ioc}</strong>')}</div>
                </div>
                """
                
                # Get top 3 MITRE techniques
                # mitre_techniques = report['ai_analysis'].get('mitre_mapping', [])
                # if mitre_techniques:
                #     top_3_mitre = mitre_techniques[:3]
                #     mitre_html = """
                #     <div class="mitre-section mt-3">
                #         <h5>Top 3 MITRE ATT&CK Techniques</h5>
                #         <ul class="list-group">
                #     """
                #     for technique in top_3_mitre:
                #         mitre_html += f"""
                #             <li class="list-group-item">
                #                 <strong>{technique.get('name', 'Unknown')}</strong>
                #                 <br>
                #                 <small class="text-muted">{technique.get('description', 'No description available')}</small>
                #             </li>
                #         """
                #     mitre_html += """
                #         </ul>
                #     </div>
                #     """
                # else:
                #     mitre_html = """
                #     <div class="mitre-section mt-3">
                #         <h5>MITRE ATT&CK Techniques</h5>
                #         <div class="alert alert-info">No MITRE techniques available</div>
                #     </div>
                #     """
                
                # Combine all sections
                html_report = f"{html_report}{pcap_html}"
                
                ioc_analysis.append({
                    'ioc': ioc,
                    'html_analysis': html_report,
                    'raw_analysis': report['ai_analysis']['analysis'],
                    'threat_data': report['threatfox_data'],
                    'pcap_data': pcap_data
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
            html_output.append(f"<p>Found {len(ioc_analysis)} potential IOCs in the article:</p>")
            for analysis in ioc_analysis:
                if 'error' in analysis:
                    html_output.append(f"<div class='alert alert-warning'>Error analyzing {analysis['ioc']}: {analysis['error']}</div>")
                else:
                    html_output.append(analysis['html_analysis'])
            html_output.append("</div>")
        
        html_output.append("</div>")
        
        return JSONResponse({
            "html": "".join(html_output)
        })
        
    except Exception as e:
        print(f"Error in analyze_article endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 
