
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import Session
from db import Base, get_db, engine

class FetchedStory(Base):
    __tablename__ = "fetched_stories"  

    id = Column(Integer, primary_key=True, nullable=False)
    published_at = Column(TIMESTAMP, nullable=False)
    fetched_at = Column(TIMESTAMP, nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)        
    image_url = Column(String, nullable=False)

def add_fetched_story(db: Session, story: FetchedStory):    
    db.add(story)
    db.commit()

def find_fetched_stories(db: Session):
    return db.query(FetchedStory).all() 

def exists_fetched_story(db: Session, url: str) -> bool:
    return db.query(FetchedStory).filter(FetchedStory.url == url).first() is not None      

class ShortlistedStory(Base):   
    __tablename__ = "shortlisted_stories"  

    id = Column(Integer, primary_key=True, nullable=False)
    published_at = Column(TIMESTAMP, nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    image_url = Column(String, nullable=False)       

def add_shortlisted_story(db: Session, story: ShortlistedStory):
    db.add(story)
    db.commit()
   
def find_shortlisted_stories(db: Session):    
    return db.query(ShortlistedStory) \
            .order_by(ShortlistedStory.published_at.desc()) \
            .all()  

def add_demo_stories(db: Session):
    fetched_stories = [
        FetchedStory(
            id = 1,
            published_at = "2024-09-09 12:00:00",
            fetched_at = "2024-09-09 12:00:00",
            url = "https://www.google.com",
            title = "GoogleMX - The AI powerd music creation tool",
            content = "GogoMX is a music creation tool that uses AI to help you create music. It is a great tool for musicians and music producers.",
            image_url = "https://media.istockphoto.com/id/1085717468/es/foto/seminario-de-rob%C3%B3tica-en-el-%C3%A1mbito.jpg?s=1024x1024&w=is&k=20&c=30qW68ySJFiW4D4eNXoRkhKMRntiFlfkqikrVB0ByuU="
        ),
        FetchedStory(
            id = 2,
            published_at = "2024-09-08 12:00:00",
            fetched_at = "2024-09-08 12:00:00",
            url = "https://www.google.com",
            title = "BandLab - The free music creation tool",
            content = "BandLab is a free music creation tool that allows you to create music online. It is a great tool for musicians and music producers.",
            image_url = "https://media.istockphoto.com/id/1495811235/es/foto/concepto-de-m%C3%BAsica-generado-por-ia-icono-de-notas-en-la-mano-humanoide-robot-sobre-fondo-azul.jpg?s=1024x1024&w=is&k=20&c=9-GHR5JAHb_wWrpPTljaDldD2a44AUoZHnjCbwq24Y4="
        )
    ]
    for story in fetched_stories:
        add_fetched_story(db, story)

    shortlisted_stories = [
        ShortlistedStory(
            id = 1,
            published_at = "2024-09-09 12:00:00",
            url = "https://www.google.com",
            title = "GoogleMX - The AI powerd music creation tool",
            summary = "GogoMX is a music creation tool that uses AI to help you create music. It is a great tool for musicians and music producers.",
            image_url = "https://media.istockphoto.com/id/1085717468/es/foto/seminario-de-rob%C3%B3tica-en-el-%C3%A1mbito.jpg?s=1024x1024&w=is&k=20&c=30qW68ySJFiW4D4eNXoRkhKMRntiFlfkqikrVB0ByuU="
        ),
        ShortlistedStory(
            id = 2,
            published_at = "2024-09-08 12:00:00",
            url = "https://www.google.com",
            title = "BandLab - The free music creation tool",
            summary = "BandLab is a free music creation tool that allows you to create music online. It is a great tool for musicians and music producers.",
            image_url = "https://media.istockphoto.com/id/1495811235/es/foto/concepto-de-m%C3%BAsica-generado-por-ia-icono-de-notas-en-la-mano-humanoide-robot-sobre-fondo-azul.jpg?s=1024x1024&w=is&k=20&c=9-GHR5JAHb_wWrpPTljaDldD2a44AUoZHnjCbwq24Y4="
        )
    ]   

    for story in shortlisted_stories:
        add_shortlisted_story(db, story)

def inizialize_db():
    print("Initializing the database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")

if __name__ == '__main__':
    inizialize_db()
    db_ = next(get_db())
    print("Adding demo stories...")
    add_demo_stories(db_,)
    db_.close()
    print("Demo stories added.")
