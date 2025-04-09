import requests
from bs4 import BeautifulSoup
import time
import datetime
from ioc_analyzer import IOCAnalyzer
from typing import List, Dict
import re

class CyberMonitor:
    def __init__(self):
        self.ioc_analyzer = IOCAnalyzer()
        self.article_url = 'https://www.newsnow.co.uk/h/Technology/Cyber+Security/Cyber+Attacks?type=ln'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }
        self.seen_articles = set()
        self.ioc_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b|\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b|\b[a-fA-F0-9]{32,}\b')

    def get_articles(self) -> List[Dict]:
        """Fetch articles from the news source"""
        response = requests.get(self.article_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article')
        return self._process_articles(articles)

    def _process_articles(self, articles: List) -> List[Dict]:
        """Process raw articles into structured data"""
        article_info = []
        for article in articles:
            title = article.find('a').text
            # Get the redirect page URL first
            redirect_url = article.find('a')['href']
            
            # Fetch the redirect page to get the real article URL
            try:
                redirect_response = requests.get(redirect_url, headers=self.headers)
                redirect_soup = BeautifulSoup(redirect_response.text, 'html.parser')
                
                # Try different possible locations for the real URL
                real_url = None
                
                # Try the retrieval message first
                retrieval_msg = redirect_soup.find('div', class_='retrieval-msg')
                if retrieval_msg and retrieval_msg.find('a'):
                    real_url = retrieval_msg.find('a')['href']
                
                # If not found, try the clickthrough button
                if not real_url:
                    clickthrough = redirect_soup.find('div', class_='clickthrough-dec__button')
                    if clickthrough and clickthrough.find('a'):
                        real_url = clickthrough.find('a')['href']
                
                # If still not found, try to find any link in the page
                if not real_url:
                    all_links = redirect_soup.find_all('a')
                    for link in all_links:
                        href = link.get('href', '')
                        if href and not href.startswith('javascript:') and not href.startswith('#'):
                            real_url = href
                            break
                
                # If we couldn't find a real URL, use the redirect URL
                if not real_url:
                    print(f"Could not find real article URL for: {title}")
                    real_url = redirect_url
                
            except Exception as e:
                print(f"Error getting real article URL for '{title}': {e}")
                real_url = redirect_url  # Fallback to the redirect URL if we can't get the real one
            
            timestamp = article.find('span', class_='article-publisher__timestamp')['data-timestamp']
            dt_object = datetime.datetime.fromtimestamp(int(timestamp))
            
            # Extract potential IOCs from the title
            potential_iocs = self._extract_iocs(title)
            
            article_info.append({
                'title': title,
                'link': real_url,  # Use the real article URL
                'time': dt_object,
                'potential_iocs': potential_iocs
            })
        return article_info

    def _extract_iocs(self, text: str) -> List[str]:
        """Extract potential IOCs from text"""
        return self.ioc_pattern.findall(text)

    def serialize_article(self, article: Dict) -> Dict:
        """Convert article data to JSON-serializable format."""
        return {
            'title': article['title'],
            'link': article['link'],
            'time': article['time'].isoformat() if isinstance(article['time'], datetime.datetime) else article['time'],
            'potential_iocs': article['potential_iocs']
        }

    def analyze_article(self, article: Dict) -> Dict:
        """Analyze an article and its potential IOCs"""
        analysis_results = []
        # Analyze any IOCs found in the article
        for ioc in article['potential_iocs']:
            try:
                report = self.ioc_analyzer.generate_report(ioc)
                # Get the HTML formatted report
                html_report = self.ioc_analyzer.display_report(report)
                analysis_results.append({
                    'ioc': ioc,
                    'html_analysis': html_report,
                    'raw_analysis': report['ai_analysis']['analysis'],
                    'threat_data': report['threatfox_data']
                })
            except Exception as e:
                analysis_results.append({
                    'ioc': ioc,
                    'error': str(e)
                })
        
        return {
            'ioc_analysis': analysis_results
        }

    def monitor_and_analyze(self, interval: int = 60):
        """Monitor for new articles and analyze them"""
        print("Starting cyber threat monitoring...")
        while True:
            try:
                articles = self.get_articles()
                for article in articles:
                    # Check if we've seen this article before
                    article_key = f"{article['title']}_{article['link']}"
                    if article_key not in self.seen_articles:
                        print(f"\nNew article detected: {article['title']}")
                        print(f"Published at: {article['time']}")
                        print(f"Link: {article['link']}")
                        
                        if article['potential_iocs']:
                            print("\nPotential IOCs found:")
                            for ioc in article['potential_iocs']:
                                print(f"- {ioc}")
                            
                            # Analyze the article
                            analysis = self.analyze_article(article)
                            print("\nAnalysis Results:")
                            for result in analysis['ioc_analysis']:
                                if 'error' in result:
                                    print(f"Error analyzing {result['ioc']}: {result['error']}")
                                else:
                                    print(f"\nAnalysis for {result['ioc']}:")
                                    print(result['html_analysis'])
                        
                        self.seen_articles.add(article_key)
                        print("\n" + "="*50)
                
                time.sleep(interval)
            except Exception as e:
                print(f"Error during monitoring: {str(e)}")
                time.sleep(interval)

if __name__ == "__main__":
    monitor = CyberMonitor()
    monitor.monitor_and_analyze() 