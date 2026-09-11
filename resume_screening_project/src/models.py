from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class CandidateInfo(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    github_url: str = ""
    linkedin_url: str = ""
    skills: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    projects: list[ProjectInfo] = Field(default_factory=list)
    experience: list[ExperienceInfo] = Field(default_factory=list)
    education: list[EducationInfo] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    raw_text: str = ""


class ProjectInfo(BaseModel):
    name: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)
    highlights: list[str] = Field(default_factory=list)


class ExperienceInfo(BaseModel):
    company: str = ""
    title: str = ""
    duration: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)


class EducationInfo(BaseModel):
    institution: str = ""
    degree: str = ""
    field: str = ""
    duration: str = ""
    gpa: str = ""


class PythonEvidence(BaseModel):
    has_python: bool = False
    evidence: list[str] = Field(default_factory=list)
    evidence_type: list[str] = Field(default_factory=list)


class AIEvidence(BaseModel):
    has_ai: bool = False
    evidence: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    project_count: int = 0
    project_details: list[str] = Field(default_factory=list)


class EligibilityResult(BaseModel):
    eligible: bool = False
    rejection_reasons: list[str] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    python_evidence: PythonEvidence = Field(default_factory=PythonEvidence)
    ai_evidence: AIEvidence = Field(default_factory=AIEvidence)


class ScoreBreakdown(BaseModel):
    ai_project_depth: int = 0
    python_backend: int = 0
    cloud_fullstack: int = 0
    github: int = 0
    engineering_depth: int = 0
    total: int = 0
    evidence: dict[str, list[str]] = Field(default_factory=dict)
    penalties: list[str] = Field(default_factory=list)


class GitHubEnrichment(BaseModel):
    has_github: bool = False
    username: str = ""
    profile_url: str = ""
    recent_activity_score: int = 0
    repos_score: int = 0
    total_score: int = 0
    summary: str = ""
    recent_repos: list[str] = Field(default_factory=list)
    recent_activity: list[str] = Field(default_factory=list)
    error: str = ""


class CandidateResult(BaseModel):
    filename: str = ""
    candidate_name: str = ""
    eligible: bool = False
    rank: Optional[int] = None
    total_score: int = 0
    score_breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    matched_skills: list[str] = Field(default_factory=list)
    project_summary: str = ""
    github_summary: str = ""
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    rejection_reasons: list[str] = Field(default_factory=list)
    github_enrichment: GitHubEnrichment = Field(default_factory=GitHubEnrichment)
    parsing_error: str = ""
    llm_error: str = ""


class BatchSummary(BaseModel):
    total_resumes: int = 0
    successfully_parsed: int = 0
    eligible: int = 0
    rejected: int = 0
    failed: int = 0


class ScreeningResult(BaseModel):
    candidates: list[CandidateResult] = Field(default_factory=list)
    rejected: list[CandidateResult] = Field(default_factory=list)
    failed: list[CandidateResult] = Field(default_factory=list)
    batch_summary: BatchSummary = Field(default_factory=BatchSummary)


CandidateInfo.model_rebuild()
