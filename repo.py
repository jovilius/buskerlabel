import database

# gnerate a list of articles with id, title, content, date and image url
class FetchedStory:
    def __init__(self, id: int, published_at: str, fetched_at: str, url: str, title: str, content: str, image_url: str):
        self.id = id
        self.published_at = published_at
        self.fetched_at = fetched_at
        self.url = url
        self.title = title
        self.content = content        
        self.image_url = image_url
        
class ShortlistedStory:
    def __init__(self, id: int, published_at: str, url: str, title: str, summary: str, image_url: str): 
        self.id = id
        self.published_at = published_at
        self.url = url
        self.title = title
        self.summary = summary
        self.image_url = image_url

def initialize():

    print("Initializing the database...")
    connection = database.get_connection()

    # Create the 'fetched_stories' table
    database.create_table_if_not_exists(
        connection,
        "fetched_stories",
        {
            "id": "SERIAL PRIMARY KEY",
            "published_at": "TIMESTAMP NOT NULL",
            "fetched_at": "TIMESTAMP NOT NULL",
            "url": "VARCHAR(256) NOT NULL",
            "title": "TEXT NOT NULL",
            "content": "TEXT NOT NULL",
            "image_url": "VARCHAR(256) NOT NULL"
        }
    )    

    # Create the 'shortlisted_stories' table
    database.create_table_if_not_exists(  
        connection,      
        "shortlisted_stories",
        {
            "id": "INT PRIMARY KEY",  
            "published_at": "TIMESTAMP NOT NULL",
            "url": "VARCHAR(256) NOT NULL",  
            "title": "TEXT NOT NULL",
            "summary": "TEXT NOT NULL",
            "image_url": "VARCHAR(256) NOT NULL"            
        }
    )
    print("Database initialized.")

def add_fetched_stories(story):    
    database.insert(        
        "fetched_stories",
        FetchedStory,
        story,
        auto_increment=True
    )    

def find_fetched_stories():
    fetched_stories = database.select(        
        "fetched_stories", 
        FetchedStory,
    )
    return fetched_stories

def add_shortlisted_story(story):
    database.insert(        
        "shortlisted_stories",
        ShortlistedStory,
        story,
        auto_increment=False
    )

def find_shortlisted_stories():
    shortlisted_stories = database.select(        
        "shortlisted_stories", 
        ShortlistedStory
    )
    return shortlisted_stories

def add_demo_stories():
    fetched_stories = [
        (
            "2024-09-09 12:00:00",
            "2024-09-09 12:00:00",
            "https://www.google.com",
            "GoogleMX - The AI powerd music creation tool",
            "GogoMX is a music creation tool that uses AI to help you create music. It is a great tool for musicians and music producers.",
            "https://media.istockphoto.com/id/1085717468/es/foto/seminario-de-rob%C3%B3tica-en-el-%C3%A1mbito.jpg?s=1024x1024&w=is&k=20&c=30qW68ySJFiW4D4eNXoRkhKMRntiFlfkqikrVB0ByuU="
        ),
        (
            "2024-09-08 12:00:00",
            "2024-09-08 12:00:00",
            "https://www.google.com",
            "BandLab - The free music creation tool",
            "BandLab is a free music creation tool that allows you to create music online. It is a great tool for musicians and music producers.",
            "https://media.istockphoto.com/id/1495811235/es/foto/concepto-de-m%C3%BAsica-generado-por-ia-icono-de-notas-en-la-mano-humanoide-robot-sobre-fondo-azul.jpg?s=1024x1024&w=is&k=20&c=9-GHR5JAHb_wWrpPTljaDldD2a44AUoZHnjCbwq24Y4="
        )
    ]
    add_fetched_stories(fetched_stories)

    shortlisted_story = [
        (
            1,
            "2024-09-09 12:00:00",
            "https://www.google.com",
            "GoogleMX - The AI powerd music creation tool",
            "Exciting tool!",
            "https://media.istockphoto.com/id/1085717468/es/foto/seminario-de-rob%C3%B3tica-en-el-%C3%A1mbito.jpg?s=1024x1024&w=is&k=20&c=30qW68ySJFiW4D4eNXoRkhKMRntiFlfkqikrVB0ByuU="
        ),
        (
            2,
            "2024-09-08 12:00:00",
            "https://www.google.com",
            "BandLab - The free music creation tool",
            "Amazing tool!",
            "https://media.istockphoto.com/id/1495811235/es/foto/concepto-de-m%C3%BAsica-generado-por-ia-icono-de-notas-en-la-mano-humanoide-robot-sobre-fondo-azul.jpg?s=1024x1024&w=is&k=20&c=9-GHR5JAHb_wWrpPTljaDldD2a44AUoZHnjCbwq24Y4="
        )   
    ]
    add_shortlisted_story(shortlisted_story)

    print("Demo stories added.")
        