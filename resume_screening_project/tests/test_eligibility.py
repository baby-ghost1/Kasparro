import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from src.config import Config
from src.models import CandidateInfo, ProjectInfo, ExperienceInfo, GitHubEnrichment, ScoreBreakdown
from src.screening.eligibility import (
    check_eligibility, check_python_evidence, check_ai_evidence,
    assess_shallow_ai,
)
from src.screening.scorer import score_candidate, _generate_project_summary
from src.enrichment.github_enricher import enrich_github, _extract_username


class TestPythonEvidence:
    def test_python_in_skills(self):
        info = CandidateInfo(
            name="Test",
            skills=["Python", "FastAPI", "React"],
            raw_text="Python FastAPI React PostgreSQL",
        )
        result = check_python_evidence(info)
        assert result.has_python is True
        assert len(result.evidence) > 0

    def test_python_in_project(self):
        info = CandidateInfo(
            name="Test",
            skills=["React"],
            projects=[ProjectInfo(name="Web App", description="Built with Python and FastAPI", technologies=["Python", "FastAPI"])],
            raw_text="React JavaScript",
        )
        result = check_python_evidence(info)
        assert result.has_python is True

    def test_no_python(self):
        info = CandidateInfo(
            name="Test",
            skills=["JavaScript", "React", "Node.js"],
            raw_text="JavaScript React Node.js TypeScript frontend developer",
        )
        result = check_python_evidence(info)
        assert result.has_python is False
        assert len(result.evidence) == 0

    def test_python_in_experience(self):
        info = CandidateInfo(
            name="Test",
            skills=["JavaScript"],
            experience=[ExperienceInfo(company="ACME", title="Dev", description="Built Python backend services", technologies=["Python"])],
            raw_text="JavaScript",
        )
        result = check_python_evidence(info)
        assert result.has_python is True


class TestAIEvidence:
    def test_ai_with_project(self):
        info = CandidateInfo(
            name="Test",
            skills=["Python", "LangChain", "OpenAI"],
            projects=[ProjectInfo(
                name="RAG Chatbot",
                description="Built a RAG pipeline with LangChain and vector search for document retrieval",
                technologies=["LangChain", "OpenAI", "ChromaDB"],
            )],
            raw_text="Python LangChain OpenAI RAG pipeline vector search",
        )
        result = check_ai_evidence(info)
        assert result.has_ai is True
        assert result.project_count >= 1
        assert len(result.frameworks) > 0

    def test_no_ai(self):
        info = CandidateInfo(
            name="Test",
            skills=["Python", "Django", "PostgreSQL"],
            raw_text="Python Django PostgreSQL REST API backend developer",
        )
        result = check_ai_evidence(info)
        assert result.has_ai is False

    def test_ai_frameworks_in_skills_only(self):
        info = CandidateInfo(
            name="Test",
            skills=["Python", "LangChain", "OpenAI"],
            raw_text="Python LangChain OpenAI skills only no projects",
        )
        result = check_ai_evidence(info)
        assert result.has_ai is False or result.project_count == 0

    def test_shallow_ai_detection(self):
        info = CandidateInfo(
            name="Test",
            skills=["Python", "OpenAI"],
            projects=[ProjectInfo(
                name="ChatGPT Wrapper",
                description="Simple wrapper around OpenAI API for chatbot responses",
                technologies=["OpenAI", "Python"],
            )],
            raw_text="Python OpenAI simple wrapper chatbot",
        )
        ai_result = check_ai_evidence(info)
        is_shallow, penalty, reason = assess_shallow_ai(info, ai_result)
        assert is_shallow is True
        assert penalty > 0


class TestEligibility:
    def test_python_and_ai_eligible(self):
        info = CandidateInfo(
            name="Python AI Dev",
            skills=["Python", "FastAPI", "LangChain"],
            projects=[ProjectInfo(
                name="RAG System",
                description="Built RAG pipeline with LangChain, vector embeddings, and retrieval augmented generation",
                technologies=["Python", "LangChain", "ChromaDB"],
            )],
            raw_text="Python FastAPI LangChain RAG pipeline vector embeddings",
        )
        result = check_eligibility(info)
        assert result.eligible is True
        assert len(result.rejection_reasons) == 0

    def test_python_only_rejected(self):
        info = CandidateInfo(
            name="Python Dev",
            skills=["Python", "Django", "PostgreSQL"],
            raw_text="Python Django PostgreSQL backend developer REST API",
        )
        result = check_eligibility(info)
        assert result.eligible is False
        assert any("AI" in r or "agentic" in r or "LLM" in r for r in result.rejection_reasons)

    def test_ai_only_no_python_rejected(self):
        info = CandidateInfo(
            name="JS AI Dev",
            skills=["JavaScript", "React", "LangChain"],
            projects=[ProjectInfo(
                name="AI Chatbot",
                description="LangChain chatbot with OpenAI integration",
                technologies=["JavaScript", "LangChain"],
            )],
            raw_text="JavaScript React LangChain OpenAI chatbot frontend",
        )
        result = check_eligibility(info)
        assert result.eligible is False
        assert any("Python" in r for r in result.rejection_reasons)

    def test_javascript_react_only_rejected(self):
        info = CandidateInfo(
            name="Frontend Dev",
            skills=["JavaScript", "React", "Next.js", "TypeScript"],
            raw_text="JavaScript React Next.js TypeScript frontend developer UI/UX",
        )
        result = check_eligibility(info)
        assert result.eligible is False
        assert len(result.rejection_reasons) >= 2

    def test_java_python_ai_eligible(self):
        info = CandidateInfo(
            name="Full Stack AI Dev",
            skills=["Java", "Python", "React", "LangChain", "FastAPI"],
            projects=[ProjectInfo(
                name="AI Agent System",
                description="Multi-agent workflow with LangGraph for task orchestration",
                technologies=["Python", "LangGraph", "FastAPI"],
            )],
            raw_text="Java Python React LangChain LangGraph FastAPI multi-agent workflow",
        )
        result = check_eligibility(info)
        assert result.eligible is True


