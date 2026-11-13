# Local workspace

Conventions for keeping the 46 repositories on one machine, with SSH for the
operator and the built-in `GITHUB_TOKEN` for workflows.

## Layout

```text
~/github/
├── contract/     contract-json, contract-proto, contract-graphql, contract-openapi, contract-sql, contract-wit
├── dashboard/    dashboard-devops, dashboard-lottery, dashboard-news, dashboard-stocks, dashboard-wiki
├── database/     database-devops, database-lottery, database-news, database-stocks, database-wiki
├── game/         game-crosswords, game-logic-grid, game-sudoku
├── package/      package-cpp … package-zig (21 repositories)
├── meta/         package-yml, gardusi-gustavo
└── private/      optional, operator-only (SSH)
```

Rule: `github/<prefix>/<repo>`. There is no automation access to `private`.

## Credentials

| Identity | Method | Used for |
| --- | --- | --- |
| operator | SSH ed25519 | clone, push, tags, workflow files |
| workflows | `GITHUB_TOKEN` | everything inside a repository |

- No personal access tokens.
- No GitHub Apps.
- No cross-repository credentials.

SSH key: `~/.ssh/id_ed25519_github`, registered under **Settings → SSH and GPG keys**.

## Clone

```bash
mkdir -p ~/github/{contract,dashboard,database,game,package,workflow,meta}
git clone git@github.com:gardusi-gustavo/package-yml.git ~/github/meta/package-yml
```

The full list of repositories is in
[workspace.json](https://github.com/gardusi-gustavo/contract-json/blob/main/governance/workspace.json).
Clone each one with its SSH URL; nothing else is required.

## Workflow surface

Every consumer repository carries exactly two callers:

```text
.github/workflows/event-pull-request.yml   pull_request
.github/workflows/event-tag.yml            push tags
```

Logic lives in `package-yml`, referenced at `release/v1`. No scheduled workflow is
installed in a consumer. Repository-specific behaviour lives in `scripts/` and
`infra/docker/`.

## Private repository

`gardusi-gustavo/private` is operator-only:

- accessible with the SSH key;
- no workflow, no automation, no `GITHUB_TOKEN`;
- never cloned by a bot.

## Troubleshooting

`fatal: repository not found` means the SSH key is not registered for the account
or the remote is still HTTPS. Check:

```bash
ssh -T git@github.com
git remote -v
```

A pull request created by `GITHUB_TOKEN` does not trigger the `pull_request`
workflow. That is expected: automation prepares a branch and a PR, and a human
opens or pushes it so CI runs.

A workflow edit rejected with a permissions error means the token being used is
not the operator's SSH key. Workflow files must be pushed over SSH.

## Related

- [Workflow permissions](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/workflow-permissions.md)
- [Operating model](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/operating-model.md)
