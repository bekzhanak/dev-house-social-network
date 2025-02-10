from fastapi import FastAPI, Depends, HTTPException, Path, Request, status
import models
from database import engine, Sessionlocal
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from routers import auth, posts
app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def test(request: Request):
    return RedirectResponse(url="/docs")

app.include_router(auth.router)
app.include_router(posts.router)
