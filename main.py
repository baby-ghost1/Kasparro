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


def cmd_screen(args):
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


def cmd_report(args):
    from src.utils.report import print_terminal_report
    print_terminal_report(args.results)


def cmd_serve(args):
    import uvicorn
    print(f"Starting API server on http://0.0.0.0:{args.port}")
    print(f"  POST /screen  — Run screening pipeline")
    print(f"  GET  /results — Get results JSON")
    uvicorn.run("src.api:app", host="0.0.0.0", port=args.port, reload=args.reload)


def is_legacy_syntax():
    """Check if user passed --input or --output without a subcommand."""
    args = sys.argv[1:]
    return len(args) > 0 and not args[0] in ("screen", "report", "serve", "-h", "--help") and any(
        a.startswith("--input") or a.startswith("-i") or a.startswith("--output") or a.startswith("-o")
        for a in args
    )


def main():
    # Legacy support: if --input/--output passed without subcommand, treat as 'screen'
    if is_legacy_syntax():
        sys.argv.insert(1, "screen")

    parser = argparse.ArgumentParser(
        description="AI Resume Screening & Ranking System",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    sp_screen = subparsers.add_parser("screen", help="Run the screening pipeline")
    sp_screen.add_argument("--input", "-i", default="./resumes", help="Input directory with resumes")
    sp_screen.add_argument("--output", "-o", default="./output/results.json", help="Output JSON path")
    sp_screen.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    sp_report = subparsers.add_parser("report", help="Show terminal report")
    sp_report.add_argument("--results", "-r", default="./output/results.json", help="Results JSON path")

    sp_serve = subparsers.add_parser("serve", help="Start FastAPI server")
    sp_serve.add_argument("--port", "-p", type=int, default=8000, help="Port number")
    sp_serve.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()

    if args.command == "screen":
        cmd_screen(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "serve":
        cmd_serve(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
