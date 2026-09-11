import re
import logging
from src.models import (
    CandidateInfo, ProjectInfo, ExperienceInfo, EducationInfo,
)

logger = logging.getLogger(__name__)

_SECTION_HEADERS = [
    "summary", "profile", "objective", "about",
    "education", "experience", "work experience", "professional experience",
    "projects", "key projects", "personal projects", "academic projects",
    "skills", "technical skills", "technical expertise", "competencies",
    "certifications", "certificates", "awards", "achievements",
    "contact", "links", "languages",
]


def _extract_email(text: str) -> str:
    m = re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', text)
    return m.group(0) if m else ""


def _extract_phone(text: str) -> str:
    patterns = [
        r'\+?\d{1,3}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3,5}[\s\-]?\d{3,5}',
        r'\d{10}',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(0).strip()
    return ""


def _extract_github(text: str) -> str:
    m = re.search(r'github\.com/([A-Za-z0-9_.-]+)', text, re.IGNORECASE)
    if m:
        username = m.group(1).rstrip('/')
        return f"https://github.com/{username}"
    return ""


def _extract_linkedin(text: str) -> str:
    m = re.search(r'linkedin\.com/in/([A-Za-z0-9_.%-]+)', text, re.IGNORECASE)
    if m:
        return f"https://linkedin.com/in/{m.group(1)}"
    return ""


def _extract_name(text: str) -> str:
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return ""

    skip_patterns = r'@|phone|email|linkedin|github|\+\d|\bsummary\b|\bobjective\b|\bprofile\b|\babout\b|\bcontact\b|\bresume\b|\bcv\b|\bportfolio\b|\bleetcode\b|\bcertification\b|\beducation\b|\bskills\b|\bexperience\b|\bprojects\b|\btechnical\b|\blanguages\b|\bframeworks\b|\btools\b|\bdatabases\b|\bdevops\b|\bprogramming\b|\bdatabase\b|\bweb\b|\bdevelopment\b|\bbasic\b|\bschool\b|\bcollege\b|\buniversity\b|\bgrade\b|\bcgpa\b|\baddress\b|\bmobile\b|\bproject\b|\bintern\b|\bwork\b|\bcompany\b|\blink\b|\bcert\b|\baward\b|\bhonour\b|\bhonor\b|\bbachelor\b|\bmaster\b|\bb\.tech\b|\bm\.tech\b|\bb\.s\b|\bm\.s\b|\bbca\b|\bmca\b|\bsecondary\b|\bhigher\b|\bscience\b|\bpresent\b|\bjan\b|\bfeb\b|\bmar\b|\bapr\b|\bmay\b|\bjun\b|\bjul\b|\baug\b|\bsep\b|\boct\b|\bnov\b|\bdec\b|\b20\d{2}\b'

    for line in lines[:10]:
        clean = re.sub(r'[^\w\s.,/-]', '', line).strip()
        if not clean or len(clean) < 2:
            continue
        if re.search(skip_patterns, clean, re.IGNORECASE):
            continue
        if re.match(r'^[\d/\-|:]+$', clean):
            continue
        words = clean.split()
        if 1 <= len(words) <= 5:
            if all(len(w) > 0 for w in words):
                has_alpha = any(w[0].isalpha() for w in words if w)
                if has_alpha:
                    return clean[:60]

    email_line_idx = -1
    for i, line in enumerate(lines):
        if re.search(r'@[\w.-]+\.\w+', line):
            email_line_idx = i
            break
    if email_line_idx > 0:
        for j in range(max(0, email_line_idx - 5), min(len(lines), email_line_idx + 3)):
            line = lines[j]
            clean = re.sub(r'[^\w\s.,/-]', '', line).strip()
            if not clean or len(clean) < 3:
                continue
            if re.search(skip_patterns, clean, re.IGNORECASE):
                continue
            if re.match(r'^[\d/\-|:]+$', clean):
                continue
            words = clean.split()
            if 2 <= len(words) <= 5:
                has_alpha = any(w[0].isalpha() for w in words if w)
                if has_alpha:
                    return clean[:60]

    for line in lines[:30]:
        clean = re.sub(r'[^\w\s.,/-]', '', line).strip()
        if not clean or len(clean) < 3:
            continue
        if re.search(skip_patterns, clean, re.IGNORECASE):
            continue
        if re.match(r'^[\d/\-|:]+$', clean):
            continue
        words = clean.split()
        if 2 <= len(words) <= 5:
            has_alpha = any(w[0].isalpha() for w in words if w)
            if has_alpha:
                return clean[:60]

    return "Unknown"


def _split_sections(text: str) -> dict[str, str]:
    lines = text.split('\n')
    sections: dict[str, list[str]] = {}
    current_header = "__top__"
    sections[current_header] = []

    for line in lines:
        stripped = line.strip()
        lower = stripped.lower().rstrip(':')
        if lower in _SECTION_HEADERS and len(stripped) < 60:
            current_header = lower
            if current_header not in sections:
                sections[current_header] = []
        else:
            sections[current_header].append(line)

    return {k: '\n'.join(v) for k, v in sections.items()}


def _extract_skills(text: str) -> list[str]:
    skills = set()
    tech_keywords = [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang", "rust",
        "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql", "nosql",
        "react", "react.js", "reactjs", "next.js", "nextjs", "vue", "vue.js", "angular",
        "node.js", "nodejs", "express", "express.js", "fastapi", "flask", "django",
        "spring", "spring boot", "springboot",
        "pytorch", "tensorflow", "keras", "scikit-learn", "sklearn", "pandas", "numpy",
        "langchain", "langgraph", "llamaindex", "llama index", "openai", "anthropic",
        "hugging face", "huggingface", "transformers",
        "docker", "kubernetes", "k8s", "aws", "gcp", "google cloud", "azure",
        "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
        "graphql", "rest api", "rest apis", "grpc",
        "git", "github", "gitlab", "jenkins", "ci/cd", "github actions",
        "html", "html5", "css", "css3", "tailwind", "bootstrap",
        "sass", "scss", "less",
        "mongo", "dynamodb", "sqlite", "firebase", "supabase",
        "linux", "bash", "shell",
        "celery", "rabbitmq", "kafka", "grpc",
        "pydantic", "asyncio", "celery",
        "rag", "vector database", "pinecone", "weaviate", "chromadb", "chroma", "faiss",
        "langsmith", "openai api", "anthropic api",
        "airflow", "spark", "hadoop", "etl",
        "terraform", "ansible", "prometheus", "grafana",
        "figma", "postman", "swagger",
        "google adk", "adk", "crewai", "autogen",
        "ollama", "llama", "mistral", "gpt", "gemini",
        "mistral", "claude",
        "opencv", "nltk", "spacy",
        "fastapi", "uvicorn", "gunicorn",
        "websocket", "sse",
        "stripe", "razorpay",
        "xgboost", "lightgbm",
        "mlops", "mlflow", "wandb", "neptune",
    ]
    text_lower = text.lower()
    for kw in tech_keywords:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, text_lower):
            skills.add(kw)
    return sorted(skills)


