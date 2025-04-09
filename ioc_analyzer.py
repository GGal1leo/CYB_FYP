import os
import json
import requests
import google.generativeai as genai
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv
from stix2 import MemoryStore
from stix2 import Filter
import time

# Load environment variables
load_dotenv()

class IOCAnalyzer:
    def __init__(self):
        self.console = Console()
        self._setup_gemini()
        self._setup_mitre()
        
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
    
    def _setup_mitre(self):
        """Setup MITRE ATT&CK framework with local caching"""
        # Use absolute path for cache file
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
        cache_file = os.path.join(cache_dir, 'mitre_attack_cache.json')
        cache_age_days = 7  # Refresh cache after 7 days
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Check if cache file exists and is recent enough
        if os.path.exists(cache_file):
            file_age = (time.time() - os.path.getmtime(cache_file)) / (24 * 3600)  # age in days
            if file_age < cache_age_days:
                try:
                    with open(cache_file, 'r') as f:
                        self.attack_data = MemoryStore(stix_data=json.load(f))
                    return
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error reading cache file: {e}. Downloading fresh data...")
        
        # If cache doesn't exist, is too old, or is corrupted, download fresh data
        url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
        response = requests.get(url)
        data = response.json()
        
        # Save to cache file
        with open(cache_file, 'w') as f:
            json.dump(data, f)
        
        self.attack_data = MemoryStore(stix_data=data)
    
    def search_threatfox(self, ioc: str) -> Dict:
        """Search for IOC in ThreatFox database"""
        url = "https://threatfox-api.abuse.ch/api/v1/"
        payload = {
            "query": "search_ioc",
            "search_term": ioc
        }
        response = requests.post(url, json=payload)
        return response.json()
    
    def map_to_mitre(self, ioc_data: Dict) -> List[Dict]:
        """Map IOC data to relevant MITRE ATT&CK techniques"""
        matching_techniques = []
        
        # Get threat type and description from the IOC data
        threat_type = ioc_data.get('threat_type', '')
        threat_desc = ioc_data.get('threat_type_desc', '')
        malware = ioc_data.get('malware', '')
        
        # Define relevant tactics based on threat type
        relevant_tactics = {
            'botnet_cc': ['Initial Access', 'Command and Control', 'Persistence'],
            'payload_delivery': ['Initial Access', 'Execution'],
            'payload_hosting': ['Initial Access', 'Command and Control'],
            'malware_sample': ['Execution', 'Persistence', 'Defense Evasion'],
            'c2': ['Command and Control', 'Persistence'],
            'exploit': ['Initial Access', 'Execution', 'Privilege Escalation']
        }
        
        # Get all techniques
        techniques = self.attack_data.query([
            Filter("type", "=", "attack-pattern")
        ])
        
        # Search for matching techniques based on threat type and description
        for technique in techniques:
            # Check if technique matches any relevant tactics for this threat type
            technique_tactics = [phase.phase_name for phase in technique.kill_chain_phases]
            has_relevant_tactic = any(tactic in technique_tactics 
                                    for tactic in relevant_tactics.get(threat_type, []))
            
            # Check if technique description matches threat description or malware
            matches_description = (threat_desc.lower() in technique.description.lower() or
                                 malware.lower() in technique.description.lower())
            
            if has_relevant_tactic or matches_description:
                matching_techniques.append({
                    'id': technique.id,
                    'name': technique.name,
                    'description': technique.description,
                    'tactic': technique_tactics,
                    'url': f"https://attack.mitre.org/techniques/{technique.external_references[0].external_id}"
                })
        
        return matching_techniques

    def analyze_with_gemini(self, ioc_data: Dict) -> Dict:
        """Analyze IOC data using Gemini AI"""
        # Map the IOC data to MITRE techniques
        mitre_mapping = self.map_to_mitre(ioc_data)
        
        prompt = f"""
        Analyze this IOC data and provide a concise response with the following sections, each on a new line:
        1. Threat Level: [Low/Medium/High]
        2. Impact: [Brief description of potential impact]
        3. Recommended Actions: [List key actions]
        4. Related Threat Actors: [If any]
        5. Historical Context: [If available]
        
        IOC Data: {json.dumps(ioc_data, indent=2)}
        
        MITRE ATT&CK Mapping: {json.dumps(mitre_mapping, indent=2)}
        """
        
        response = self.model.generate_content(prompt)
        # Split the response into sections
        sections = {}
        current_section = None
        current_content = []
        
        for line in response.text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                if current_section:
                    sections[current_section] = ' '.join(current_content)
                current_section = line.split(':', 1)[0].strip()
                current_content = [line.split(':', 1)[1].strip()] if ':' in line else []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = ' '.join(current_content)
        
        return {
            "analysis": sections,
            "raw_data": ioc_data,
            "mitre_mapping": mitre_mapping
        }
    
    def generate_report(self, ioc: str) -> Dict:
        """Generate comprehensive IOC analysis report"""
        # Get data from ThreatFox
        threatfox_data = self.search_threatfox(ioc)
        
        # Analyze with Gemini AI
        ai_analysis = self.analyze_with_gemini(threatfox_data)
        
        return {
            "ioc": ioc,
            "threatfox_data": threatfox_data,
            "ai_analysis": ai_analysis
        }
    
    def display_report(self, report: Dict) -> str:
        """Display the analysis report in HTML format"""
        output = []
        output.append("<div class='report-container'>")
        
        # Basic IOC information
        output.append(f"<h2>IOC Analysis Report</h2>")
        output.append(f"<p><strong>IOC:</strong> {report['ioc']}</p>")
        
        # Analysis sections
        analysis = report["ai_analysis"]["analysis"]
        output.append("<div class='analysis-section'>")
        output.append(f"<p><strong>Threat Level:</strong> {analysis.get('1. Threat Level', 'Not available')}</p>")
        output.append(f"<p><strong>Impact:</strong> {analysis.get('2. Impact', 'Not available')}</p>")
        output.append(f"<p><strong>Recommended Actions:</strong> {analysis.get('3. Recommended Actions', 'Not available')}</p>")
        output.append(f"<p><strong>Related Threat Actors:</strong> {analysis.get('4. Related Threat Actors', 'Not available')}</p>")
        output.append(f"<p><strong>Historical Context:</strong> {analysis.get('5. Historical Context', 'Not available')}</p>")
        output.append("</div>")
        
        # MITRE ATT&CK techniques
        if report["ai_analysis"]["mitre_mapping"]:
            output.append("<div class='mitre-section'>")
            output.append("<h3>MITRE ATT&CK Techniques</h3>")
            for technique in report["ai_analysis"]["mitre_mapping"]:
                tactics_str = ", ".join(technique['tactic']) if isinstance(technique['tactic'], list) else str(technique['tactic'])
                output.append("<div class='technique'>")
                output.append(f"<p><strong>{technique['name']}</strong> ({technique['id']})</p>")
                output.append(f"<p><em>Tactic:</em> {tactics_str}</p>")
                output.append(f"<p><a href='{technique['url']}' target='_blank'>View on MITRE ATT&CK</a></p>")
                output.append("</div>")
            output.append("</div>")
        
        output.append("</div>")
        
        # Add some basic CSS styling
        output.append("""
        <style>
        .report-container {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .analysis-section {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .mitre-section {
            background-color: #e9f7fe;
            padding: 15px;
            border-radius: 5px;
        }
        .technique {
            margin-bottom: 15px;
            padding: 10px;
            background-color: white;
            border-radius: 3px;
        }
        h2, h3 {
            color: #333;
        }
        a {
            color: #0066cc;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        </style>
        """)
        
        return "\n".join(output)

    def analyze_article_content(self, content: str) -> Dict:
        """Analyze article content using Gemini AI"""
        prompt = f"""
        Analyze this cybersecurity article and provide a structured analysis with the following sections:
        1. Summary: [Brief overview of the article]
        2. Key Threats: [List of main threats discussed]
        3. Impact Assessment: [Potential impact of the threats]
        4. Recommendations: [Suggested actions or mitigations]
        5. Technical Details: [Any technical information worth noting]
        
        Article Content:
        {content[:8000]}  # Limit content length to avoid token limits
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Split the response into sections
            sections = {}
            current_section = None
            current_content = []
            
            for line in response.text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    if current_section:
                        sections[current_section] = ' '.join(current_content)
                    current_section = line.split(':', 1)[0].strip()
                    current_content = [line.split(':', 1)[1].strip()] if ':' in line else []
                elif current_section:
                    current_content.append(line)
            
            if current_section:
                sections[current_section] = ' '.join(current_content)
            
            return {
                "analysis": sections,
                "html": self._format_article_analysis_html(sections)
            }
        except Exception as e:
            print(f"Error analyzing article content: {e}")
            return None

    def _format_article_analysis_html(self, sections: Dict) -> str:
        """Format the article analysis as HTML"""
        html = []
        html.append("<div class='article-analysis'>")
        
        for section_num, section_title in [
            ("1.", "Summary"),
            ("2.", "Key Threats"),
            ("3.", "Impact Assessment"),
            ("4.", "Recommendations"),
            ("5.", "Technical Details")
        ]:
            if section_num in sections:
                html.append(f"<div class='analysis-section'>")
                html.append(f"<h3>{section_title}</h3>")
                html.append(f"<p>{sections[section_num]}</p>")
                html.append("</div>")
        
        html.append("</div>")
        
        # Add some basic CSS styling
        html.append("""
        <style>
        .article-analysis {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .analysis-section {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .analysis-section h3 {
            color: #2c3e50;
            margin-top: 0;
        }
        .analysis-section p {
            margin-bottom: 0;
            line-height: 1.6;
        }
        </style>
        """)
        
        return "\n".join(html)

if __name__ == "__main__":
    analyzer = IOCAnalyzer()
    ioc = input("Enter IOC to analyze: ")
    report = analyzer.generate_report(ioc)
    print(analyzer.display_report(report)) 