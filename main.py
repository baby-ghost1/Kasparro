import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.pipeline import run_pipeline


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    parser = argparse.ArgumentParser(
        description="AI Resume Screening & Ranking System",
    )
    parser.add_argument(
        "--input", "-i",
        default="./resumes",
        help="Path to directory containing resume PDFs (default: ./resumes)",
    )
    parser.add_argument(
        "--output", "-o",
        default="./output/results.json",
        help="Path for output JSON file (default: ./output/results.json)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose/debug logging",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("AI Resume Screening & Ranking System")
    logger.info("=" * 60)

    config = Config()
    logger.info(f"LLM enabled: {config.llm_enabled}")
    logger.info(f"GitHub token configured: {'yes' if config.github_token else 'no'}")

    result = run_pipeline(args.input, args.output, config)

    summary = result.batch_summary
    print("\n" + "=" * 60)
    print("BATCH SUMMARY")
    print("=" * 60)
    print(f"  Total resumes:      {summary.total_resumes}")
    print(f"  Successfully parsed: {summary.successfully_parsed}")
    print(f"  Eligible:           {summary.eligible}")
    print(f"  Rejected:           {summary.rejected}")
    print(f"  Failed:             {summary.failed}")
    print("=" * 60)

    if result.candidates:
        print("\nTOP RANKED CANDIDATES:")
        print("-" * 60)
        for c in result.candidates[:10]:
            print(f"  #{c.rank} {c.candidate_name} (Score: {c.total_score})")
            print(f"     AI: {c.score_breakdown.ai_project_depth}/40 | "
                  f"Python: {c.score_breakdown.python_backend}/30 | "
                  f"Cloud: {c.score_breakdown.cloud_fullstack}/15 | "
                  f"GitHub: {c.score_breakdown.github}/10 | "
                  f"Eng: {c.score_breakdown.engineering_depth}/5")
            if c.strengths:
                print(f"     Strengths: {'; '.join(c.strengths[:3])}")
            print()

    if result.rejected:
        print(f"\nREJECTED CANDIDATES ({len(result.rejected)}):")
        print("-" * 60)
        for c in result.rejected:
            reasons = '; '.join(c.rejection_reasons[:2])
            print(f"  {c.candidate_name or c.filename}: {reasons}")

    if result.failed:
        print(f"\nFAILED CANDIDATES ({len(result.failed)}):")
        print("-" * 60)
        for c in result.failed:
            print(f"  {c.filename}: {c.parsing_error}")

    print(f"\nResults written to: {args.output}")


if __name__ == "__main__":
    main()
