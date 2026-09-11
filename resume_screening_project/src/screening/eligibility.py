import re
import logging
from src.models import (
    CandidateInfo, EligibilityResult, PythonEvidence, AIEvidence,
)

logger = logging.getLogger(__name__)

PYTHON_SKILL_VARIANTS = {
    "python", "python3", "python2", "py", "cpython", "pypy", "micropython",
}

PYTHON_CONTEXT_PATTERNS = [
    r'(?:built|developed|implemented|created|engineered|designed|wrote|coded)\s+(?:in|using|with)\s+python',
    r'python\s+(?:backend|api|script|application|service|pipeline|tool|cli|bot|microservice)',
    r'(?:fastapi|flask|django|uvicorn|gunicorn|celery|pydantic|asyncio)',
    r'(?:pytorch|tensorflow|scikit-learn|pandas|numpy|scipy|matplotlib)',
    r'\b(?:pip|poetry|conda|virtualenv|pyenv)\b',
    r'(?:pytest|unittest|tox|mypy|black|ruff|pylint|flake8)',
    r'python\s+(?:and|&|/\s*)\s*(?:postgresql|redis|docker|aws|gcp)',
    r'(?:requirements\.txt|pyproject\.toml|setup\.py|setup\.cfg)',
]

AI_FRAMEWORKS = {
    "langchain", "langgraph", "llamaindex", "llama index", "openai", "anthropic",
    "huggingface", "hugging face", "transformers", "pytorch", "tensorflow",
    "keras", "scikit-learn", "sklearn", "bert", "gpt", "chatgpt",
    "rag", "retrieval augmented generation", "retrieval-augmented",
    "vector search", "embedding", "embeddings", "vector database",
    "pinecone", "weaviate", "chromadb", "chroma", "faiss", "milvus",
    "tool calling", "tool-calling", "function calling",
    "multi-agent", "multi agent", "agentic", "agent",
    "langsmith", "weights & biases", "wandb", "mlflow",
    "google adk", "adk", "crewai", "autogen",
    "ollama", "llama", "mistral", "gemini", "claude",
    "evaluation pipeline", "eval pipeline",
    "prompt engineering", "fine-tuning", "fine tuning", "finetuning",
    "neural network", "deep learning", "machine learning",
    "nlp", "natural language processing", "computer vision",
    "image classification", "object detection", "sentiment analysis",
    "text generation", "text classification", "named entity recognition",
    "recommendation system", "conversational ai",
}

AI_PROJECT_SIGNAL_PATTERNS = [
    r'(?:built|developed|implemented|created|engineered|designed)\s+.*(?:ai|llm|rag|agent|chatbot|recommender)',
    r'(?:rag|retrieval)\s+(?:pipeline|system|chatbot|application|platform|workflow)',
    r'(?:agent|agentic)\s+(?:system|workflow|pipeline|platform|architecture)',
    r'(?:tool[- ]?calling|function[- ]?calling)\s+(?:agent|system|workflow)',
    r'(?:multi[- ]?agent|multiagent)\s+(?:system|workflow|architecture|orchestration)',
    r'(?:vector\s+(?:search|store|database|embedding|db))',
    r'(?:embedding|embeddings?)\s+(?:pipeline|system|search|retrieval|indexing)',
    r'(?:llm|large language model)\s+(?:application|pipeline|system|workflow|agent|wrapper|api)',
    r'(?:langchain|langgraph|llamaindex)\s+(?:chain|agent|workflow|pipeline|application)',
    r'(?:evaluation|eval)\s+pipeline\s+(?:for|using|with)',
    r'(?:fine[- ]?tun(?:e|ed|ing)|finetun(?:e|ed|ing))\s+(?:model|llm|gpt)',
    r'(?:prompt|prompts?)\s+(?:template|engineering|optimization|chaining)',
    r'(?:chatbot|conversational)\s+(?:ai|agent|bot|assistant)',
    r'(?:recommendation|classifier|sentiment)\s+(?:model|system|engine|pipeline)',
    r'(?:tensorflow|pytorch|keras|transformers)\s+(?:model|network|pipeline|system)',
]

SHALLOW_AI_INDICATORS = [
    r'(?:simple|basic|quick)\s+(?:llm|openai|chatgpt|gpt|api)\s+(?:wrapper|call|integration)',
    r'(?:wrapper)\s+(?:around|for|to)\s+(?:openai|gpt|llama|llm|api)',
    r'(?:prompt|chat)\s*(?:→|->|to)\s*(?:response|output|completion)',
    r'(?:api\s+)?(?:call|wrapper)\s+(?:to|for)\s+(?:openai|gpt|llama)',
    r'(?:chatgpt|openai)\s+(?:clone|copy|wrapper|api\s*call)',
    r'(?:tutorial|course|assignment)\s+(?:project|implementation)',
    r'(?:hello\s+world|todo\s+app|calculator)\s+(?:with|using)\s+(?:llm|ai|gpt)',
    r'(?:simple|basic)\s+(?:chatbot|bot)\s+(?:using|with|built)',
    r'(?:simple|basic)\s+(?:openai|llm|gpt)',
]

