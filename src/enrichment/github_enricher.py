import re
import json
import logging
import urllib.request
import urllib.error
from datetime import datetime, timezone
from src.config import Config
from src.models import GitHubEnrichment

logger = logging.getLogger(__name__)


def _extract_username(github_url: str) -> str:
    m = re.search(r'github\.com/([A-Za-z0-9_.-]+)', github_url)
    if m:
        return m.group(1).rstrip('/')
    return ""


def _github_api_get(url: str, config: Config, timeout: int = 10) -> dict | list | None:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Resume-Screening-Bot/1.0",
    }
    if config.github_token:
        headers["Authorization"] = f"token {config.github_token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
            else:
                logger.warning(f"GitHub API returned {resp.status} for {url}")
                return None
    except urllib.error.HTTPError as e:
        if e.code == 404:
            logger.info(f"GitHub 404 for {url}")
        elif e.code == 403:
            logger.warning(f"GitHub rate limit hit for {url}")
        else:
            logger.warning(f"GitHub HTTP error {e.code} for {url}")
        return None
    except urllib.error.URLError as e:
        logger.warning(f"GitHub network error for {url}: {e}")
        return None
    except Exception as e:
        logger.warning(f"GitHub request failed for {url}: {e}")
        return None


def _get_recent_events(username: str, config: Config) -> list[dict]:
    url = f"https://api.github.com/users/{username}/events/public?per_page=30"
    result = _github_api_get(url, config, timeout=config.github_request_timeout)
    return result if isinstance(result, list) else []


def _get_repos(username: str, config: Config) -> list[dict]:
    url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=20"
    result = _github_api_get(url, config, timeout=config.github_request_timeout)
    return result if isinstance(result, list) else []


def _calculate_recent_activity_score(events: list[dict], config: Config) -> tuple[int, list[str]]:
    max_pts = config.github_recent_activity_max
    if not events:
        return 0, ["No recent public activity found"]

    now = datetime.now(timezone.utc)
    recent_count = 0
    activity_labels = []
    cutoff_days = 90

    for event in events:
        created_at = event.get("created_at", "")
        if created_at:
            try:
                event_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                days_ago = (now - event_date).days
                if days_ago <= cutoff_days:
                    recent_count += 1
                    event_type = event.get("type", "")
                    repo_name = event.get("repo", {}).get("name", "")
                    if event_type in ("PushEvent", "CreateEvent", "IssuesEvent", "PullRequestEvent"):
                        activity_labels.append(f"{event_type} on {repo_name} ({days_ago}d ago)")
            except (ValueError, TypeError):
                continue

    if recent_count >= 15:
        score = 5
    elif recent_count >= 10:
        score = 4
    elif recent_count >= 5:
        score = 3
    elif recent_count >= 2:
        score = 2
    elif recent_count >= 1:
        score = 1
    else:
        score = 0

    return min(score, max_pts), activity_labels[:5]


def _calculate_repos_score(repos: list[dict], config: Config) -> tuple[int, list[str], list[str]]:
    max_pts = config.github_repos_max
    if not repos:
        return 0, [], ["No public repositories found"]

    ai_keywords = ["ai", "llm", "rag", "agent", "ml", "deep", "neural", "nlp", "chatbot",
                    "langchain", "openai", "tensorflow", "pytorch", "embedding", "vector"]
    python_keywords = ["python", "fastapi", "flask", "django", "pytorch", "pandas"]

    maintained_repos = []
    ai_repos = []
    python_repos = []

    for repo in repos:
        name = repo.get("name", "")
        desc = (repo.get("description") or "").lower()
        lang = (repo.get("language") or "").lower()
        topics = [t.lower() for t in repo.get("topics", [])]
        stars = repo.get("stargazers_count", 0)
        updated = repo.get("updated_at", "")
        forks = repo.get("forks_count", 0)

        combined = f"{name} {desc} {' '.join(topics)}"

        is_maintained = stars > 0 or forks > 0 or any(kw in combined for kw in ai_keywords + python_keywords)
        if is_maintained:
            maintained_repos.append(name)

        if any(kw in combined for kw in ai_keywords) or lang in ("jupyter notebook",):
            ai_repos.append(name)
        if any(kw in combined for kw in python_keywords) or lang == "python":
            python_repos.append(name)

    repo_score = 0
    evidence = []

    if len(maintained_repos) >= 5:
        repo_score += 3
        evidence.append(f"{len(maintained_repos)} maintained repos")
    elif len(maintained_repos) >= 3:
        repo_score += 2
        evidence.append(f"{len(maintained_repos)} maintained repos")
    elif len(maintained_repos) >= 1:
        repo_score += 1
        evidence.append(f"{len(maintained_repos)} maintained repo(s)")

    if ai_repos:
        repo_score += min(len(ai_repos), 2)
        evidence.append(f"{len(ai_repos)} AI-related repos")
    if python_repos:
        repo_score += min(len(python_repos), 1)
        evidence.append(f"{len(python_repos)} Python repos")

    return min(repo_score, max_pts), evidence, maintained_repos[:5]


def enrich_github(github_url: str, config: Config) -> GitHubEnrichment:
    if not github_url:
        return GitHubEnrichment(
            has_github=False,
            summary="No GitHub URL found in resume",
        )

    username = _extract_username(github_url)
    if not username:
        return GitHubEnrichment(
            has_github=False,
            profile_url=github_url,
            summary="Could not extract GitHub username",
            error="Invalid GitHub URL format",
        )

    enrichment = GitHubEnrichment(
        has_github=True,
        username=username,
        profile_url=f"https://github.com/{username}",
    )

    events = _get_recent_events(username, config)
    activity_score, activity_labels = _calculate_recent_activity_score(events, config)
    enrichment.recent_activity_score = activity_score
    enrichment.recent_activity = activity_labels

    repos = _get_repos(username, config)
    repo_score, repo_evidence, recent_repos = _calculate_repos_score(repos, config)
    enrichment.repos_score = repo_score
    enrichment.recent_repos = recent_repos

    enrichment.total_score = min(activity_score + repo_score, config.github_repos_max + config.github_recent_activity_max)
    enrichment.total_score = min(enrichment.total_score, 10)

    parts = []
    if activity_labels:
        parts.append(f"Recent activity: {activity_score}/5")
    if repo_evidence:
        parts.append(f"Repos: {', '.join(repo_evidence)}")
    if not parts:
        parts.append("Limited GitHub activity")
    enrichment.summary = "; ".join(parts)

    return enrichment
