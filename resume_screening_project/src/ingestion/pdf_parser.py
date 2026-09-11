import logging
import pymupdf

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        doc = pymupdf.open(pdf_path)
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        full_text = "\n".join(text_parts)
        if not full_text.strip():
            logger.warning(f"Empty text extracted from {pdf_path}")
        return full_text
    except Exception as e:
        logger.error(f"Failed to parse PDF {pdf_path}: {e}")
        raise
