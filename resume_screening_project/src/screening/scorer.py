import re
import logging
from src.config import Config
from src.models import (
    CandidateInfo, EligibilityResult, ScoreBreakdown, AIEvidence,
)
from src.screening.eligibility import (
    AI_FRAMEWORKS, CLOUD_TECH, FULLSTACK_TECH, ENGINEERING_DEPTH_SIGNALS,
    assess_shallow_ai,
)

logger = logging.getLogger(__name__)


def _score_ai_project_depth(
    info: CandidateInfo,
    ai_evidence: AIEvidence,
    config: Config,
) -> tuple[int, list[str], list[str], str]:
    max_pts = config.scoring_weights.ai_project_depth
    evidence = []
    penalties = []
    score = 0

    if ai_evidence.project_count == 0:
        return 5, ["AI frameworks mentioned but no concrete AI projects"], penalties, "Minimal AI project evidence"

    if ai_evidence.project_count >= 3:
        score += 12
        evidence.append(f"{ai_evidence.project_count} AI projects found")
    elif ai_evidence.project_count == 2:
        score += 8
        evidence.append("2 AI projects found")
    else:
        score += 5
        evidence.append("1 AI project found")

    framework_depth = len(set(ai_evidence.frameworks))
    if framework_depth >= 4:
        score += 10
        evidence.append(f"Deep AI framework usage ({framework_depth} frameworks)")
    elif framework_depth >= 2:
        score += 7
        evidence.append(f"Multiple AI frameworks used ({framework_depth})")
    elif framework_depth == 1:
        score += 4
        evidence.append("Single AI framework used")

    has_rag = any('rag' in fw or 'retriev' in fw or 'vector' in fw or 'embedding' in fw for fw in ai_evidence.frameworks)
    has_agent = any('agent' in fw or 'langgraph' in fw or 'tool call' in fw or 'multi' in fw for fw in ai_evidence.frameworks)
    has_evaluation = any('eval' in fw or 'langsmith' in fw or 'wandb' in fw for fw in ai_evidence.frameworks)

    if has_rag:
        score += 5
        evidence.append("RAG/retrieval implementation")
    if has_agent:
        score += 5
        evidence.append("Agentic workflow implementation")
    if has_evaluation:
        score += 3
        evidence.append("Evaluation pipeline")

    text_lower = info.raw_text.lower()
    depth_keywords = [
        (r'retrieval.?augmented|rag\s+pipeline|rag\s+system|rag\s+chatbot', "RAG pipeline"),
        (r'vector\s+(?:search|store|database|embedding)', "Vector search/store"),
        (r'tool[- ]?calling|function[- ]?calling', "Tool calling"),
        (r'multi[- ]?agent|multiagent', "Multi-agent system"),
        (r'stateful|state\s+management|conversation\s+memory', "State management"),
        (r'orchestrat', "Orchestration"),
        (r'fine[- ]?tun', "Fine-tuning"),
        (r'evaluation\s+pipeline|eval\s+pipeline', "Evaluation pipeline"),
        (r'(?:agent|agentic)\s+(?:system|workflow|pipeline)', "Agentic system"),
        (r'(?:backend|server|api)\s+(?:for|using|with)\s+(?:ai|llm|agent|rag)', "AI backend"),
    ]
    for pattern, label in depth_keywords:
        if re.search(pattern, text_lower):
            score += 3
            evidence.append(label)

    is_shallow, penalty, reason = assess_shallow_ai(info, ai_evidence)
    if is_shallow:
        score -= penalty
        penalties.append(reason)
        evidence.append(f"Penalty: {reason}")

    project_detail_bonus = 0
    for p in info.projects:
        ptext = (p.name + ' ' + p.description + ' ' + ' '.join(p.highlights)).lower()
        if any('ai' in fw for fw in ai_evidence.frameworks if fw in ptext):
            if len(p.description) > 100:
                project_detail_bonus += 2
                evidence.append(f"Detailed AI project: {p.name}")
            if len(p.highlights) >= 3:
                project_detail_bonus += 1
    score += min(project_detail_bonus, 5)

    score = max(0, min(score, max_pts))
    summary = f"AI/Agentic depth: {ai_evidence.project_count} projects, {len(ai_evidence.frameworks)} frameworks"
    return score, evidence, penalties, summary