CLOUD_TECH = {
    "aws", "gcp", "google cloud", "azure", "heroku", "vercel", "netlify",
    "docker", "kubernetes", "k8s", "terraform", "ansible",
    "ci/cd", "github actions", "jenkins", "gitlab ci",
    "nginx", "apache", "load balancer", "cdn",
}

FULLSTACK_TECH = {
    "react", "react.js", "reactjs", "next.js", "nextjs", "vue", "angular",
    "node.js", "nodejs", "express", "express.js",
    "html", "css", "tailwind", "bootstrap",
    "postgresql", "postgres", "mysql", "mongodb", "redis",
    "graphql", "rest api", "rest apis",
    "fastapi", "flask", "django", "spring boot",
}

ENGINEERING_DEPTH_SIGNALS = {
    "testing", "test suite", "unit test", "integration test", "e2e test", "pytest", "jest", "mocha",
    "caching", "redis cache", "memcached",
    "queue", "celery", "rabbitmq", "kafka", "redis queue",
    "async", "asyncio", "concurrent", "concurrency", "threading", "multiprocessing",
    "monitoring", "observability", "logging", "prometheus", "grafana", "sentry",
    "circuit breaker", "retry", "backoff", "rate limiting",
    "scalability", "horizontal scaling", "load balancing",
    "ci/cd", "github actions", "jenkins", "pipeline",
    "docker", "kubernetes", "containerization",
    "database migration", "alembic", "schema",
    "validation", "pydantic", "marshmallow", "joi",
    "error handling", "exception handling", "try except",
    "microservice", "microservices",
    "webhook", "event-driven", "event driven",
    "pagination", "throttling",
}


def check_python_evidence(info: CandidateInfo) -> PythonEvidence:
    evidence = []
    evidence_types = []
    text_lower = info.raw_text.lower()

    for skill in info.skills:
        if skill.lower() in PYTHON_SKILL_VARIANTS:
            evidence.append(f"Skill listed: {skill}")
            evidence_types.append("skill")
            break

    for lang in info.languages:
        if lang.lower() in PYTHON_SKILL_VARIANTS:
            evidence.append(f"Language listed: {lang}")
            evidence_types.append("language")
            break

    for fw in info.frameworks:
        if any(pw in fw.lower() for pw in PYTHON_SKILL_VARIANTS):
            evidence.append(f"Framework listed: {fw}")
            evidence_types.append("framework")
            break

    for project in info.projects:
        techs = ' '.join(project.technologies).lower() + ' ' + project.description.lower() + ' ' + project.name.lower()
        if 'python' in techs:
            evidence.append(f"Project uses Python: {project.name}")
            evidence_types.append("project")
        if any(pw in techs for pw in ["fastapi", "flask", "django", "pytorch", "tensorflow"]):
            evidence.append(f"Python framework in project: {project.name}")
            evidence_types.append("project")

    for exp in info.experience:
        techs = ' '.join(exp.technologies).lower() + ' ' + exp.description.lower()
        if 'python' in techs:
            evidence.append(f"Work experience uses Python: {exp.company or exp.title}")
            evidence_types.append("experience")
        if any(pw in techs for pw in ["fastapi", "flask", "django", "pytorch", "tensorflow"]):
            evidence.append(f"Python framework in work: {exp.company or exp.title}")
            evidence_types.append("experience")

    for pattern in PYTHON_CONTEXT_PATTERNS:
        if re.search(pattern, text_lower):
            evidence.append(f"Context match: {pattern[:50]}")
            evidence_types.append("context")
            break

    return PythonEvidence(
        has_python=len(evidence) > 0,
        evidence=evidence[:5],
        evidence_type=list(set(evidence_types)),
    )


