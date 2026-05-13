from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from authenticity_lab.evaluation import run_evaluation, write_reports


def main() -> None:
    parser = argparse.ArgumentParser(description="Run authenticity lab evaluation fixtures.")
    parser.add_argument("--ai-mode", default="heuristic", choices=["heuristic", "pretrained"])
    parser.add_argument("--output-dir", default="evaluation")
    args = parser.parse_args()

    payload = run_evaluation(root=ROOT, ai_mode=args.ai_mode)
    json_path, md_path = write_reports(payload, ROOT / args.output_dir)
    print(f"Wrote {json_path.relative_to(ROOT)}")
    print(f"Wrote {md_path.relative_to(ROOT)}")
    print(f"Passed {payload['summary']['passed']} / {payload['summary']['cases']} cases")


if __name__ == "__main__":
    main()
