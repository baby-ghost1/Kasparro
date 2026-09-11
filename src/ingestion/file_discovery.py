import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def discover_resumes(input_dir: str) -> list[dict[str, str]]:
    results = []
    input_path = Path(input_dir)
    if not input_path.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        return results

    seen_names: set[str] = set()
    for file_path in sorted(input_path.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() in (".pdf", ".docx", ".txt"):
            name = file_path.name
            if name in seen_names:
                logger.warning(f"Duplicate file skipped: {name}")
                continue
            seen_names.add(name)
            results.append({"filename": name, "path": str(file_path)})

    logger.info(f"Discovered {len(results)} resume files in {input_dir}")
    return results
