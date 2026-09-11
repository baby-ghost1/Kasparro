# AI Resume Screening & Ranking System

## Overview

A production-minded system that ingests a folder of candidate resumes (PDF), filters candidates against Python/AI eligibility requirements, scores eligible candidates on a 100-point scale, enriches scores with public GitHub activity, and returns a ranked shortlist with explainable scoring.

## Features

- **PDF Resume Ingestion**: Discovers and parses all PDF resumes from an input directory
- **Deterministic Information Extraction**: Extracts name, email, skills, projects, experience, education, and GitHub URL using regex-based parsing
- **Hard Eligibility Filtering**: Rule-based filter requiring genuine Python evidence AND meaningful AI/LLM/RAG/agentic evidence
- **100-Point Scoring Model**: Weighted scoring across 5 categories with explainable evidence
- **Shallow AI Penalty**: Deducts 5-15 points for thin LLM wrappers and tutorial-style projects
- **GitHub Enrichment**: Fetches public GitHub activity and repository data via the GitHub API
- **Graceful Error Handling**: One malformed resume or API failure never crashes the batch
- **Lightweight Caching**: Avoids repeated GitHub API calls for the same user during a run
- **CLI Interface**: Simple command-line interface with `--input` and `--output` flags

## Architecture

```
project/
  main.py                    # CLI entry point
  requirements.txt           # Python dependencies
  .env.example              # Environment variable template
  .gitignore                # Git ignore rules
  README.md                 # This file
  
  resumes/                  # Input directory with candidate PDFs
    candidate_01.pdf
    candidate_02.pdf
    ...
  
  output/                   # Generated output
    results.json            # Screening results
  
  src/                      # Source modules
    __init__.py
    config.py               # Configuration and weights
    models.py               # Pydantic data models
    pipeline.py             # Orchestration logic
    
    ingestion/
      __init__.py
      file_discovery.py     # Resume file discovery
      pdf_parser.py         # PDF text extraction
    
    extraction/
      __init__.py
      extractor.py          # Deterministic resume parsing
    
    screening/
      __init__.py
      eligibility.py        # Hard eligibility filter
      scorer.py             # 100-point scoring model
    
    enrichment/
      __init__.py
      github_enricher.py    # GitHub API enrichment
    
    utils/
      __init__.py
      llm_adapter.py        # LLM abstraction (optional)
  
  tests/                    # Test suite
    __init__.py
    test_eligibility.py     # Eligibility and scoring tests
```

## Setup

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/baby-ghost1/Kasparro.git
cd Kasparro

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | No | empty | OpenAI API key for LLM features |
| `LLM_ENABLED` | No | `false` | Set to `true` to enable LLM-assisted extraction |
| `LLM_MODEL` | No | `gpt-4o-mini` | Model to use for LLM features |
| `GITHUB_TOKEN` | No | empty | GitHub PAT for higher API rate limits |

**Note**: The system works fully without any API keys. LLM and GitHub enrichment are optional enhancements.

## Running the Application

### Basic Usage

```bash
python main.py --input ./resumes --output ./output/results.json
```

### With Verbose Logging

```bash
python main.py --input ./resumes --output ./output/results.json --verbose
```

### Custom Directories

```bash
python main.py --input /path/to/resumes --output /path/to/output/results.json
```

## Output Format

The system generates a JSON file with the following structure:

```json
{
  "batch_summary": {
    "total_resumes": 50,
    "successfully_parsed": 50,
    "eligible": 41,
    "rejected": 9,
    "failed": 0
  },
  "eligible_candidates": [
    {
      "rank": 1,
      "candidate_name": "Yash Maini",
      "eligible": true,
      "total_score": 98,
      "score_breakdown": {
        "ai_project_depth": 40,
        "python_backend": 30,
        "cloud_fullstack": 13,
        "github": 10,
        "engineering_depth": 5,
        "total": 98,
        "evidence": { ... },
        "penalties": []
      },
      "matched_skills": ["Python", "FastAPI", "LangChain", ...],
      "project_summary": "...",
      "github_summary": "...",
      "strengths": ["Strong AI/Agentic project depth", ...],
      "concerns": [],
      "github_enrichment": { ... }
    }
  ],
  "rejected_candidates": [
    {
      "candidate_name": "Kartikay Sinha",
      "eligible": false,
      "rejection_reasons": ["No evidence of Python ..."],
      "matched_skills": ["React", "JavaScript", ...]
    }
  ],
  "failed_candidates": []
}
```

