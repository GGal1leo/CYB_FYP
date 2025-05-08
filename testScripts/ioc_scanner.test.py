import requests
import json
import google.generativeai as genai
import os
import sys


ai_api = os.getenv("AI_API")

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
        }, 
]

genai.configure(api_key=ai_api)
model = genai.GenerativeModel("gemini-1.5-flash", safety_settings=safety_settings)
# curl -X POST https://threatfox-api.abuse.ch/api/v1/ -d '{ "query": "search_ioc", "search_term": "139.180.203.104" }'
def search_ioc(ioc):
    url = "https://threatfox-api.abuse.ch/api/v1/"
    payload = {
        "query": "search_ioc",
        "search_term": ioc
    }
    response = requests.post(url, json=payload)
    return response.json()


def main():
    ioc = sys.argv[1]
    print(f"Searching for IOC: {ioc}")
    result = search_ioc(ioc)
    #print(result)
    # pretty print the json response and colourise it
    import pygments
    from pygments import lexers, formatters
    print(pygments.highlight(json.dumps(result, indent=4, sort_keys=True), lexers.JsonLexer(), formatters.TerminalFormatter()))
    #print(json.dumps(result, indent=4, sort_keys=True))
    response = model.generate_content(f"Summarise this data about an IOC into a pretty report: {json.dumps(result, indent=4, sort_keys=True)} use html tags to format the output")
    # prettify the ai response with colors
    #print(pygments.highlight(response, lexers.JsonLexer(), formatters.TerminalFormatter()))
    # color the elements between ** symbols
    with open("report.html", "w") as f:
        f.write(response.text)


if __name__ == "__main__":
    main()
