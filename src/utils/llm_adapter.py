import json
import logging
import os
from pydantic import BaseModel, Field
from src.config import Config

logger = logging.getLogger(__name__)


class LLMResumeExtraction(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    github_url: str = ""
    skills: list[str] = Field(default_factory=list)
    project_summaries: list[dict] = Field(default_factory=list)
    experience_summaries: list[dict] = Field(default_factory=list)
    education_summaries: list[dict] = Field(default_factory=list)
    ai_evidence: list[str] = Field(default_factory=list)
    python_evidence: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)


class LLMProjectScore(BaseModel):
    depth_score: int = Field(default=0, ge=0, le=40)
    is_shallow: bool = False
    depth_signals: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    summary: str = ""


class LLMAdapter:
    def __init__(self, config: Config):
        self.config = config
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        if not self.config.llm_enabled:
            return None
        if not self.config.openai_api_key:
            logger.warning("LLM_ENABLED is true but OPENAI_API_KEY is not set")
            return None
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.config.openai_api_key)
            return self._client
        except ImportError:
            logger.warning("openai package not installed. LLM features disabled.")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            return None

    def extract_resume_info(self, raw_text: str, filename: str) -> LLMResumeExtraction | None:
        client = self._get_client()
        if client is None:
            return None

        prompt = f"""Extract structured information from this resume text. Return JSON with these fields:
- name: candidate full name
- email: email address
- phone: phone number
- github_url: GitHub profile URL (full URL)
- skills: list of technical skills
- project_summaries: list of project summaries (name + brief description + technologies used)
- experience_summaries: list of work experience summaries (company + role + technologies + key achievements)
- education_summaries: list of education entries
- ai_evidence: list of evidence of AI/ML/LLM/RAG/agentic work
- python_evidence: list of evidence of Python usage
- strengths: list of candidate strengths
- weaknesses: list of candidate weaknesses or gaps

Resume text:
{raw_text[:4000]}

Return ONLY valid JSON, no explanation."""

        try:
            response = client.chat.completions.create(
                model=self.config.llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000,
            )
            content = response.choices[0].message.content
            if content:
                content = content.strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1]
                    if content.endswith("```"):
                        content = content[:-3]
                raw = json.loads(content)
                return LLMResumeExtraction.model_validate(raw)
            return None
        except json.JSONDecodeError as e:
            logger.warning(f"LLM returned invalid JSON for {filename}: {e}")
            return None
        except Exception as e:
            logger.warning(f"LLM call failed for {filename}: {e}")
            return None

    def score_ai_project(self, project_name: str, project_description: str, technologies: list[str]) -> LLMProjectScore | None:
        client = self._get_client()
        if client is None:
            return None

        prompt = f"""Evaluate this AI/ML project for depth and quality. Return JSON with:
- depth_score: 0-40 integer score
- is_shallow: boolean
- depth_signals: list of positive depth signals found
- concerns: list of concerns about project depth
- summary: 1-sentence summary

Project: {project_name}
Description: {project_description}
Technologies: {', '.join(technologies)}

Focus on: retrieval, state management, orchestration, evaluation, tool calling, backend logic, data processing, product logic vs. simple API wrappers.
Return ONLY valid JSON."""

        try:
            response = client.chat.completions.create(
                model=self.config.llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500,
            )
            content = response.choices[0].message.content
            if content:
                content = content.strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1]
                    if content.endswith("```"):
                        content = content[:-3]
                raw = json.loads(content)
                return LLMProjectScore.model_validate(raw)
            return None
        except Exception as e:
            logger.warning(f"LLM scoring failed for {project_name}: {e}")
            return None


def create_llm_adapter(config: Config) -> LLMAdapter:
    return LLMAdapter(config)
