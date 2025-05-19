from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import os

app = FastAPI()

# Serve frontend
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
        title = item.findtext("title")
        link = item.findtext("link")
        description = item.findtext("description")
        pubDate = item.findtext("pubDate")
        content = extract_article_content(link)

        items.append({
            "title": title,
            "link": link,
            "description": description,
            "pubDate": pubDate,
            "content": content
        })

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4, ensure_ascii=False)

    return {"message": f"Stored {len(items)} articles with full content."}

@app.get("/get-news")
def get_news():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {"message": "No news found. Please click Fetch Latest News."}

def extract_article_content(url):
    try:
        # Use public proxy to bypass CORS and JS rendering
        proxy_url = "https://api.codetabs.com/v1/proxy/?quest=" + url
        response = requests.get(proxy_url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        main_div = soup.select_one("div._s30J.clearfix")
        if main_div:
            for img in main_div.find_all("img"):
                img.decompose()
            return main_div.get_text(separator="\n", strip=True)
        else:
            return "[Content not found]"
    except Exception as e:
        return f"[Error fetching content: {e}]"
