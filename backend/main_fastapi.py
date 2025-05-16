from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
import os

import models, schemas
from database import SessionLocal, engine
from langchain import PromptTemplate, LLMChain
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Create a movie + its actors
@app.post("/movies/", response_model=schemas.MoviePublic)
def create_movie(payload: schemas.MovieBase, db: Session = Depends(get_db)):
    movie = models.Movie(title=payload.title, year=payload.year, director=payload.director)
    db.add(movie)
    db.commit()        # ← commit so movie.id is assigned before creating actors
    db.refresh(movie)
    # It's necessary to commit first because Actors need movie.id (FK) to exist.
    db.bulk_save_objects([
        models.Actor(actor_name=a.actor_name, movie_id=movie.id)
        for a in payload.actors
    ])
    db.commit()
    db.refresh(movie)
    return movie

# 2. Get a random movie with its actors
@app.get("/movies/random/", response_model=schemas.MoviePublic)
def random_movie(db: Session = Depends(get_db)):
    movie = (
        db.query(models.Movie)
          .options(joinedload(models.Movie.actors))
          .order_by(func.random())
          .first()
    )
    if not movie:
        raise HTTPException(status_code=404, detail="No movies found")
    return movie
# — Difference lazy vs eager loading?
# Lazy loading defers fetching actors until accessed; eager (joinedload) does one SQL JOIN up-front.

# 3. Generate a summary via Groq
groq = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="mixtral-8x7b-32768"  # or "llama2-70b-4096" depending on your needs
)
prompt = PromptTemplate(
    input_variables=["title","year","director","actors"],
    template="Generate a short, engaging summary for the movie '{title}' ({year}), directed by {director} and starring {actors}."
)
chain = LLMChain(llm=groq, prompt=prompt)

@app.post("/generate_summary/", response_model=schemas.SummaryResponse)
def generate_summary(req: schemas.SummaryRequest, db: Session = Depends(get_db)):
    movie = (
        db.query(models.Movie)
          .options(joinedload(models.Movie.actors))
          .filter(models.Movie.id == req.movie_id)
          .first()
    )
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    # Format actor list into comma-separated string
    actor_list = ", ".join(actor.actor_name for actor in movie.actors)
    summary = chain.run(
        title=movie.title,
        year=str(movie.year),
        director=movie.director,
        actors=actor_list
    )
    return {"summary_text": summary}
# — To format actors: join their .actor_name with commas into a single string.
