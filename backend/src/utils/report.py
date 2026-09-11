import json
import sys
from pathlib import Path


def print_terminal_report(results_path: str):
    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    summary = data["batch_summary"]
    eligible = data["eligible_candidates"]
    rejected = data["rejected_candidates"]
    failed = data["failed_candidates"]

    width = 72

    print("=" * width)
    print("  AI RESUME SCREENING — TERMINAL REPORT")
    print("=" * width)

    print(f"\n  {'BATCH SUMMARY':^{width-4}}")
    print("  " + "-" * (width - 4))
    print(f"  Total resumes:       {summary['total_resumes']}")
    print(f"  Successfully parsed: {summary['successfully_parsed']}")
    print(f"  Eligible:            {summary['eligible']}")
    print(f"  Rejected:            {summary['rejected']}")
    print(f"  Failed:              {summary['failed']}")

    if eligible:
        print(f"\n  {'TOP RANKED CANDIDATES':^{width-4}}")
        print("  " + "-" * (width - 4))
        print(f"  {'Rank':<6}{'Name':<30}{'Score':<8}{'AI':<6}{'Py':<6}{'Cloud':<7}{'GH':<6}{'Eng':<5}")
        print("  " + "-" * (width - 4))
        for c in eligible[:15]:
            sb = c["score_breakdown"]
            print(
                f"  #{c['rank']:<5}"
                f"{c['candidate_name'][:28]:<30}"
                f"{c['total_score']:<8}"
                f"{sb['ai_project_depth']:<6}"
                f"{sb['python_backend']:<6}"
                f"{sb['cloud_fullstack']:<7}"
                f"{sb['github']:<6}"
                f"{sb['engineering_depth']:<5}"
            )

        print(f"\n  {'DETAILED TOP 3':^{width-4}}")
        print("  " + "-" * (width - 4))
        for c in eligible[:3]:
            sb = c["score_breakdown"]
            print(f"\n  #{c['rank']} {c['candidate_name']} — Total: {c['total_score']}/100")
            print(f"     Score: AI={sb['ai_project_depth']}/40 | Python={sb['python_backend']}/30 | "
                  f"Cloud={sb['cloud_fullstack']}/15 | GitHub={sb['github']}/10 | Eng={sb['engineering_depth']}/5")
            if c.get("matched_skills"):
                print(f"     Skills: {', '.join(c['matched_skills'][:8])}")
            if c.get("strengths"):
                print(f"     Strengths: {'; '.join(c['strengths'][:3])}")
            if c.get("concerns"):
                print(f"     Concerns: {'; '.join(c['concerns'][:3])}")
            if c.get("project_summary"):
                print(f"     Summary: {c['project_summary'][:90]}")
            gh = c.get("github_enrichment", {})
            if gh.get("has_github"):
                print(f"     GitHub: {gh.get('summary', 'N/A')[:80]}")

    if rejected:
        print(f"\n  {'REJECTED CANDIDATES':^{width-4}}")
        print("  " + "-" * (width - 4))
        for c in rejected:
            reasons = "; ".join(c["rejection_reasons"][:2])
            print(f"  {c['candidate_name'][:35]:<36} {reasons[:50]}")

    if failed:
        print(f"\n  {'FAILED CANDIDATES':^{width-4}}")
        print("  " + "-" * (width - 4))
        for c in failed:
            print(f"  {c['filename']:<36} {c['parsing_error'][:50]}")

    print("\n" + "=" * width)
    print(f"  Full results: {results_path}")
    print("=" * width)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "./data/output/results.json"
    print_terminal_report(path)