def check_ai_evidence(info: CandidateInfo) -> AIEvidence:
    evidence = []
    frameworks_found = []
    project_count = 0
    project_details = []
    text_lower = info.raw_text.lower()

    all_text_sources = []
    for s in info.skills:
        all_text_sources.append(s.lower())
    for fw in info.frameworks:
        all_text_sources.append(fw.lower())
    for cert in info.certifications:
        all_text_sources.append(cert.lower())
    for project in info.projects:
        all_text_sources.append(' '.join(project.technologies).lower())
        all_text_sources.append(project.description.lower())
        all_text_sources.append(project.name.lower())
    for exp in info.experience:
        all_text_sources.append(' '.join(exp.technologies).lower())
        all_text_sources.append(exp.description.lower())
    all_text_sources.append(text_lower)

    combined = ' '.join(all_text_sources)

    for fw in AI_FRAMEWORKS:
        if fw in combined:
            frameworks_found.append(fw)

    for project in info.projects:
        project_text = (project.name + ' ' + project.description + ' ' + ' '.join(project.technologies) + ' ' + ' '.join(project.highlights)).lower()
        is_ai_project = False
        for signal in AI_PROJECT_SIGNAL_PATTERNS:
            if re.search(signal, project_text):
                is_ai_project = True
                break
        if not is_ai_project:
            for fw in AI_FRAMEWORKS:
                if fw in project_text:
                    is_ai_project = True
                    break
        if is_ai_project:
            project_count += 1
            project_details.append(f"{project.name}: {project.description[:100]}")
            evidence.append(f"AI project: {project.name}")

    for exp in info.experience:
        exp_text = (exp.title + ' ' + exp.description + ' ' + ' '.join(exp.technologies)).lower()
        for fw in AI_FRAMEWORKS:
            if fw in exp_text:
                evidence.append(f"AI in work: {exp.company or exp.title}")
                break

    for pattern in AI_PROJECT_SIGNAL_PATTERNS:
        if re.search(pattern, text_lower):
            evidence.append(f"AI context in resume")
            break

    return AIEvidence(
        has_ai=len(evidence) > 0 and (len(frameworks_found) > 0 or project_count > 0 or len(evidence) > 1),
        evidence=evidence[:10],
        frameworks=list(set(frameworks_found)),
        project_count=project_count,
        project_details=project_details[:5],
    )


def assess_shallow_ai(info: CandidateInfo, ai_evidence: AIEvidence) -> tuple[bool, int, str]:
    combined_text = info.raw_text.lower()
    for project in info.projects:
        combined_text += ' ' + project.name.lower() + ' ' + project.description.lower() + ' ' + ' '.join(project.technologies).lower()
    for exp in info.experience:
        combined_text += ' ' + exp.description.lower() + ' ' + ' '.join(exp.technologies).lower()

    for pattern in SHALLOW_AI_INDICATORS:
        if re.search(pattern, combined_text):
            return True, 10, f"Shallow AI indicator: {pattern[:60]}"

    if ai_evidence.project_count == 0 and len(ai_evidence.frameworks) > 0:
        frameworks_in_skills = [fw for fw in ai_evidence.frameworks if fw in [s.lower() for s in info.skills]]
        if frameworks_in_skills and len(frameworks_in_skills) == len(ai_evidence.frameworks):
            return True, 8, "AI frameworks only in skills, no project evidence"

    if ai_evidence.project_count == 1 and len(ai_evidence.frameworks) <= 2:
        project_text = ""
        for p in info.projects:
            pt = (p.name + ' ' + p.description).lower()
            for fw in AI_FRAMEWORKS:
                if fw in pt:
                    project_text = pt
                    break
            if project_text:
                break
        if project_text:
            has_retrieval = bool(re.search(r'retriev|rag|vector|embedding|search', project_text))
            has_state = bool(re.search(r'state|memory|context|workflow|orchestrat', project_text))
            has_tools = bool(re.search(r'tool|function call|plugin|action', project_text))
            has_backend = bool(re.search(r'api|endpoint|fastapi|flask|django|backend|server|database', project_text))
            depth_signals = sum([has_retrieval, has_state, has_tools, has_backend])
            if depth_signals <= 1:
                return True, 8, "AI project appears shallow - limited depth signals"

    return False, 0, ""


def check_eligibility(info: CandidateInfo) -> EligibilityResult:
    rejection_reasons = []
    matched_skills = []

    python_evidence = check_python_evidence(info)
    ai_evidence = check_ai_evidence(info)

    if python_evidence.has_python:
        for s in info.skills:
            if s.lower() in PYTHON_SKILL_VARIANTS:
                matched_skills.append(s)
        matched_skills.extend(["Python"])
    else:
        rejection_reasons.append("No evidence of Python as a genuine skill, project technology, or implementation language")

    if ai_evidence.has_ai:
        matched_skills.extend([fw.title() for fw in ai_evidence.frameworks[:5]])
    else:
        rejection_reasons.append("No meaningful AI/LLM/RAG/agentic project evidence found")

    all_skills = set()
    for s in info.skills:
        all_skills.add(s.lower())
    for fw in info.frameworks:
        all_skills.add(fw.lower())

    fullstack_present = any(t in all_skills for t in FULLSTACK_TECH)
    cloud_present = any(t in all_skills for t in CLOUD_TECH)

    eligible = python_evidence.has_python and ai_evidence.has_ai

    return EligibilityResult(
        eligible=eligible,
        rejection_reasons=rejection_reasons,
        matched_skills=list(set(matched_skills)),
        python_evidence=python_evidence,
        ai_evidence=ai_evidence,
    )
