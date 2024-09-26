from sqlalchemy import Column, Integer, String, TIMESTAMP, func
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

def find_unprocessed_fetched_stories(db: Session):
    return db.query(FetchedStory) \
        .filter(~FetchedStory.url.in_(
            db.query(ProcessedStory.url)
        )) \
        .all()

class ProcessedStory(Base):
    __tablename__ = "processed_stories"  

    id = Column(Integer, primary_key=True, nullable=False)
    url = Column(String, nullable=False)
    processed_at = Column(TIMESTAMP, nullable=False, default=func.now())    
    type = Column(String, nullable=False)
    
def add_processed_story(db: Session, story: ProcessedStory):
    db.add(story)
    db.commit()

def exists_processed_story(db: Session, url: str) -> bool:
    return db.query(ProcessedStory).filter(ProcessedStory.url == url).first() is not None

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

def initialize_db():
    print("Initializing the database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")

if __name__ == '__main__':
    initialize_db()
   