def _extract_projects(text: str) -> list[ProjectInfo]:
    sections = _split_sections(text)
    projects_text = sections.get("projects", "") or sections.get("key projects", "") or sections.get("personal projects", "") or sections.get("academic projects", "")
    if not projects_text.strip():
        return []

    projects = []
    blocks = re.split(r'\n(?=[A-Z][^\n]{3,80}\s*[|\-–—])', projects_text)
    if len(blocks) <= 1:
        blocks = re.split(r'\n{2,}', projects_text)

    for block in blocks:
        block = block.strip()
        if not block or len(block) < 20:
            continue
        first_line = block.split('\n')[0].strip()
        name_match = re.split(r'\s*[|\-–—]\s*', first_line)
        name = name_match[0].strip()[:80] if name_match else first_line[:80]

        technologies = []
        tech_match = re.search(r'\|\s*(.+?)$', first_line)
        if tech_match:
            technologies = [t.strip() for t in re.split(r'[,/]', tech_match.group(1)) if t.strip()]

        bullets = [l.strip().lstrip('•-–* ') for l in block.split('\n')[1:] if l.strip() and len(l.strip()) > 5]

        if not technologies:
            tech_kw = re.findall(r'(?:built with|using|tech stack[:\s]*|technologies?[:\s]*)(.+?)(?:\.|$)', block, re.IGNORECASE)
            if tech_kw:
                technologies = [t.strip() for t in re.split(r'[,/]', tech_kw[0]) if t.strip()]

        projects.append(ProjectInfo(
            name=name,
            description=block[:300],
            technologies=technologies,
            highlights=bullets[:5],
        ))
    return projects[:10]


