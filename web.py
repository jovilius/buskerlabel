import repo
from db import get_db
from sqlalchemy.orm import Session

from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import crawler
import summarizer

from repo import ShortlistedStory, FetchedStory

app = FastAPI()

# Serve static files (like CSS, JavaScript, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

#repo.initialize_db()

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
        fetched_story = FetchedStory(**fetched_story)
        if not repo.exists_fetched_story(db, fetched_story.url):
            print(f"Adding story: {fetched_story.url}")
            repo.add_fetched_story(db, fetched_story)
            added += 1
        else:
            print(f"Story already exists: {fetched_story.url}")
    print(f"Saved {added} stories to database.")
    return {"message": "Crawling completed."}

@app.get("/shortlist")
async def shortlist(request: Request, db: Session = Depends(get_db)):
    fetched_stories = repo.find_fetched_stories(db)
    print(f"Processing {len(fetched_stories)} stories...")

    for fetched_story in fetched_stories:
        if not repo.exists_processed_story(db, fetched_story.url):
            print(f"Analyzing: {fetched_story.url} ...")
            print(f"Original content: {fetched_story.content}")
            result = summarizer.filter_and_summarize_ai_music(
                fetched_story.content
            )
            on_topic = result['check'].lower() == "yes"
            
            if on_topic:
                summary = result['summary']
                story = {
                    "published_at": fetched_story.published_at,
                    "url": fetched_story.url,
                    "title": fetched_story.title,
                    "summary": summary,                
                    "image_url": fetched_story.image_url,
                }
                shortlisted_story = ShortlistedStory(**story)
                repo.add_shortlisted_story(db, shortlisted_story)
                print(f"Shortlisted: {shortlisted_story.summary}") 
            else:
                print("Off-topic.")

            repo.add_processed_story(db, repo.ProcessedStory(url=fetched_story.url, type="filter:ai,music;summary"))   
        else:
            print(f"Skipped: {fetched_story.url}")
        
    print("Processing completed.")
 
    return {"message": "Shortlisting completed."}

