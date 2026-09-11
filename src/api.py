import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.config import Config
from src.pipeline import run_pipeline

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Resume Screening API", version="1.0.0")


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


@app.get("/")
def root():
    return {"status": "ok", "service": "AI Resume Screening API"}


@app.post("/screen", response_model=ScreenResponse)
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


@app.get("/results")
def get_results(output_path: str = "./output/results.json"):
    try:
        return FileResponse(output_path, media_type="application/json")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Results not found. Run /screen first.")
