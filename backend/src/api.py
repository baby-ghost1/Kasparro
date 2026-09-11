import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.config import Config
from src.pipeline import run_pipeline

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Resume Screening API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_ROOT = PROJECT_ROOT
REPO_ROOT = PROJECT_ROOT.parent
STATIC_DIR = BACKEND_ROOT / "static"
FRONTEND_DIST = REPO_ROOT / "frontend" / "dist"


class ScreenRequest(BaseModel):
    input_dir: str = "./resumes"
    output_path: str = "./output/results.json"


class ScreenResponse(BaseModel):
    message: str
    total_resumes: int
    eligible: int
    rejected: int
    failed: int
    output_path: str


@app.get("/api")
def api_root():
    return {"status": "ok", "service": "AI Resume Screening API"}


@app.post("/api/screen", response_model=ScreenResponse)
def screen_resumes(request: ScreenRequest):
    try:
        config = Config()
        result = run_pipeline(request.input_dir, request.output_path, config)
        summary = result.batch_summary
        return ScreenResponse(
            message="Screening completed successfully",
            total_resumes=summary.total_resumes,
            eligible=summary.eligible,
            rejected=summary.rejected,
            failed=summary.failed,
            output_path=request.output_path,
        )
    except Exception as e:
        logger.error(f"Screening failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/results")
def get_results(output_path: str = "./output/results.json"):
    try:
        return FileResponse(output_path, media_type="application/json")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Results not found. Run /screen first.")


@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")

    if FRONTEND_DIST.exists():
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        index = FRONTEND_DIST / "index.html"
        if index.exists():
            return FileResponse(str(index))

    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "Frontend not built. Run 'npm run build' in frontend/ or use /api endpoints directly."}


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
