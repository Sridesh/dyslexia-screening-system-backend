from fastapi import FastAPI
from app.db.database import Base, engine
from app.core.config import settings
from app.api.v1 import api_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"Hello": "World"}
