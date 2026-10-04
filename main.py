from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE = Path(__file__).parent
AUDIO = BASE / "assets" / "audio"
EXT = {".mp3", ".wav", ".m4a", ".flac"}

app = FastAPI(title="shelovesttute vault", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


def load_beats():
    files = sorted(p for p in AUDIO.glob("*") if p.suffix.lower() in EXT) if AUDIO.exists() else []
    return [
        {"n": f"{i:02d}", "file": p.name, "title": p.stem.replace("_", " ").replace("-", " ").upper()}
        for i, p in enumerate(files, 1)
    ]


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        name="index.html", context={"request": request, "beats": load_beats()}
    )


@app.get("/stream/{name}")
async def stream(name: str):
    path = (AUDIO / name).resolve()
    if AUDIO.resolve() not in path.parents or not path.is_file():
        raise HTTPException(404)
    return FileResponse(path, headers={"Content-Disposition": "inline", "Cache-Control": "private, no-store"})