def _extract_experience(text: str) -> list[ExperienceInfo]:
    sections = _split_sections(text)
    exp_text = sections.get("experience", "") or sections.get("work experience", "") or sections.get("professional experience", "")
    if not exp_text.strip():
        return []

    experiences = []
    blocks = re.split(r'\n{2,}', exp_text)
    for block in blocks:
        block = block.strip()
        if not block or len(block) < 15:
            continue
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        title = lines[0] if lines else ""
        company = lines[1] if len(lines) > 1 else ""
        duration = ""
        for l in lines[:4]:
            if re.search(r'\b(?:present|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|20\d{2})\b', l, re.IGNORECASE):
                duration = l
                break
        description = '\n'.join(lines[4:]) if len(lines) > 4 else '\n'.join(lines[2:])
        technologies = []
        tech_kw = re.findall(r'(?:tech(?:nolog(?:y|ies))?[:\s]*|built with[:\s]*|using[:\s]*)(.+?)(?:\.|$)', block, re.IGNORECASE)
        if tech_kw:
            technologies = [t.strip() for t in re.split(r'[,/]', tech_kw[0]) if t.strip()]

        experiences.append(ExperienceInfo(
            company=company[:80],
            title=title[:80],
            duration=duration,
            description=description[:400],
            technologies=technologies,
        ))
    return experiences[:10]


def _extract_education(text: str) -> list[EducationInfo]:
    sections = _split_sections(text)
    edu_text = sections.get("education", "")
    if not edu_text.strip():
        return []
    education = []
    blocks = re.split(r'\n{2,}', edu_text)
    for block in blocks:
        block = block.strip()
        if not block or len(block) < 10:
            continue
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        institution = ""
        degree = ""
        duration = ""
        gpa = ""
        for l in lines:
            if re.search(r'(?:university|institute|college|school|academy|b\.?tech|m\.?tech|b\.?s|m\.?s|bca|mca|bachelor|master|phd|b\.?e|m\.?e)', l, re.IGNORECASE):
                if not institution:
                    institution = l[:120]
                else:
                    degree = l[:120]
            elif re.search(r'20\d{2}\s*[–\-]\s*(?:20\d{2}|present)', l, re.IGNORECASE):
                duration = l
            elif re.search(r'(?:cgpa|gpa|grade|percentage|score)[:\s]*[\d.]+', l, re.IGNORECASE):
                gpa = l
            elif not institution and len(l) < 120:
                institution = l
        education.append(EducationInfo(
            institution=institution,
            degree=degree,
            duration=duration,
            gpa=gpa,
        ))
    return education[:5]


def extract_candidate_info(text: str, filename: str = "") -> CandidateInfo:
    if not text or not text.strip():
        return CandidateInfo(name="Unknown", raw_text=text, filename=filename)

    info = CandidateInfo(raw_text=text)
    info.name = _extract_name(text)
    info.email = _extract_email(text)
    info.phone = _extract_phone(text)
    info.github_url = _extract_github(text)
    info.linkedin_url = _extract_linkedin(text)
    info.skills = _extract_skills(text)
    info.projects = _extract_projects(text)
    info.experience = _extract_experience(text)
    info.education = _extract_education(text)

    tech_line_match = re.search(
        r'(?:languages?|programming)[:\s]*(.+?)(?:\n[A-Z]|\n\n)',
        text, re.IGNORECASE
    )
    if tech_line_match:
        for lang in re.split(r'[,/|]', tech_line_match.group(1)):
            lang = lang.strip().rstrip('.')
            if lang and len(lang) < 30:
                info.languages.append(lang)

    fw_line = re.search(
        r'(?:frameworks?|libraries|technologies)[:\s]*(.+?)(?:\n[A-Z]|\n\n)',
        text, re.IGNORECASE
    )
    if fw_line:
        for fw in re.split(r'[,/|]', fw_line.group(1)):
            fw = fw.strip().rstrip('.')
            if fw and len(fw) < 40:
                info.frameworks.append(fw)

    cert_match = re.search(
        r'(?:certifications?|certificates?|awards?)[:\s]*(.+?)(?:\n[A-Z]|\Z)',
        text, re.IGNORECASE | re.DOTALL
    )
    if cert_match:
        for cert in re.split(r'\n', cert_match.group(1)):
            cert = cert.strip().lstrip('•-–* ')
            if cert and len(cert) > 5:
                info.certifications.append(cert[:120])

    logger.info(f"Extracted info for {info.name or filename}: {len(info.skills)} skills, {len(info.projects)} projects, {len(info.experience)} experiences")
    return info
