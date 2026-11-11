# Local workspace

Conventions for keeping the 43 public repositories of `gardusi-gustavo` on a single
machine, addressed by prefix, with one credential per domain.

The authoritative repository list is [repos.json](https://github.com/gardusi-gustavo/contract-json/blob/main/governance/repos.json).
The machine-readable form of this runbook is [workspace.json](https://github.com/gardusi-gustavo/contract-json/blob/main/governance/workspace.json).

## Layout

```text
~/github/
├── contract/     contract-json, contract-proto, contract-graphql, contract-openapi, contract-sql
├── dashboard/    dashboard-devops, dashboard-lottery, dashboard-news, dashboard-stocks, dashboard-wiki
├── database/     database-devops, database-lottery, database-news, database-stocks, database-wiki
├── game/         game-crosswords, game-logic-grid, game-sudoku
├── package/      package-cpp … package-zig (20 repositories)
├── workflow/     workflow-event, workflow-manual, workflow-scheduled
└── meta/         .github, gardusi-gustavo
```

Rule: `github/<prefix>/<repo>`, where `<prefix>` is the singular repository prefix.
There is no `private/` directory; see [Private boundary](#private-boundary).

## Authentication model

One fine-grained personal access token per domain, named after the domain
(`contracts`, `dashboards`, `databases`, `games`, `packages`, `workflows`, `github`).

- Repository access: **only select repositories**, never `private`.
- Required permissions: `Contents`, `Pull requests`, `Issues`, `Workflows` → write;
  `Metadata` → read.
- `Administration` is never granted, so a token cannot delete a repository.
- Tokens expire every 30 days; renew and re-register before expiry.

Each domain gets its own GitHub CLI config directory, which allows all seven
credentials to coexist:

```text
~/.config/gh/
├── domains/<domain>/hosts.yml   # token, mode 600
├── registry.json                # non-secret metadata: name, repos, expiry, probe results
└── bin/
    ├── ghd                      # optional: run gh as a domain
    └── workspace                # optional: symlink to scripts/workspace.py
```

Repository-local credential helpers point at the owning domain:

```bash
git config --local credential.https://github.com.helper \
  '!<absolute-path>/scripts/workspace.py helper <domain>'
```

so ordinary `git fetch` and `git push` pick the correct token without environment juggling.

## Bootstrap

Run the commands below from a clone of this repository; `scripts/workspace.py`
is the tool that maintains the local registry.

1. Create the workspace root and prefix directories:

   ```bash
   mkdir -p ~/github/{contract,dashboard,database,game,package,workflow,meta}
   ```

2. Create the local registry from the manifest (refuses to overwrite without `--force`):

   ```bash
   python3 scripts/workspace.py init --root ~/github --expires 2026-12-11
   ```

3. Register one token per domain. The token is read from a file, never from argv:

   ```bash
   python3 scripts/workspace.py add contracts --token-file ~/.gh-token-contracts --expires 2026-12-11
   ```

4. Clone everything that is not already present:

   ```bash
   python3 scripts/workspace.py clone
   ```

5. Verify read and write access against every domain:

   ```bash
   python3 scripts/workspace.py verify --workflows
   ```

`clone` and `verify` only operate on the repositories listed in `workspace.json`.
Entries without a domain, such as `private`, are skipped.

Optional short alias:

```bash
ln -sf "$PWD/scripts/workspace.py" ~/.config/gh/bin/workspace
```

## Daily use

```bash
python3 scripts/workspace.py list        # token status table
python3 scripts/workspace.py check       # non-zero on missing write, missing workflow scope, or expiry < 14 days
ghd packages gh pr list                  # run gh with the packages credential
ghd meta gh repo view .github            # "meta" resolves to the github domain
```

Plain `git` commands work in any clone because of the local credential helper.

## Token registry

The registry records only metadata: token name, domain, repository list, expiry,
last verification time, and the result of a non-destructive write probe.
Token values stay in `hosts.yml` and are never committed.

A write probe creates a temporary branch with an empty commit, pushes it, and
deletes it. A workflow probe additionally pushes a throwaway workflow file and
removes the branch. Both probes leave the default branch untouched.

## Private boundary

`gardusi-gustavo/private` is excluded from the local workspace:

- no personal access token covers it;
- `private` is never cloned or pushed from this machine;
- manual updates happen in a GitHub Codespace, where the scoped
  `GITHUB_TOKEN` already has access;
- the registry records the exclusion with `"auth": "codespaces"`.

## Troubleshooting

`refusing to allow a Personal Access Token to create or update workflow` means the
token lacks the `Workflows` permission. Add `Workflows: Read and write` to that
token in the GitHub UI, then run `verify --workflows`; editing permissions does not
change the token value.

`403` on push but `200` on read means the repository is not in the token's
selected set. Public repositories are readable by every fine-grained token, so a
clone can succeed while the first push fails.

## Related

- [Repository bootstrap](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/repository-bootstrap.md)
- [Workspace manifest](https://github.com/gardusi-gustavo/contract-json/blob/main/governance/workspace.json)
- [Repository inventory](https://github.com/gardusi-gustavo/contract-json/blob/main/governance/repos.json)
- [Workspace tool](https://github.com/gardusi-gustavo/contract-json/blob/main/scripts/workspace.py)
