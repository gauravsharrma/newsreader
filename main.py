from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import requests
import xml.etree.ElementTree as ET
import json
import os

app = FastAPI()

# Serve static HTML
app.mount("/static", StaticFiles(directory="static"), name="static")

RSS_FEED = "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
JSON_FILE = "news_data.json"

@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse("static/index.html")

@app.get("/fetch-news")
def fetch_news():
    resp = requests.get(RSS_FEED)
    root = ET.fromstring(resp.content)

    items = []
    for item in root.findall(".//item"):
        items.append({
            "title": item.findtext("title"),
            "link": item.findtext("link"),
            "description": item.findtext("description"),
            "pubDate": item.findtext("pubDate")
        })

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4, ensure_ascii=False)

    return {"message": f"Stored {len(items)} articles in {JSON_FILE}"}

@app.get("/get-news")
def get_news():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {"message": "No news found. Please click Fetch Latest News."}
