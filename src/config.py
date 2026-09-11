import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ScoringWeights:
    ai_project_depth: int = 40
    python_backend: int = 30
    cloud_fullstack: int = 15
    github: int = 10
    engineering_depth: int = 5


@dataclass
class Config:
    scoring_weights: ScoringWeights = field(default_factory=ScoringWeights)

    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))
    llm_enabled: bool = field(default_factory=lambda: os.getenv("LLM_ENABLED", "false").lower() == "true")

    github_token: str = field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))

    max_score: int = 100

    shallow_ai_penalty_min: int = 5
    shallow_ai_penalty_max: int = 15

    github_recent_activity_max: int = 5
    github_repos_max: int = 5

    github_request_timeout: int = 10
    llm_request_timeout: int = 30
