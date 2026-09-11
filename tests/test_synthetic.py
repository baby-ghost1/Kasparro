import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from src.config import Config
from src.models import CandidateInfo, ProjectInfo, ExperienceInfo
from src.screening.eligibility import check_eligibility
from src.screening.scorer import score_candidate
from src.enrichment.github_enricher import enrich_github


class TestSyntheticPythonAICandidate:
    def test_strong_python_ai_candidate_is_eligible(self):
        info = CandidateInfo(
            name="Alice Chen",
            email="alice@example.com",
            github_url="https://github.com/alicechen",
            skills=["Python", "FastAPI", "LangChain", "LangGraph", "Docker", "PostgreSQL", "Redis"],
            projects=[
                ProjectInfo(
                    name="Multi-Agent Research Assistant",
                    description="Built a multi-agent system using LangGraph with tool calling, retrieval augmented generation, vector search with ChromaDB, conversation memory, and evaluation pipeline. Deployed with FastAPI and Docker.",
                    technologies=["Python", "LangGraph", "ChromaDB", "FastAPI", "Docker"],
                    highlights=["Implemented RAG pipeline", "Multi-agent orchestration", "Evaluation metrics"],
                ),
                ProjectInfo(
                    name="Document Q&A Platform",
                    description="Full-stack RAG application with embeddings, vector store, FastAPI backend, and React frontend. Includes caching with Redis and async processing.",
                    technologies=["Python", "FastAPI", "Redis", "ChromaDB"],
                ),
            ],
            experience=[
                ExperienceInfo(
                    company="AI Startup",
                    title="ML Engineer",
                    description="Built Python backend services with FastAPI, designed RAG pipelines, implemented evaluation frameworks, deployed with Docker on GCP",
                    technologies=["Python", "FastAPI", "Docker", "GCP"],
                ),
            ],
            raw_text="Python FastAPI LangChain LangGraph ChromaDB Docker PostgreSQL Redis multi-agent RAG retrieval vector search tool calling evaluation pipeline async",
        )
        eligibility = check_eligibility(info)
        assert eligibility.eligible is True
        assert len(eligibility.rejection_reasons) == 0
        matched_lower = [s.lower() for s in eligibility.matched_skills]
        assert "python" in matched_lower

    def test_strong_candidate_scores_high(self):
        info = CandidateInfo(
            name="Alice Chen",
            skills=["Python", "FastAPI", "LangChain", "Docker", "PostgreSQL", "Redis"],
            projects=[
                ProjectInfo(
                    name="RAG Agent",
                    description="Multi-agent RAG system with tool calling, state management, vector search, evaluation pipeline, deployed with Docker and FastAPI",
                    technologies=["Python", "LangChain", "Docker", "FastAPI"],
                    highlights=["RAG pipeline", "agent orchestration", "evaluation"],
                ),
            ],
            experience=[
                ExperienceInfo(company="AI Co", title="Engineer", description="Python FastAPI backend with Redis caching and PostgreSQL", technologies=["Python", "FastAPI", "Redis"]),
            ],
            raw_text="Python FastAPI LangChain Docker PostgreSQL Redis RAG agent evaluation",
        )
        eligibility = check_eligibility(info)
        config = Config()
        breakdown = score_candidate(info, eligibility, 8, "Active GitHub", config)
        assert breakdown.total >= 60
        assert breakdown.ai_project_depth >= 20
        assert breakdown.python_backend >= 10


class TestSyntheticRejectCandidates:
    def test_python_only_no_ai_rejected(self):
        info = CandidateInfo(
            name="Bob Smith",
            skills=["Python", "Django", "PostgreSQL", "Redis"],
            projects=[
                ProjectInfo(name="Web App", description="E-commerce platform with Django REST framework", technologies=["Python", "Django"]),
            ],
            raw_text="Python Django PostgreSQL Redis backend developer REST API",
        )
        eligibility = check_eligibility(info)
        assert eligibility.eligible is False
        assert any("AI" in r or "agentic" in r or "LLM" in r for r in eligibility.rejection_reasons)

    def test_ai_only_no_python_rejected(self):
        info = CandidateInfo(
            name="Carol White",
            skills=["JavaScript", "React", "LangChain"],
            projects=[
                ProjectInfo(name="AI Chatbot", description="LangChain chatbot with OpenAI", technologies=["JavaScript", "LangChain"]),
            ],
            raw_text="JavaScript React LangChain OpenAI chatbot",
        )
        eligibility = check_eligibility(info)
        assert eligibility.eligible is False
        assert any("Python" in r for r in eligibility.rejection_reasons)

    def test_js_react_only_rejected(self):
        info = CandidateInfo(
            name="Dave Johnson",
            skills=["JavaScript", "React", "Next.js", "TypeScript", "Node.js"],
            projects=[
                ProjectInfo(name="E-commerce", description="Next.js storefront with Stripe integration", technologies=["Next.js", "TypeScript"]),
            ],
            raw_text="JavaScript React Next.js TypeScript Node.js frontend developer",
        )
        eligibility = check_eligibility(info)
        assert eligibility.eligible is False
        assert len(eligibility.rejection_reasons) >= 2


