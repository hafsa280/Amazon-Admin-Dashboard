from fastapi import FastAPI
from app import routes
from app.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(routes.router)