import requests
import json
import google.generativeai as genai
import os
import sys


ai_api = "AIzaSyC_OQkjAiKUZQeMSLDYR7mxbxYwvfc4X_A"
genai.configure(api_key=ai_api)
model = genai.GenerativeModel("gemini-1.5-flash")
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
    response = model.generate_content(f"Summarise this data about an IOC into a pretty report: {json.dumps(result, indent=4, sort_keys=True)} use ** symbols to highlight the start of the important parts and ## symbols to highlight the end of the important parts")
    # prettify the ai response with colors
    #print(pygments.highlight(response, lexers.JsonLexer(), formatters.TerminalFormatter()))
    # color the elements between ** symbols
    response = response.text.replace("**", "\033[1;31m").replace("##", "\033[0m")
    print(response)


if __name__ == "__main__":
    main()
