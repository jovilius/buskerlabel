import asyncio
from typing import Union
import os

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import crawler

app = FastAPI()

# Serve static files (like CSS, JavaScript, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

# gnerate a list of articles with id, title, content, date and image url
class article:
    def __init__(self, id: int, title: str, content: str, date: str, image: str, url: str):
        self.id = id
        self.title = title
        self.content = content
        self.date = date
        self.image = image
        self.url = url


@app.get("/")
def read_root(request: Request):

    articles = [
        article(
            id=1,
            title="GoogleMX - The AI powerd music creation tool",
            content="GogoMX is a music creation tool that uses AI to help you create music. It is a great tool for musicians and music producers.",
            date="9 Sep 2024",
            image="https://media.istockphoto.com/id/1085717468/es/foto/seminario-de-rob%C3%B3tica-en-el-%C3%A1mbito.jpg?s=1024x1024&w=is&k=20&c=30qW68ySJFiW4D4eNXoRkhKMRntiFlfkqikrVB0ByuU=",
            url="https://www.google.com"
        ),
        article(
            id=2,
            title="BandLab - The free music creation tool",
            content="BandLab is a free music creation tool that allows you to create music online. It is a great tool for musicians and music producers.",
            date="8 Sep 2024",
            image="https://media.istockphoto.com/id/1495811235/es/foto/concepto-de-m%C3%BAsica-generado-por-ia-icono-de-notas-en-la-mano-humanoide-robot-sobre-fondo-azul.jpg?s=1024x1024&w=is&k=20&c=9-GHR5JAHb_wWrpPTljaDldD2a44AUoZHnjCbwq24Y4=",
            url="https://www.google.com"
        ),
        article(
            id=3,
            title="JammAI - where music meets AI",
            content="JammAI is a music creation tool that uses AI to help you create music. It is a great tool for musicians and music producers.",
            date="7 Sep 2024",
            image="https://media.istockphoto.com/id/1300745934/es/foto/transformaci%C3%B3n-digital-mezcla-de-m%C3%BAsica-disc-jockey.jpg?s=1024x1024&w=is&k=20&c=iEcnf1BRri7LThcYrNlOXwJGkIp_IXlVqGeu7YZRqlw=",
            url="https://www.google.com"
        )
    ]

    print(articles)

    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "articles": articles}
    )

@app.get("/info")
def read_info(request: Request):   
    return "This is buskerlabel.com"

@app.put("/crawl")
async def crawl(request: Request):     
    await crawler.main()
    return {"message": "Crawling completed."}

