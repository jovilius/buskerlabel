import asyncio
from typing import Union
import os
import repo

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import crawler

repo.initialize()
#repo.add_demo_stories()

app = FastAPI()

# Serve static files (like CSS, JavaScript, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(request: Request):
    stories = repo.find_shortlisted_stories()
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "stories": stories}
    )

@app.get("/info")
def read_info(request: Request):   
    return "This is buskerlabel.com"

@app.put("/crawl")
async def crawl(request: Request):     
    await crawler.main()
    return {"message": "Crawling completed."}

