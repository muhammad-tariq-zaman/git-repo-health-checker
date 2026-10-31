"""Score a git repository's health: clean tree, recent commits, branch.

Usage: python3 main.py /path/to/repo [--stale-days 90]
Score starts at 100: -20 for uncommitted changes, -20 for untracked files,
-10 when the last commit is older than the stale threshold.
"""
import argparse
import subprocess
import sys
from datetime import date


def run_git(path, args):
    result = subprocess.run(["git", "-C", path] + args, capture_output=True, text=True, timeout=30)
    return result.stdout.strip(), result.returncode


def health(path, stale_days=90, today=None):
    today = today or date.today()
    _, code = run_git(path, ["rev-parse", "--is-inside-work-tree"])
    if code != 0:
        return {"score": 0, "verdict": "NOT A REPO", "details": ["not a git repository"]}
    status, _ = run_git(path, ["status", "--porcelain"])
    changed = [line for line in status.splitlines() if line and not line.startswith("??")]
    untracked = [line for line in status.splitlines() if line.startswith("??")]
    branch, _ = run_git(path, ["branch", "--show-current"])
    log, code = run_git(path, ["log", "-1", "--format=%ct"])
    details, score = [], 100
    if changed:
        score -= 20
        details.append(f"{len(changed)} uncommitted change(s)")
    if untracked:
        score -= 20
        details.append(f"{len(untracked)} untracked file(s)")
    if code == 0 and log:
        age_days = (today - date.fromtimestamp(int(log))).days
        details.append(f"last commit {age_days} day(s) ago on branch '{branch or 'detached'}'")
        if age_days > stale_days:
            score -= 10
            details.append(f"stale: last commit older than {stale_days} days")
    else:
        details.append("no commits yet")
    verdict = "HEALTHY" if score >= 80 else ("NEEDS ATTENTION" if score >= 50 else "AT RISK")
    return {"score": max(score, 0), "verdict": verdict, "details": details}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Path to a git repository")
    parser.add_argument("--stale-days", type=int, default=90)
    args = parser.parse_args(argv)
    result = health(args.path, args.stale_days)
    print(f"Score: {result['score']}/100 - {result['verdict']}")
    for detail in result["details"]:
        print(f"- {detail}")
    return 0 if result["verdict"] == "HEALTHY" else 1


if __name__ == "__main__":
    sys.exit(main())
