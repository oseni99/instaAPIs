from fastapi import FastAPI 
from .database import Base, engine
from .api import router


app = FastAPI(
  title="Social Media App",
  description="Engine behind a social media",
  version="0.1"
  )

Base.metadata.create_all(bind=engine)


@app.get("/")
async def homepage():
    return {
        "details":"Homepage Success"
        }

app.include_router(router)
