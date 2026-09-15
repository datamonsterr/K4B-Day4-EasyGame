"""Append one measured run to the experiment ledger; never overwrite run evidence."""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--author", required=True)
    parser.add_argument("--hypothesis", required=True)
    parser.add_argument("--change", required=True)
    args = parser.parse_args()
    run = json.loads(args.run.read_text())
    path = ROOT / "artifacts/version_log.csv"
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    run_file = args.run.resolve().relative_to(ROOT).as_posix()
    if any(row["run_file"] == run_file for row in rows):
        raise SystemExit("Run already logged")
    previous = next((row for row in reversed(rows) if row["metric_name"] == "case_accuracy" and row["reason"].startswith(f"suite={run['suite']};")), None)
    summary = run["summary"]
    valid = summary["provider_error_cases"] == 0 and summary["measured_cases"] == summary["total_cases"]
    row = dict(version=run["version"], author=args.author, changed_artifact=args.change,
               artifact_version=run["artifact_version"], prompt_hash=run["prompt_hash"], tools_hash=run["tools_hash"],
               reason=f"suite={run['suite']}; measured={summary['measured_cases']}/{summary['total_cases']}; provider_errors={summary['provider_error_cases']}; passed={summary['passed_cases']}",
               hypothesis=args.hypothesis, metric_name="case_accuracy" if valid else "INVALID_partial_case_accuracy",
               metric_before=previous["metric_after"] if previous else "", metric_after=summary["case_accuracy"], run_file=run_file)
    with path.open("a", newline="") as stream:
        csv.DictWriter(stream, fieldnames=fields).writerow(row)
    print(row["reason"])


if __name__ == "__main__":
    main()
