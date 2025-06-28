from fastapi import FastAPI
from endpoints import auth, news, fake_news
from tasks.background import scheduler, start_background_verification
from dotenv import load_dotenv
load_dotenv()
openapi_tags = [
    {
        "name": "News Aggregation and Personalization"    }
]

app = FastAPI(
    title="TrueShorts Backend",
    openapi_tags=openapi_tags
)
app.include_router(auth.router, tags=["News Aggregation and Personalization"])
app.include_router(news.router, tags=["News Aggregation and Personalization"])
app.include_router(fake_news.router, tags=["News Aggregation and Personalization"])

@app.on_event("startup")
async def startup_event():
    await start_background_verification()
