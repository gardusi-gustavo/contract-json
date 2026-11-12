#!/usr/bin/env python3
"""Token registry and workspace tooling for the github/<prefix>/<repo> layout.

Secrets live in ``~/.config/gh/domains/<domain>/hosts.yml``. This tool only
reads and writes the non-secret metadata registry (``~/.config/gh/registry.json``).

Typical use:

    workspace.py init --root ~/github
    workspace.py list
    workspace.py check
    workspace.py verify --workflows
    workspace.py add contracts --token-file ~/.gh-token-contracts --expires 2026-12-11
    workspace.py clone

Environment variables:

    WORKSPACE_GH_REGISTRY  override the registry path
    GH_HOME                override the ~/.config/gh root
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys
import time

GH_HOME = pathlib.Path(os.environ.get("GH_HOME", pathlib.Path.home() / ".config" / "gh"))
REGISTRY = pathlib.Path(
    os.environ.get("WORKSPACE_GH_REGISTRY", GH_HOME / "registry.json")
)
PROBE_BRANCH = "__token-probe"
PROBE_TIMEOUT = 180


def probe_identity() -> list[str]:
    """Use the repository identity when configured, otherwise a throwaway one."""
    name = subprocess.run(["git", "config", "user.name"], text=True, capture_output=True)
    mail = subprocess.run(["git", "config", "user.email"], text=True, capture_output=True)
    if name.returncode == 0 and mail.returncode == 0 and name.stdout.strip():
        return ["-c", f"user.name={name.stdout.strip()}", "-c", f"user.email={mail.stdout.strip()}"]
    return ["-c", "user.name=token-probe", "-c", "user.email=token-probe@users.noreply.github.com"]


def load() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def save(reg: dict) -> None:
    REGISTRY.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
    os.chmod(REGISTRY, 0o600)


def run(args: list[str], cwd: pathlib.Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        args, cwd=cwd, text=True, capture_output=True, timeout=PROBE_TIMEOUT
    )


def last(stderr: str) -> str:
    lines = [line.strip() for line in (stderr or "").splitlines() if line.strip()]
    return lines[-1][:160] if lines else ""


def selected(reg: dict, wanted: list[str]) -> list[dict]:
    return [d for d in reg["domains"] if not wanted or d["domain"] in wanted]


def cmd_list(reg: dict, _args: argparse.Namespace) -> int:
    today = dt.date.today()
    print(f"{'DOMAIN':11} {'REPOS':>5} {'WRITE':6} {'WORKFLOWS':10} {'EXPIRES':10} {'DAYS':>4}  NAME")
    for d in reg["domains"]:
        exp = dt.date.fromisoformat(d["expires"]) if d.get("expires") else None
        days = (exp - today).days if exp else "-"
        write = "ok" if d.get("write_ok") else ("fail" if d.get("write_ok") is False else "-")
        print(
            f"{d['domain']:11} {len(d['repos']):>5} {write:6} "
            f"{d.get('workflows_permission', '?'):10} {d.get('expires', '-'):10} "
            f"{str(days):>4}  {d.get('token_name', '-')}"
        )
    for excluded in reg.get("excluded", []):
        print(
            f"{'EXCLUDED':11} {'-':>5} {'-':6} {'-':10} {'-':10} {'-':>4}  "
            f"{excluded['repo']} ({excluded['auth']})"
        )
    return 0


def cmd_check(reg: dict, _args: argparse.Namespace) -> int:
    today = dt.date.today()
    problems = 0
    for d in reg["domains"]:
        exp = dt.date.fromisoformat(d["expires"]) if d.get("expires") else None
        if exp and (exp - today).days < 14:
            print(f"WARN {d['domain']}: expires in {(exp - today).days} days")
            problems += 1
        if d.get("write_ok") is False:
            print(f"FAIL {d['domain']}: no write access")
            problems += 1
        if d.get("workflows_permission") != "write":
            print(f"WARN {d['domain']}: workflow scope missing (CI file edits will be rejected)")
            problems += 1
        if not pathlib.Path(d["config_dir"]).is_dir():
            print(f"FAIL {d['domain']}: config dir missing {d['config_dir']}")
            problems += 1
    print(f"{problems} warning(s)/failure(s)")
    return 1 if problems else 0


def probe(d: dict, repo: pathlib.Path, workflows: bool) -> dict:
    """Non-destructive write probe: temporary branch, pushed then deleted."""
    result = {"write_ok": False, "workflows_permission": "unverified", "detail": ""}
    if run(["git", "rev-parse", "--verify", "HEAD"], cwd=repo).returncode != 0:
        result["detail"] = "no commits"
        return result
    base = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo).stdout.strip()
    identity = probe_identity()
    run(["git", "checkout", "-q", "-B", PROBE_BRANCH], cwd=repo)
    try:
        run(["git", "commit", "-q", "--allow-empty", "-m", "chore: token probe (temp)", *identity], cwd=repo)
        push = run(["git", "push", "-q", "origin", f"HEAD:refs/heads/{PROBE_BRANCH}"], cwd=repo)
        if push.returncode != 0:
            result["detail"] = last(push.stderr)
            return result
        result["write_ok"] = True
        if workflows:
            wf = repo / ".github" / "workflows" / "__token_probe.yml"
            wf.parent.mkdir(parents=True, exist_ok=True)
            wf.write_text(
                "name: __token_probe\n"
                "on: workflow_dispatch\n"
                "jobs:\n"
                "  noop:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: echo probe\n",
                encoding="utf-8",
            )
            run(["git", "add", ".github/workflows/__token_probe.yml"], cwd=repo)
            run(["git", "commit", "-q", "-m", "chore: workflow probe (temp)", *identity], cwd=repo)
            second = run(["git", "push", "-q", "origin", f"HEAD:refs/heads/{PROBE_BRANCH}"], cwd=repo)
            result["workflows_permission"] = "write" if second.returncode == 0 else "missing"
        return result
    finally:
        if result["write_ok"]:
            run(["git", "push", "-q", "origin", "--delete", PROBE_BRANCH], cwd=repo)
        run(["git", "checkout", "-q", base], cwd=repo)
        run(["git", "branch", "-q", "-D", PROBE_BRANCH], cwd=repo)


def cmd_verify(reg: dict, args: argparse.Namespace) -> int:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    for d in selected(reg, args.domains):
        repo = pathlib.Path(d["repos"][0]["path"])
        if not repo.is_dir():
            print(f"{d['domain']:11} missing clone {repo}")
            continue
        result = probe(d, repo, args.workflows)
        d["write_ok"] = result["write_ok"]
        if result["workflows_permission"] != "unverified":
            d["workflows_permission"] = result["workflows_permission"]
            d["workflows_verified_at"] = now
        d["verified_at"] = now
        print(
            f"{d['domain']:11} write={'ok' if result['write_ok'] else 'FAIL':4} "
            f"workflows={result['workflows_permission']:10} {result['detail']}"
        )
    save(reg)
    return 0


def cmd_add(reg: dict, args: argparse.Namespace) -> int:
    entry = next((x for x in reg["domains"] if x["domain"] == args.domain), None)
    if entry is None:
        print(
            f"unknown domain {args.domain}; known: "
            + ", ".join(x["domain"] for x in reg["domains"]),
            file=sys.stderr,
        )
        return 2
    token = pathlib.Path(args.token_file).read_text(encoding="utf-8").strip()
    config_dir = GH_HOME / "domains" / args.domain
    config_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(config_dir, 0o700)
    env = dict(os.environ, GH_CONFIG_DIR=str(config_dir))
    login = subprocess.run(
        ["gh", "auth", "login", "--with-token", "--hostname", "github.com"],
        input=token + "\n",
        text=True,
        env=env,
        capture_output=True,
    )
    if login.returncode != 0:
        print(f"login failed: {last(login.stderr)}", file=sys.stderr)
        return 1
    for path in config_dir.iterdir():
        os.chmod(path, 0o600)
    entry["config_dir"] = str(config_dir)
    entry["expires"] = args.expires or entry.get("expires")
    entry["status"] = "active"
    entry["write_ok"] = None
    entry["verified_at"] = None
    save(reg)
    print(f"registered {args.domain}; run: workspace.py verify {args.domain}")
    return 0


def cmd_revoke(reg: dict, args: argparse.Namespace) -> int:
    entry = next((x for x in reg["domains"] if x["domain"] == args.domain), None)
    if entry is None:
        print(f"unknown domain {args.domain}", file=sys.stderr)
        return 2
    config_dir = pathlib.Path(entry["config_dir"])
    if config_dir.is_dir():
        subprocess.run(["rm", "-rf", str(config_dir)], check=True)
    entry["status"] = "revoked"
    entry["write_ok"] = False
    save(reg)
    print(f"removed local credentials for {args.domain} (revoke it in the GitHub UI too)")
    return 0


def cmd_init(_reg: dict, args: argparse.Namespace) -> int:
    if REGISTRY.exists() and not args.force:
        print(f"{REGISTRY} already exists (use --force to overwrite)", file=sys.stderr)
        return 1
    manifest = json.loads(pathlib.Path(args.manifest).read_text(encoding="utf-8"))
    root = pathlib.Path(args.root).expanduser()
    registry = {
        "schema": 1,
        "host": manifest.get("host", "github.com"),
        "owner": manifest.get("owner", ""),
        "workspace_root": str(root),
        "config_root": str(GH_HOME / "domains"),
        "created": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "rotation_days": manifest.get("auth", {}).get("rotation_days", 30),
        "domains": [],
        "excluded": manifest.get("excluded", []),
    }
    for domain in manifest["domains"]:
        registry["domains"].append(
            {
                "domain": domain["domain"],
                "folder": domain["prefix"],
                "token_name": domain["domain"],
                "config_dir": str(GH_HOME / "domains" / domain["domain"]),
                "expires": args.expires,
                "permissions": manifest.get("auth", {}).get("required_permissions", []),
                "workflows_permission": "unverified",
                "status": "pending",
                "write_ok": None,
                "verified_at": None,
                "repos": [
                    {
                        "name": name,
                        "github": f"{manifest['owner']}/{name}",
                        "path": str(root / domain["prefix"] / name),
                    }
                    for name in domain["repos"]
                ],
            }
        )
    GH_HOME.mkdir(parents=True, exist_ok=True)
    os.chmod(GH_HOME, 0o700)
    save(registry)
    print(
        f"wrote {REGISTRY}: {len(registry['domains'])} domains, "
        f"{sum(len(d['repos']) for d in registry['domains'])} repos, "
        f"{len(registry['excluded'])} excluded"
    )
    return 0


def cmd_clone(reg: dict, args: argparse.Namespace) -> int:
    made = skipped = failed = 0
    for d in selected(reg, args.domains):
        env = dict(os.environ, GH_CONFIG_DIR=d["config_dir"], GIT_TERMINAL_PROMPT="0")
        for repo in d["repos"]:
            dest = pathlib.Path(repo["path"])
            if (dest / ".git").exists():
                skipped += 1
                continue
            clone = subprocess.run(
                ["gh", "repo", "clone", repo["github"], str(dest), "--", "--quiet"],
                env=env,
                capture_output=True,
                text=True,
            )
            if clone.returncode == 0:
                made += 1
                print(f"  ok   {repo['github']}")
            else:
                failed += 1
                print(f"  FAIL {repo['github']}: {last(clone.stderr)}")
    print(f"cloned={made} skipped={skipped} failed={failed}")
    return 1 if failed else 0


def cmd_helper(reg: dict, args: argparse.Namespace) -> int:
    entry = next((x for x in reg["domains"] if x["domain"] == args.domain), None)
    if entry is None:
        print(f"unknown domain {args.domain}", file=sys.stderr)
        return 2
    os.environ["GH_CONFIG_DIR"] = entry["config_dir"]
    os.execvp("gh", ["gh", "auth", "git-credential", *args.credential_args])


def main() -> int:
    parser = argparse.ArgumentParser(prog="workspace.py", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="show the token registry").set_defaults(fn=cmd_list)
    sub.add_parser("check", help="exit non-zero on stale or incomplete tokens").set_defaults(fn=cmd_check)

    init = sub.add_parser("init", help="create the registry from governance/workspace.json")
    init.add_argument("--manifest", default="governance/workspace.json")
    init.add_argument("--root", default=str(pathlib.Path.home() / "github"))
    init.add_argument("--expires")
    init.add_argument("--force", action="store_true")
    init.set_defaults(fn=cmd_init)

    verify = sub.add_parser("verify", help="probe read/write access per domain")
    verify.add_argument("domains", nargs="*")
    verify.add_argument("--workflows", action="store_true", help="also probe workflow-file writes")
    verify.set_defaults(fn=cmd_verify)

    add = sub.add_parser("add", help="register a token for a domain")
    add.add_argument("domain")
    add.add_argument("--token-file", required=True)
    add.add_argument("--expires")
    add.set_defaults(fn=cmd_add)

    revoke = sub.add_parser("revoke", help="remove local credentials for a domain")
    revoke.add_argument("domain")
    revoke.set_defaults(fn=cmd_revoke)

    clone = sub.add_parser("clone", help="clone missing repositories from the registry")
    clone.add_argument("domains", nargs="*")
    clone.set_defaults(fn=cmd_clone)

    helper = sub.add_parser("helper", help="git credential helper (internal)")
    helper.add_argument("domain")
    helper.add_argument("credential_args", nargs=argparse.REMAINDER)
    helper.set_defaults(fn=cmd_helper)

    args = parser.parse_args()
    if args.command == "init":
        return args.fn({}, args)
    return args.fn(load(), args)


if __name__ == "__main__":
    raise SystemExit(main())
