import repo
from db import get_db
from sqlalchemy.orm import Session

from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
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
    import time
    start = time.time()
    stories = repo.find_shortlisted_stories(db)
    end = time.time()
    print(f"Stories loaded in {end-start} seconds.")
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "stories": stories}
    )

@app.get("/info")
def read_info(request: Request):   
    return "This is buskerlabel.com"

@app.get("/crawl")
async def crawl(request: Request, db: Session = Depends(get_db)):  
    async def generate():   
        yield "Fetching ... \n"
        already_fetched_urls = [story.url for story in repo.find_fetched_stories(db)]
        fetched_stories = await crawler.crawl(set(already_fetched_urls))
        yield f"Fetched {len(fetched_stories)} stories.\n"
        yield "Adding new stories to database...\n"
        added = 0
        for fetched_story in fetched_stories:
            fetched_story = FetchedStory(**fetched_story)
            if not repo.exists_fetched_story(db, fetched_story.url):
                yield f"Adding story: {fetched_story.url} ...\n"
                repo.add_fetched_story(db, fetched_story)
                added += 1            
        yield f"Added {added} new stories to database.\n"
    return StreamingResponse(generate())

@app.get("/shortlist")
async def shortlist(request: Request, db: Session = Depends(get_db)):
    async def generate():
        fetched_stories = repo.find_unprocessed_fetched_stories(db)
        yield f"Analyzing {len(fetched_stories)} stories ...\n"
        for fetched_story in fetched_stories:
            yield f"Analyzing: {fetched_story.url} ...\n"
            yield f"Original content: {fetched_story.content}\n---\n"
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
                yield f"Shortlisted: {shortlisted_story.summary}\n"
            else:
                yield "Off-topic.\n---\n"
            repo.add_processed_story(db, repo.ProcessedStory(url=fetched_story.url, type="filter:ai,music;summary"))   
        yield "Analyzing completed.\n"
    return StreamingResponse(generate())

