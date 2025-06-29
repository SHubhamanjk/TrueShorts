from fastapi import FastAPI, Request
from endpoints import auth, news, fake_news
from tasks.background import scheduler, start_background_verification
from dotenv import load_dotenv
from utils.database import update_last_active
load_dotenv()
openapi_tags = [
    {
        "name": "News Aggregation and Personalization"    }
]

app = FastAPI(
    title="TrueShorts Backend",
    openapi_tags=openapi_tags
)

@app.middleware("http")
async def update_heartbeat_middleware(request: Request, call_next):
    update_last_active()
    response = await call_next(request)
    return response

app.include_router(auth.router, tags=["News Aggregation and Personalization"])
app.include_router(news.router, tags=["News Aggregation and Personalization"])
app.include_router(fake_news.router, tags=["News Aggregation and Personalization"])

@app.on_event("startup")
async def startup_event():
    await start_background_verification()
