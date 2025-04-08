import os
import json
import requests
import google.generativeai as genai
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class IOCAnalyzer:
    def __init__(self):
        self.console = Console()
        self._setup_gemini()
        
    def _setup_gemini(self):
        """Configure Gemini AI with appropriate safety settings"""
        ai_api = os.getenv("AI_API")
        if not ai_api:
            raise ValueError("AI_API environment variable not set")
            
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
        
        genai.configure(api_key=ai_api)
        self.model = genai.GenerativeModel("gemini-2.0-flash", safety_settings=safety_settings)
    
    def search_threatfox(self, ioc: str) -> Dict:
        """Search for IOC in ThreatFox database"""
        url = "https://threatfox-api.abuse.ch/api/v1/"
        payload = {
            "query": "search_ioc",
            "search_term": ioc
        }
        response = requests.post(url, json=payload)
        return response.json()
    
    def get_mitre_techniques(self) -> Dict:
        """Fetch MITRE ATT&CK techniques from the API"""
        url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
        response = requests.get(url)
        return response.json()
    
    def analyze_with_gemini(self, ioc_data: Dict, mitre_data: Dict) -> Dict:
        """Analyze IOC data using Gemini AI"""
        prompt = f"""
        Analyze this IOC data and provide:
        1. Threat level assessment
        2. Potential impact
        3. Recommended actions
        4. Related threat actors
        5. Historical context
        6. MITRE ATT&CK techniques that might be relevant
        
        IOC Data: {json.dumps(ioc_data, indent=2)}
        
        MITRE ATT&CK Techniques: {json.dumps(mitre_data, indent=2)}
        """
        
        response = self.model.generate_content(prompt)
        return {
            "analysis": response.text,
            "raw_data": ioc_data
        }
    
    def generate_report(self, ioc: str) -> Dict:
        """Generate comprehensive IOC analysis report"""
        # Get data from ThreatFox
        threatfox_data = self.search_threatfox(ioc)
        
        # Get MITRE ATT&CK data
        mitre_data = self.get_mitre_techniques()
        
        # Analyze with Gemini AI
        ai_analysis = self.analyze_with_gemini(threatfox_data, mitre_data)
        
        return {
            "ioc": ioc,
            "threatfox_data": threatfox_data,
            "ai_analysis": ai_analysis
        }
    
    def display_report(self, report: Dict):
        """Display the analysis report in a formatted table"""
        table = Table(title="IOC Analysis Report")
        
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("IOC", report["ioc"])
        table.add_row("Threat Level", report["ai_analysis"]["analysis"].split("\n")[0])
        table.add_row("Impact", report["ai_analysis"]["analysis"].split("\n")[1])
        
        self.console.print(table)

if __name__ == "__main__":
    analyzer = IOCAnalyzer()
    ioc = input("Enter IOC to analyze: ")
    report = analyzer.generate_report(ioc)
    analyzer.display_report(report) 