from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import routes
from app.db.database import create_db_and_tables

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# CORS (Allow Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, update for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "Welcome to Note Beautifier API"}

app.include_router(routes.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