class TestScoring:
    def _make_eligible_candidate(self):
        info = CandidateInfo(
            name="Strong AI Dev",
            skills=["Python", "FastAPI", "LangChain", "LangGraph", "Docker", "PostgreSQL", "Redis"],
            projects=[
                ProjectInfo(
                    name="RAG Pipeline",
                    description="Built a full RAG pipeline with retrieval, vector search, embeddings, state management, and evaluation. Orchestrated multi-step workflows with tool calling agents.",
                    technologies=["Python", "LangChain", "LangGraph", "ChromaDB", "FastAPI"],
                    highlights=["Implemented retrieval augmented generation", "Built evaluation pipeline", "Deployed with Docker"],
                ),
                ProjectInfo(
                    name="AI Agent Platform",
                    description="Multi-agent system with tool calling, state management, and workflow orchestration using LangGraph.",
                    technologies=["Python", "LangGraph", "FastAPI"],
                ),
            ],
            experience=[
                ExperienceInfo(company="AI Startup", title="Backend Engineer", description="Built Python FastAPI backend with Redis caching and PostgreSQL", technologies=["Python", "FastAPI", "Redis", "PostgreSQL"]),
            ],
            raw_text="Python FastAPI LangChain LangGraph Docker PostgreSQL Redis RAG pipeline retrieval vector embeddings multi-agent tool calling state management evaluation",
        )
        eligibility = check_eligibility(info)
        return info, eligibility

    def test_score_does_not_exceed_100(self):
        info, eligibility = self._make_eligible_candidate()
        config = Config()
        breakdown = score_candidate(info, eligibility, 10, "Active GitHub", config)
        assert breakdown.total <= 100
        assert breakdown.total == breakdown.ai_project_depth + breakdown.python_backend + breakdown.cloud_fullstack + breakdown.github + breakdown.engineering_depth

    def test_score_categories_within_bounds(self):
        info, eligibility = self._make_eligible_candidate()
        config = Config()
        breakdown = score_candidate(info, eligibility, 5, "Some activity", config)
        assert 0 <= breakdown.ai_project_depth <= 40
        assert 0 <= breakdown.python_backend <= 30
        assert 0 <= breakdown.cloud_fullstack <= 15
        assert 0 <= breakdown.github <= 10
        assert 0 <= breakdown.engineering_depth <= 5

    def test_strong_candidate_scores_high(self):
        info, eligibility = self._make_eligible_candidate()
        config = Config()
        breakdown = score_candidate(info, eligibility, 8, "Active GitHub", config)
        assert breakdown.total >= 50

    def test_shallow_ai_project_penalty(self):
        info = CandidateInfo(
            name="Shallow AI Dev",
            skills=["Python", "OpenAI"],
            projects=[ProjectInfo(
                name="ChatBot",
                description="Simple wrapper around OpenAI API for basic chatbot responses",
                technologies=["Python", "OpenAI"],
            )],
            raw_text="Python OpenAI simple wrapper chatbot basic API",
        )
        eligibility = check_eligibility(info)
        assert eligibility.eligible is True
        config = Config()
        breakdown = score_candidate(info, eligibility, 0, "", config)
        assert breakdown.ai_project_depth < 20
        assert len(breakdown.penalties) > 0

    def test_project_summary_generation(self):
        info = CandidateInfo(
            name="Test",
            skills=["Python"],
            projects=[ProjectInfo(name="AI App", description="Built with LangChain", technologies=["LangChain"])],
            experience=[ExperienceInfo(company="ACME", title="Dev")],
        )
        from src.models import AIEvidence
        ai_evidence = AIEvidence(has_ai=True, frameworks=["langchain"], project_count=1)
        summary = _generate_project_summary(info, ai_evidence)
        assert "AI" in summary or "LangChain" in summary or "project" in summary.lower()


class TestGitHubEnrichment:
    def test_extract_username(self):
        assert _extract_username("https://github.com/username") == "username"
        assert _extract_username("https://github.com/user-name_123/") == "user-name_123"
        assert _extract_username("https://gitlab.com/user") == ""

    def test_no_github_url(self):
        config = Config()
        result = enrich_github("", config)
        assert result.has_github is False

    def test_github_failure_graceful(self):
        config = Config()
        result = enrich_github("https://github.com/nonexistent_user_123456789xyz", config)
        assert result.has_github is True
        assert result.username == "nonexistent_user_123456789xyz"


class TestErrorHandling:
    def test_malformed_resume_no_crash(self):
        info = CandidateInfo(name="Unknown", raw_text="")
        eligibility = check_eligibility(info)
        assert eligibility.eligible is False

    def test_empty_text_eligibility(self):
        info = CandidateInfo(name="", raw_text="   ")
        eligibility = check_eligibility(info)
        assert eligibility.eligible is False
        assert len(eligibility.rejection_reasons) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