def _score_python_backend(
    info: CandidateInfo,
    eligibility: EligibilityResult,
    config: Config,
) -> tuple[int, list[str], str]:
    max_pts = config.scoring_weights.python_backend
    evidence = []
    score = 0
    text_lower = info.raw_text.lower()

    py_evidence = eligibility.python_evidence
    if py_evidence.has_python:
        score += 5
        evidence.append("Python confirmed as skill/language")

    python_backend_frameworks = {"fastapi", "flask", "django", "uvicorn", "gunicorn", "celery"}
    all_techs = set()
    for s in info.skills:
        all_techs.add(s.lower())
    for fw in info.frameworks:
        all_techs.add(fw.lower())

    frameworks_used = python_backend_frameworks.intersection(all_techs)
    if frameworks_used:
        score += min(len(frameworks_used) * 4, 12)
        evidence.append(f"Python backend frameworks: {', '.join(frameworks_used)}")

    async_indicators = ["async", "asyncio", "await", "async def", "asynchronous"]
    for ind in async_indicators:
        if ind in text_lower:
            score += 2
            evidence.append(f"Async programming: {ind}")
            break

    db_indicators = {"postgresql", "postgres", "mysql", "redis", "mongodb", "sqlite", "dynamodb", "supabase"}
    dbs_used = db_indicators.intersection(all_techs)
    if dbs_used:
        score += min(len(dbs_used) * 2, 6)
        evidence.append(f"Database experience: {', '.join(dbs_used)}")

    api_indicators = ["rest api", "rest apis", "graphql", "grpc", "websocket"]
    for ind in api_indicators:
        if ind in text_lower:
            score += 2
            evidence.append(f"API development: {ind}")
            break

    data_processing = ["pandas", "numpy", "scipy", "etl", "data pipeline", "data processing", "spark"]
    for ind in data_processing:
        if ind in text_lower:
            score += 2
            evidence.append(f"Data processing: {ind}")
            break

    project_evidence = 0
    for p in info.projects:
        ptext = (' '.join(p.technologies) + ' ' + p.description).lower()
        if 'python' in ptext or 'fastapi' in ptext or 'flask' in ptext or 'django' in ptext:
            project_evidence += 1
    if project_evidence > 0:
        score += min(project_evidence * 2, 6)
        evidence.append(f"Python projects: {project_evidence}")

    exp_evidence = 0
    for exp in info.experience:
        etext = (' '.join(exp.technologies) + ' ' + exp.description).lower()
        if 'python' in etext or 'fastapi' in etext or 'flask' in etext or 'django' in etext:
            exp_evidence += 1
    if exp_evidence > 0:
        score += min(exp_evidence * 2, 4)
        evidence.append(f"Python work experience: {exp_evidence}")

    score = max(0, min(score, max_pts))
    summary = f"Python/Backend: {len(frameworks_used)} frameworks, {len(dbs_used)} databases"
    return score, evidence, summary


def _score_cloud_fullstack(
    info: CandidateInfo,
    config: Config,
) -> tuple[int, list[str], str]:
    max_pts = config.scoring_weights.cloud_fullstack
    evidence = []
    score = 0
    text_lower = info.raw_text.lower()

    all_techs = set()
    for s in info.skills:
        all_techs.add(s.lower())
    for fw in info.frameworks:
        all_techs.add(fw.lower())
    for p in info.projects:
        for t in p.technologies:
            all_techs.add(t.lower())

    cloud_used = CLOUD_TECH.intersection(all_techs)
    if cloud_used:
        score += min(len(cloud_used) * 3, 9)
        evidence.append(f"Cloud/DevOps: {', '.join(cloud_used)}")

    frontend_indicators = {"react", "react.js", "reactjs", "next.js", "nextjs", "vue", "vue.js", "angular"}
    frontend_used = frontend_indicators.intersection(all_techs)
    if frontend_used:
        score += min(len(frontend_used) * 2, 4)
        evidence.append(f"Frontend: {', '.join(frontend_used)}")

    docker_k8s = {"docker", "kubernetes", "k8s"}.intersection(all_techs)
    if docker_k8s:
        score += 2
        evidence.append(f"Containerization: {', '.join(docker_k8s)}")

    fullstack_techs = FULLSTACK_TECH.intersection(all_techs)
    if len(fullstack_techs) >= 3:
        score += 2
        evidence.append(f"Full-stack breadth ({len(fullstack_techs)} technologies)")

    score = max(0, min(score, max_pts))
    summary = f"Cloud/FullStack: {len(cloud_used)} cloud, {len(frontend_used)} frontend"
    return score, evidence, summary


def _score_engineering_depth(
    info: CandidateInfo,
    config: Config,
) -> tuple[int, list[str], str]:
    max_pts = config.scoring_weights.engineering_depth
    evidence = []
    score = 0
    text_lower = info.raw_text.lower()

    signals_found = []
    for signal in ENGINEERING_DEPTH_SIGNALS:
        if signal in text_lower:
            signals_found.append(signal)

    if len(signals_found) >= 6:
        score = 5
        evidence.append(f"Strong engineering depth ({len(signals_found)} signals)")
    elif len(signals_found) >= 4:
        score = 4
        evidence.append(f"Good engineering depth ({len(signals_found)} signals)")
    elif len(signals_found) >= 2:
        score = 3
        evidence.append(f"Moderate engineering depth ({len(signals_found)} signals)")
    elif len(signals_found) >= 1:
        score = 2
        evidence.append(f"Basic engineering depth ({len(signals_found)} signals)")
    else:
        score = 0
        evidence.append("Limited engineering depth signals")

    if signals_found:
        evidence.append(f"Signals: {', '.join(signals_found[:5])}")

    score = max(0, min(score, max_pts))
    summary = f"Engineering depth: {len(signals_found)} signals found"
    return score, evidence, summary