## Eligibility Strategy

A candidate is eligible **only** when both conditions are satisfied:

### 1. Python Evidence (Hard Requirement)

Python must appear as a **genuine** skill, project technology, work technology, or implementation language. The system checks:

- Skills section for "python" or Python-related variants
- Project technologies for Python frameworks (FastAPI, Flask, Django, PyTorch, etc.)
- Work experience descriptions for Python usage
- Context patterns (e.g., "built with Python", "requirements.txt")

A JavaScript/Java/React-only profile without meaningful Python evidence is **rejected**.

### 2. AI/Agentic Evidence (Hard Requirement)

The resume must show at least one meaningful AI/LLM/RAG/agentic project or framework. The system checks for:

- **Frameworks**: LangChain, LangGraph, LlamaIndex, OpenAI, HuggingFace, TensorFlow, PyTorch, etc.
- **Concepts**: RAG, vector search, embeddings, tool calling, multi-agent workflows, evaluation pipelines
- **Project evidence**: AI-related projects with implementation details (not just skill mentions)

Having JavaScript, Java, React, or Next.js alongside Python + AI is **accepted**.

## Scoring Strategy

The 100-point scoring model uses the exact baseline weighting from the assignment:

| Category | Max Points | What It Measures |
|----------|-----------|-----------------|
| AI/Agentic Project Depth | 40 | Quality and depth of AI projects |
| Python & Backend Engineering | 30 | Python skills, frameworks, databases |
| Cloud/Deployment/Full Stack | 15 | Cloud, Docker, frontend breadth |
| GitHub Activity | 10 | Recent activity + maintained repos |
| Engineering Depth | 5 | Testing, caching, observability, etc. |

### AI Project Quality Assessment

The system rewards **implementation evidence** over keyword mentions:

- Multiple AI projects with different frameworks score higher
- RAG/retrieval, agent workflows, evaluation pipelines add depth signals
- Shallow projects (simple LLM API wrappers, tutorial clones) receive 5-15 point penalties
- Framework mentions in Skills without project evidence receive minimal credit

### Project-Quality Penalties

- **5-15 points deducted** for thin LLM/API wrappers with no meaningful workflow
- **Points deducted** for tutorial-style projects without implementation details
- **No full credit** for framework names appearing only in skills sections

## GitHub Enrichment

When a GitHub URL is found in the resume, the system fetches public data via the GitHub API:

- **Recent Activity (0-5 points)**: Public events in the last 90 days (PushEvent, CreateEvent, IssuesEvent, PullRequestEvent)
- **Repos Score (0-5 points)**: Number of maintained public repos, AI-related repos, Python repos
- **Total capped at 10 points**

GitHub failures (rate limit, 404, network error) are gracefully handled and recorded without failing the batch.

### Caching

GitHub API responses are cached in-memory during a run to avoid repeated calls for the same user.

## LLM Usage

LLM integration is **optional** and disabled by default (`LLM_ENABLED=false`). When enabled:

- Uses OpenAI API with structured output (Pydantic schemas)
- Provider-specific code is isolated behind `LLMAdapter`
- API keys come from environment variables only
- LLM failures for individual resumes are caught and recorded without crashing the batch

The system is designed to work well **without** LLM support using deterministic extraction.

## Error Handling

The system is resilient to individual failures:

