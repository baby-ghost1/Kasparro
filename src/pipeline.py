import json
import time
import asyncio
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.config import Config
from src.models import CandidateResult, ScreeningResult, BatchSummary, GitHubEnrichment
from src.ingestion.file_discovery import discover_resumes
from src.ingestion.pdf_parser import extract_text_from_pdf
from src.ingestion.docx_parser import extract_text_from_docx
from src.extraction.extractor import extract_candidate_info
from src.screening.eligibility import check_eligibility
from src.screening.scorer import score_candidate, _generate_strengths_concerns, _generate_project_summary
from src.enrichment.github_enricher import enrich_github

logger = logging.getLogger(__name__)

MAX_WORKERS = 8


def _extract_text(filepath: str) -> str:
    ext = Path(filepath).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext == ".docx":
        return extract_text_from_docx(filepath)
    elif ext == ".txt":
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def process_single_resume(
    filename: str,
    filepath: str,
    config: Config,
) -> CandidateResult:
    result = CandidateResult(filename=filename)

    try:
        raw_text = _extract_text(filepath)
        if not raw_text.strip():
            result.parsing_error = "Empty or unreadable file"
            logger.warning(f"Empty text from {filename}")
            return result
    except Exception as e:
        result.parsing_error = f"Parsing failed: {str(e)}"
        logger.error(f"Failed to parse {filename}: {e}")
        return result

    try:
        info = extract_candidate_info(raw_text, filename)
        result.candidate_name = info.name
        result.matched_skills = info.skills[:20]
    except Exception as e:
        result.parsing_error = f"Information extraction failed: {str(e)}"
        logger.error(f"Failed to extract info from {filename}: {e}")
        return result

    try:
        eligibility = check_eligibility(info)
    except Exception as e:
        result.parsing_error = f"Eligibility check failed: {str(e)}"
        logger.error(f"Eligibility check failed for {filename}: {e}")
        return result

    result.eligible = eligibility.eligible
    result.rejection_reasons = eligibility.rejection_reasons
    result.matched_skills = eligibility.matched_skills

    if not eligibility.eligible:
        result.total_score = 0
        return result

    github_enrichment = GitHubEnrichment()
    github_score = 0
    github_summary = ""
    try:
        github_enrichment = enrich_github(info.github_url, config)
        github_score = github_enrichment.total_score
        github_summary = github_enrichment.summary
        result.github_enrichment = github_enrichment
        result.github_summary = github_summary
    except Exception as e:
        logger.warning(f"GitHub enrichment failed for {filename}: {e}")
        result.github_enrichment = GitHubEnrichment(
            has_github=bool(info.github_url),
            profile_url=info.github_url,
            summary=f"GitHub enrichment failed: {str(e)}",
            error=str(e),
        )

    try:
        breakdown = score_candidate(info, eligibility, github_score, github_summary, config)
        result.score_breakdown = breakdown
        result.total_score = breakdown.total
    except Exception as e:
        logger.error(f"Scoring failed for {filename}: {e}")
        result.parsing_error = f"Scoring failed: {str(e)}"
        return result

    result.project_summary = _generate_project_summary(info, eligibility.ai_evidence)
    strengths, concerns = _generate_strengths_concerns(info, eligibility.ai_evidence, result.score_breakdown)
    result.strengths = strengths
    result.concerns = concerns

    return result


def run_pipeline(input_dir: str, output_path: str, config: Config | None = None) -> ScreeningResult:
    if config is None:
        config = Config()

    start_time = time.time()
    logger.info(f"Starting screening pipeline: input={input_dir}, output={output_path}")

    files = discover_resumes(input_dir)
    if not files:
        logger.error("No resume files found")
        return ScreeningResult(batch_summary=BatchSummary(total_resumes=0))

    screening_result = ScreeningResult()
    batch_summary = BatchSummary(total_resumes=len(files))

    results_map: dict[str, CandidateResult] = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_file = {
            executor.submit(process_single_resume, f["filename"], f["path"], config): f["filename"]
            for f in files
        }
        for future in as_completed(future_to_file):
            filename = future_to_file[future]
            try:
                candidate_result = future.result()
            except Exception as e:
                logger.error(f"Unexpected error processing {filename}: {e}")
                candidate_result = CandidateResult(
                    filename=filename,
                    parsing_error=f"Unexpected error: {str(e)}",
                )
            results_map[filename] = candidate_result

    for file_info in files:
        candidate_result = results_map[file_info["filename"]]
        if candidate_result.parsing_error and not candidate_result.candidate_name:
            batch_summary.failed += 1
            screening_result.failed.append(candidate_result)
        elif candidate_result.eligible:
            batch_summary.successfully_parsed += 1
            batch_summary.eligible += 1
            screening_result.candidates.append(candidate_result)
        else:
            batch_summary.successfully_parsed += 1
            batch_summary.rejected += 1
            screening_result.rejected.append(candidate_result)

    screening_result.candidates.sort(key=lambda c: c.total_score, reverse=True)
    for i, candidate in enumerate(screening_result.candidates, 1):
        candidate.rank = i

    screening_result.batch_summary = batch_summary

    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        "batch_summary": batch_summary.model_dump(),
        "eligible_candidates": [c.model_dump() for c in screening_result.candidates],
        "rejected_candidates": [c.model_dump() for c in screening_result.rejected],
        "failed_candidates": [c.model_dump() for c in screening_result.failed],
    }

    with open(output_path_obj, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)

    elapsed = time.time() - start_time
    logger.info(f"Results written to {output_path} in {elapsed:.1f}s")
    logger.info(f"Batch summary: {batch_summary.model_dump()}")

    return screening_result
