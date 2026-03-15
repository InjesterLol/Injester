from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes import router
from app.ws import router as ws_router

app = FastAPI(title="injester.lol", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.include_router(ws_router)

# Serve generated optimized HTML pages
generated_dir = Path(__file__).parent.parent / "generated"
generated_dir.mkdir(exist_ok=True)
app.mount("/generated", StaticFiles(directory=str(generated_dir), html=True), name="generated")


@app.get("/health")
def health():
    return {"status": "ok"}