class TestSyntheticShallowAI:
    def test_simple_llm_wrapper_penalized(self):
        info = CandidateInfo(
            name="Eve Davis",
            skills=["Python", "OpenAI"],
            projects=[
                ProjectInfo(
                    name="ChatBot",
                    description="Simple wrapper around OpenAI API for basic chatbot responses with prompt to response flow",
                    technologies=["Python", "OpenAI"],
                ),
            ],
            raw_text="Python OpenAI simple wrapper chatbot prompt response",
        )
        eligibility = check_eligibility(info)
        assert eligibility.eligible is True
        config = Config()
        breakdown = score_candidate(info, eligibility, 0, "", config)
        assert breakdown.ai_project_depth < 20
        assert len(breakdown.penalties) > 0

    def test_framework_only_skills_penalized(self):
        info = CandidateInfo(
            name="Frank Lee",
            skills=["Python", "LangChain", "OpenAI", "Django"],
            projects=[
                ProjectInfo(name="Blog", description="Personal blog with Django", technologies=["Python", "Django"]),
            ],
            raw_text="Python LangChain OpenAI Django blog personal project",
        )
        eligibility = check_eligibility(info)
        assert eligibility.eligible is False
        assert any("AI" in r or "agentic" in r for r in eligibility.rejection_reasons)


class TestSyntheticScoreBounds:
    def test_score_never_exceeds_100(self):
        info = CandidateInfo(
            name="Super Dev",
            skills=["Python", "FastAPI", "LangChain", "LangGraph", "Docker", "Kubernetes", "AWS", "GCP", "Redis", "PostgreSQL"],
            projects=[
                ProjectInfo(name="AI Platform", description="Multi-agent RAG system with orchestration, tool calling, evaluation, deployed on K8s", technologies=["Python", "LangChain", "Docker", "K8s"]),
                ProjectInfo(name="ML Pipeline", description="End-to-end ML pipeline with fine-tuning, evaluation, monitoring", technologies=["Python", "TensorFlow"]),
            ],
            experience=[
                ExperienceInfo(company="BigTech", title="Sr Engineer", description="Python FastAPI async backend with Redis, PostgreSQL, Docker, K8s, GCP", technologies=["Python", "FastAPI", "K8s"]),
            ],
            raw_text="Python FastAPI LangChain LangGraph Docker Kubernetes AWS GCP Redis PostgreSQL async evaluation fine-tuning monitoring",
        )
        eligibility = check_eligibility(info)
        config = Config()
        breakdown = score_candidate(info, eligibility, 10, "Very active", config)
        assert breakdown.total <= 100
        assert breakdown.ai_project_depth <= 40
        assert breakdown.python_backend <= 30
        assert breakdown.cloud_fullstack <= 15
        assert breakdown.github <= 10
        assert breakdown.engineering_depth <= 5

    def test_score_sum_equals_total(self):
        info = CandidateInfo(
            name="Test Dev",
            skills=["Python", "LangChain"],
            projects=[
                ProjectInfo(name="AI Project", description="RAG with LangChain and vector search", technologies=["Python", "LangChain"]),
            ],
            raw_text="Python LangChain RAG vector search",
        )
        eligibility = check_eligibility(info)
        config = Config()
        breakdown = score_candidate(info, eligibility, 5, "Some activity", config)
        calc = (breakdown.ai_project_depth + breakdown.python_backend +
                breakdown.cloud_fullstack + breakdown.github + breakdown.engineering_depth)
        assert calc == breakdown.total


class TestSyntheticErrorHandling:
    def test_empty_resume_handled(self):
        info = CandidateInfo(name="", raw_text="")
        eligibility = check_eligibility(info)
        assert eligibility.eligible is False

    def test_whitespace_only_resume(self):
        info = CandidateInfo(name="", raw_text="   \n\n   ")
        eligibility = check_eligibility(info)
        assert eligibility.eligible is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
