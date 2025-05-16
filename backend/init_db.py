from database import engine, SessionLocal
from models import Base, Movie, Actor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_db():
    print("Database URL:", os.getenv("DATABASE_URL"))
    
    # Drop all tables and recreate them
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    # Create a new session
    db = SessionLocal()
    
    try:
        # Sample movies data
        movies_data = [
            {
                "title": "The Shawshank Redemption",
                "year": 1994,
                "director": "Frank Darabont",
                "actors": ["Tim Robbins", "Morgan Freeman"]
            },
            {
                "title": "The Godfather",
                "year": 1972,
                "director": "Francis Ford Coppola",
                "actors": ["Marlon Brando", "Al Pacino"]
            },
            {
                "title": "The Dark Knight",
                "year": 2008,
                "director": "Christopher Nolan",
                "actors": ["Christian Bale", "Heath Ledger"]
            },
            {
                "title": "Pulp Fiction",
                "year": 1994,
                "director": "Quentin Tarantino",
                "actors": ["John Travolta", "Samuel L. Jackson"]
            }
        ]
        
        print("Adding movies to database...")
        # Add movies and their actors
        for movie_data in movies_data:
            # Check if movie already exists
            existing_movie = db.query(Movie).filter(Movie.title == movie_data["title"]).first()
            if not existing_movie:
                movie = Movie(
                    title=movie_data["title"],
                    year=movie_data["year"],
                    director=movie_data["director"]
                )
                db.add(movie)
                db.flush()  # Flush to get the movie ID
                
                # Add actors
                for actor_name in movie_data["actors"]:
                    actor = Actor(actor_name=actor_name, movie_id=movie.id)
                    db.add(actor)
        
        # Commit the changes
        db.commit()
        print("Database initialized successfully with sample movies!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 