def _generate_strengths_concerns(
    info: CandidateInfo,
    ai_evidence: AIEvidence,
    score_breakdown: ScoreBreakdown,
) -> tuple[list[str], list[str]]:
    strengths = []
    concerns = []

    if score_breakdown.ai_project_depth >= 30:
        strengths.append("Strong AI/Agentic project depth")
    elif score_breakdown.ai_project_depth >= 20:
        strengths.append("Solid AI project experience")

    if score_breakdown.python_backend >= 22:
        strengths.append("Strong Python/Backend engineering")
    elif score_breakdown.python_backend >= 15:
        strengths.append("Good Python backend skills")

    if score_breakdown.cloud_fullstack >= 10:
        strengths.append("Strong cloud/full-stack capabilities")
    elif score_breakdown.cloud_fullstack >= 6:
        strengths.append("Cloud/DevOps experience")

    if score_breakdown.github >= 7:
        strengths.append("Active GitHub presence")

    if score_breakdown.engineering_depth >= 4:
        strengths.append("Strong engineering practices")

    if ai_evidence.project_count >= 3:
        strengths.append(f"Multiple AI projects ({ai_evidence.project_count})")

    has_rag = any('rag' in fw or 'retrieval' in fw or 'vector' in fw for fw in ai_evidence.frameworks)
    has_agent = any('agent' in fw or 'langgraph' in fw for fw in ai_evidence.frameworks)
    if has_rag:
        strengths.append("RAG/Retrieval experience")
    if has_agent:
        strengths.append("Agentic workflow experience")

    if score_breakdown.ai_project_depth < 15:
        concerns.append("Limited AI project depth")
    if score_breakdown.python_backend < 15:
        concerns.append("Limited Python/backend evidence")
    if score_breakdown.cloud_fullstack < 5:
        concerns.append("Limited cloud/full-stack evidence")
    if score_breakdown.engineering_depth < 2:
        concerns.append("Limited engineering depth signals")

    if score_breakdown.penalties:
        concerns.extend(score_breakdown.penalties)

    return strengths, concerns


def _generate_project_summary(info: CandidateInfo, ai_evidence: AIEvidence) -> str:
    parts = []
    if ai_evidence.project_count > 0:
        parts.append(f"{ai_evidence.project_count} AI/ML project(s)")
    if ai_evidence.frameworks:
        parts.append(f"Frameworks: {', '.join(ai_evidence.frameworks[:5])}")
    py_projects = [p for p in info.projects if 'python' in (' '.join(p.technologies) + ' ' + p.description).lower()]
    if py_projects:
        parts.append(f"Python projects: {len(py_projects)}")
    exp_count = len(info.experience)
    if exp_count > 0:
        parts.append(f"{exp_count} work experience(s)")

    if not parts:
        return "Limited project information available"
    return "; ".join(parts)


def score_candidate(
    info: CandidateInfo,
    eligibility: EligibilityResult,
    github_score: int,
    github_summary: str,
    config: Config,
) -> ScoreBreakdown:
    ai_score, ai_evidence_list, penalties, ai_summary = _score_ai_project_depth(
        info, eligibility.ai_evidence, config
    )
    py_score, py_evidence, py_summary = _score_python_backend(info, eligibility, config)
    cloud_score, cloud_evidence, cloud_summary = _score_cloud_fullstack(info, config)
    eng_score, eng_evidence, eng_summary = _score_engineering_depth(info, config)

    total = ai_score + py_score + cloud_score + github_score + eng_score
    total = max(0, min(total, config.max_score))

    all_evidence = {
        "ai_project_depth": ai_evidence_list + [ai_summary],
        "python_backend": py_evidence + [py_summary],
        "cloud_fullstack": cloud_evidence + [cloud_summary],
        "engineering_depth": eng_evidence + [eng_summary],
        "github": [github_summary] if github_summary else [],
    }

    breakdown = ScoreBreakdown(
        ai_project_depth=ai_score,
        python_backend=py_score,
        cloud_fullstack=cloud_score,
        github=github_score,
        engineering_depth=eng_score,
        total=total,
        evidence=all_evidence,
        penalties=penalties,
    )

    return breakdown
