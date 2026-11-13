# Workflow permissions

Every workflow runs with the built-in `GITHUB_TOKEN`, scoped to the repository
that executes it. No personal access tokens, no GitHub Apps, no cross-repository
credentials.

## Declared permissions

| Workflow | Trigger | `permissions:` |
| --- | --- | --- |
| `event-pull-request` | `pull_request` | `contents: read` |
| `event-tag` | `push: tags` | `contents: write` |
| `experimental-update` | `workflow_call` | `contents: write`, `pull-requests: write` |
| `reusable-backup` | `workflow_call` | `contents: read`, `actions: read` |
| `reusable-ingest` | `workflow_call` | `contents: write`, `pull-requests: write`, `issues: write` |
| `reusable-pages` | `workflow_call` | `contents: read`, `pages: write`, `id-token: write` |
| `reusable-agent` | `workflow_call` | `contents: write`, `issues: write`, `pull-requests: write` |

Nothing requests `administration`, `workflows`, `actions: write`, `secrets`, or
`packages` unless the job genuinely needs it.

## Consequences

- A pull request created with `GITHUB_TOKEN` does not trigger `pull_request`
  workflows. Automation prepares a branch and a PR; a human opens or pushes it so
  CI runs.
- A workflow cannot touch another repository. Cross-repository work is a human
  action, coordinated by an issue.
- Each repository owns its two callers; `package-yml` stores the templates and
  reusable logic.

## Forbidden

| Permission | Reason |
| --- | --- |
| `administration` | repository creation, deletion, settings |
| `workflows` | workflow files are pushed by the operator over SSH |
| `actions: write` | run management is a UI action |
| `secrets` | no secret is managed by a workflow |
| `packages` | release publishing uses the repository token only when needed |

## Related

- [Auth policy](https://github.com/gardusi-gustavo/contract-json/blob/main/governance/auth.json)
- [Identity and naming](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/identity-naming.md)
