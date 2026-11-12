#!/usr/bin/env python3
"""Capture a chat summary as a parent issue, or fan it out into child issues.

Parent issues live in the profile repository. Children live in work repositories,
one issue per repository and outcome. The queue policy comes from
``governance/operating.json`` and is applied per repository:

* profile inbox: resume at 80, pause at 100;
* work repository: resume at 15, pause at 20.

Usage:

    inbox.py --input parent.json
    inbox.py --input children.json --parent 42
    inbox.py --input parent.json --dry-run
    inbox.py --input parent.json --discard
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys

GH_HOME = pathlib.Path(os.environ.get("GH_HOME", pathlib.Path.home() / ".config" / "gh"))
REGISTRY = GH_HOME / "registry.json"
OVERFLOW = GH_HOME / "inbox-overflow.jsonl"
POLICY = pathlib.Path(
    os.environ.get(
        "OPERATING_POLICY",
        pathlib.Path(__file__).resolve().parents[1] / "governance" / "operating.json",
    )
)
OWNER = os.environ.get("GITHUB_OWNER", "gardusi-gustavo")


def load_json(path: pathlib.Path, default: dict) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def policy() -> dict:
    return load_json(POLICY, {})


def inbox_repo() -> str:
    return policy().get("inbox", {}).get("repository", f"{OWNER}/gardusi-gustavo")


def gh_env(repo_name: str) -> dict[str, str]:
    env = dict(os.environ)
    registry = load_json(REGISTRY, {})
    for domain in registry.get("domains", []):
        for repo in domain.get("repos", []):
            if repo["name"] == repo_name:
                env["GH_CONFIG_DIR"] = domain["config_dir"]
                return env
    return env


def gh(args: list[str], env: dict[str, str], stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["gh", *args], input=stdin, text=True, env=env, capture_output=True, timeout=120
    )


def last(stderr: str) -> str:
    lines = [line.strip() for line in (stderr or "").splitlines() if line.strip()]
    return lines[-1][:160] if lines else ""


def slug(entry: dict, parent: int | None) -> str:
    if parent:
        if not entry.get("repo"):
            raise ValueError("child issue needs a repo")
        repo = entry["repo"]
        return repo if "/" in repo else f"{OWNER}/{repo}"
    repo = entry.get("repo")
    if not repo or repo == "unknown":
        repo = inbox_repo()
    return repo if "/" in repo else f"{OWNER}/{repo}"


def repo_name(repo: str) -> str:
    return repo.split("/")[-1]


def open_issue_count(repo: str, env: dict[str, str]) -> int:
    result = gh(
        ["api", "-X", "GET", "search/issues",
         "-f", f"q=is:issue is:open repo:{repo}", "--jq", ".total_count"],
        env,
    )
    try:
        return int(result.stdout.strip() or 0)
    except ValueError:
        return 0


def limits(repo: str) -> tuple[int, int]:
    queues = policy().get("queues", {})
    if repo == inbox_repo():
        config = queues.get("inbox", {})
        return int(config.get("resume", 80)), int(config.get("pause", 100))
    config = queues.get("per_repo", {})
    return int(config.get("resume", 15)), int(config.get("pause", 20))


def bullets(values) -> str:
    if not values:
        return "- none"
    if isinstance(values, str):
        values = [values]
    return "\n".join(f"- {value}" for value in values)


def parent_body(entry: dict) -> str:
    return (
        f"## Summary\n\n{entry.get('summary') or entry.get('outcome', '')}\n\n"
        f"## Decisions\n\n{bullets(entry.get('decisions'))}\n\n"
        f"## Open questions\n\n{bullets(entry.get('open_questions'))}\n\n"
        f"## Actions\n\n{bullets(entry.get('actions'))}\n\n"
        f"---\nsource: chat · kind: {entry.get('kind', 'idea')} · "
        f"priority: {entry.get('priority', 'P2')}\n"
    )


def child_body(entry: dict, parent: int) -> str:
    group = entry.get("group")
    depends = entry.get("depends_on") or []
    links = [f"Parent: #{parent}"]
    if group:
        links.append(f"Group: `{group}`")
    if depends:
        links.append("Depends on: " + ", ".join(f"#{number}" for number in depends))
    return (
        f"## Problem\n\n{entry['outcome']}\n\n"
        f"## Rationale\n\n{entry.get('rationale', '')}\n\n"
        f"## Evidence\n\n{bullets(entry.get('evidence'))}\n\n"
        f"## Acceptance\n\n{bullets(entry.get('acceptance'))}\n\n"
        f"## Non-goals\n\n{bullets(entry.get('non_goals'))}\n\n"
        f"## Rollback\n\n{entry.get('rollback', 'Revert the pull request.')}\n\n"
        f"---\n" + " · ".join(links) + "\n"
    )


def wanted_labels(entry: dict, repo: str, parent: int | None) -> list[str]:
    prefix = repo_name(repo).split("-")[0]
    labels = [
        "source:chat",
        f"kind:{entry.get('kind', 'idea')}",
        f"priority:{entry.get('priority', 'P2')}",
        f"domain:{prefix}",
    ]
    if parent:
        labels.append("stage:triaged")
        if entry.get("size"):
            labels.append(f"size:{entry['size']}")
    else:
        labels.append("stage:captured")
    return labels


def existing_labels(repo: str, env: dict[str, str]) -> set[str]:
    result = gh(["label", "list", "--repo", repo, "--json", "name", "--limit", "100"], env)
    if result.returncode != 0:
        return set()
    return {item["name"] for item in json.loads(result.stdout or "[]")}


def create(entry: dict, repo: str, parent: int | None, env: dict[str, str], dry_run: bool) -> int:
    label_names = [name for name in wanted_labels(entry, repo, parent)
                   if name in existing_labels(repo, env)]
    body = child_body(entry, parent) if parent else parent_body(entry)
    args = ["issue", "create", "--repo", repo,
            "--title", entry["title"], "--body", body]
    for label in label_names:
        args += ["--label", label]
    if dry_run:
        print(f"[dry-run] create issue in {repo}: {entry['title']} labels={label_names}")
        print(body)
        return 0
    result = gh(args, env)
    if result.returncode != 0:
        print(last(result.stderr), file=sys.stderr)
        return 1
    print(result.stdout.strip())
    return 0


def defer(entry: dict, repo: str, parent: int | None, total: int, cap: int,
          env: dict[str, str], dry_run: bool) -> int:
    message = f"deferred: {repo} at {total}/{cap}"
    if parent:
        if dry_run:
            print(f"[dry-run] comment on parent #{parent}: {message}")
            return 0
        target_env = gh_env(repo_name(inbox_repo()))
        result = gh(["issue", "comment", str(parent), "--repo", inbox_repo(),
                     "--body", f"{message}\n\n{entry.get('title', '')}"], target_env)
        print(result.stdout.strip() or last(result.stderr))
        return 0 if result.returncode == 0 else 1
    park(entry, message, dry_run)
    return 0


def park(entry: dict, reason: str, dry_run: bool) -> None:
    if dry_run:
        print(f"[dry-run] park: {reason} :: {entry.get('title', '')}")
        return
    OVERFLOW.parent.mkdir(parents=True, exist_ok=True)
    record = dict(entry)
    record["parked_at"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    record["reason"] = reason
    with OVERFLOW.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
    os.chmod(OVERFLOW, 0o600)
    print(f"parked: {reason} -> {OVERFLOW}")


REQUIRED_PARENT = ("title", "summary")
REQUIRED_CHILD = ("title", "repo", "outcome", "acceptance")


def handle(entry: dict, args: argparse.Namespace, cache: dict) -> int:
    parent = args.parent or entry.get("parent")
    parent = int(parent) if parent else None
    required = REQUIRED_CHILD if parent else REQUIRED_PARENT
    missing = [key for key in required if not entry.get(key)]
    if missing:
        print(f"missing fields: {', '.join(missing)}", file=sys.stderr)
        return 2
    if args.discard or entry.get("kind") == "question":
        print(f"discarded: {entry['title']}")
        return 0

    repo = slug(entry, parent)
    env = gh_env(repo_name(repo))
    if repo not in cache:
        cache[repo] = open_issue_count(repo, env)
    total = cache[repo]
    resume, pause = limits(repo)

    if total >= resume:
        return defer(entry, repo, parent, total, pause, env, args.dry_run)

    return create(entry, repo, parent, env, args.dry_run)


def main() -> int:
    parser = argparse.ArgumentParser(prog="inbox.py", description=__doc__)
    parser.add_argument("--input", default="-", help="JSON file, or - for stdin")
    parser.add_argument("--parent", type=int, help="parent issue number in the profile repo")
    parser.add_argument("--discard", action="store_true", help="drop the entry")
    parser.add_argument("--dry-run", action="store_true", help="print the action only")
    args = parser.parse_args()

    raw = sys.stdin.read() if args.input == "-" else pathlib.Path(args.input).read_text(encoding="utf-8")
    data = json.loads(raw)
    if isinstance(data, dict) and "children" in data:
        args.parent = args.parent or data.get("parent")
        entries = data["children"]
    elif isinstance(data, list):
        entries = data
    else:
        entries = [data]

    cache: dict[str, int] = {}
    failures = 0
    for entry in entries:
        try:
            failures += handle(entry, args, cache)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
