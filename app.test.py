import os
import json
import requests
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('monitor.html')

@app.route('/recent_iocs')
def recent_iocs():
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
            return jsonify({
                'error': f'ThreatFox API returned status code {response.status_code}'
            }), 500
        
        # Parse response
        data = response.json()
        
        # Check query status
        if data.get('query_status') != 'ok':
            return jsonify({
                'error': 'ThreatFox API query failed'
            }), 500
        
        # Return the IOCs data
        return jsonify({
            'data': data.get('data', [])
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Failed to fetch data from ThreatFox API: {str(e)}'
        }), 500
    except json.JSONDecodeError as e:
        return jsonify({
            'error': f'Failed to parse ThreatFox API response: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'An unexpected error occurred: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 