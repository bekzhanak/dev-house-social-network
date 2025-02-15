from dotenv import load_dotenv
from fastapi import FastAPI, Request
import models
from database import engine
from fastapi.responses import RedirectResponse
from routers import auth, posts, profile, comments, likes, followers
load_dotenv()
app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.get("/")
def test(request: Request):
    return RedirectResponse(url="/docs")


app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(followers.router)
