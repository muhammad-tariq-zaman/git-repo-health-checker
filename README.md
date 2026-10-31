# git-repo-health-checker

Score a git repository's health from its working tree, untracked files and last-commit age — a quick hygiene check before handover or backup.

## How to run

```sh
python3 main.py /path/to/repo
```

## Example output

```
Score: 100/100 - HEALTHY
- last commit 0 day(s) ago on branch 'master'
```

Standard library only. Run the tests with `python3 -m unittest discover`.