| Failure Type | Handling |
|-------------|----------|
| Malformed PDF | Recorded as failed, batch continues |
| Empty/unreadable PDF | Recorded as failed, batch continues |
| Missing fields | Defaults to empty strings, batch continues |
| GitHub 404 | Enrichment recorded as failed |
| GitHub rate limit | Enrichment recorded as failed, batch continues |
| GitHub network error | Enrichment recorded as failed, batch continues |
| LLM timeout | LLM error recorded, falls back to deterministic |
| LLM invalid output | LLM error recorded, falls back to deterministic |
| Unexpected exceptions | Caught and logged, batch continues |

## Testing

### Run Tests

```bash
pytest tests/ -v
```

### Test Coverage

The test suite covers:

1. **Python evidence detection**: Python in skills, projects, experience, context
2. **AI evidence detection**: AI frameworks, projects, shallow detection
3. **Eligibility rules**: Python+AI eligible, Python-only rejected, AI-only rejected, JS-only rejected
4. **Score validation**: Total <= 100, categories within bounds, sum equals total
5. **Shallow AI penalties**: Thin wrappers detected and penalized
6. **GitHub handling**: Username extraction, missing URL, API failures
7. **Error resilience**: Malformed/empty resumes don't crash

## Design Decisions

### Filtering Strategy

**Deterministic hard eligibility** was chosen over LLM-based filtering for several reasons:

1. **Predictability**: Rule-based filtering produces consistent, reproducible results
2. **Speed**: No API calls needed for the eligibility gate
3. **Testability**: Easy to verify with unit tests
4. **Transparency**: Rejection reasons are clear and auditable

The eligibility check uses regex-based pattern matching with word boundaries to avoid false positives (e.g., "pipelines" matching "pip"). Python evidence requires genuine presence in skills, projects, or experience - not just AI framework mentions that happen to be Python-based.

### Scoring Strategy

A **deterministic weighted scoring** approach was chosen because:

1. **Explainability**: Every point can be traced to specific resume evidence
2. **Consistency**: Same resume always gets the same score
3. **Tunability**: Weights can be adjusted without retraining
4. **No API dependency**: Works without LLM or external services

The scoring uses the exact assignment weights (40/30/15/10/5) and adds depth signals for AI projects (RAG, agents, evaluation, orchestration) rather than just counting framework mentions.

### LLM Usage

LLM is **optional and isolated** because:

1. The assignment encourages it but doesn't require it
2. Deterministic extraction works well for structured resume data
3. LLM adds latency and cost without guaranteed improvement
4. The adapter pattern allows easy provider swapping

### GitHub Scoring

GitHub enrichment uses a simple **activity + repository quality** model:

- **Activity score (0-5)**: Based on recent public events in the last 90 days
- **Repository score (0-5)**: Based on maintained repos, AI-related repos, Python repos
- Total capped at 10 as specified in the assignment

This approach is lightweight, explainable, and avoids complex heuristics.

## Trade-offs

1. **Deterministic vs. LLM parsing**: Chose deterministic for reliability and speed; LLM would improve semantic understanding of project descriptions
2. **Regex vs. NLP extraction**: Regex is simpler and faster but less robust for unusual resume formats
3. **Synchronous vs. async processing**: Chose synchronous for simplicity; async would improve throughput for 50+ resumes
4. **In-memory vs. persistent caching**: In-memory is simpler; persistent caching would help across runs
5. **No database**: JSON output is sufficient per assignment requirements

## If I Had More Time

1. **LLM-Enhanced Project Analysis**: Use an LLM to deeply analyze project descriptions for implementation quality, distinguishing genuine multi-step AI workflows from thin wrappers with higher accuracy than regex patterns

2. **Async/Concurrent Processing**: Implement `asyncio`-based concurrent resume processing with bounded concurrency (e.g., 10 concurrent requests) to significantly reduce total processing time, especially when GitHub/LLM enrichment is enabled

3. **Persistent Caching with SQLite**: Add a lightweight SQLite cache for GitHub API responses and LLM results so that re-running the pipeline doesn't re-fetch data for candidates already processed

4. **Interactive Terminal Report**: Build a rich terminal report using `rich` library showing a color-coded dashboard with top candidates, score breakdowns, and rejection reasons for quick recruiter review
