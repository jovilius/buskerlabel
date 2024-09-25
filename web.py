import repo
from db import get_db
from sqlalchemy.orm import Session

from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import crawler

app = FastAPI()

# Serve static files (like CSS, JavaScript, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(request: Request, db: Session = Depends(get_db)):
    stories = repo.find_shortlisted_stories(db)
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "stories": stories}
    )

@app.get("/info")
def read_info(request: Request):   
    return "This is buskerlabel.com"

@app.get("/crawl")
async def crawl(request: Request, db: Session = Depends(get_db)):     
    print("Crawling...")
    fetched_stories = await crawler.main()
    print(f"Fetched {len(fetched_stories)} stories.")
    print("Saving to database...")
    added = 0
    for fetched_story in fetched_stories:
        fetched_story = repo.FetchedStory(**fetched_story)
        if not repo.exists_fetched_story(db, fetched_story.url):
            repo.add_fetched_story(db, fetched_story)
            added += 1
    print(f"Saved {added} stories to database.")
    return {"message": "Crawling completed."}

