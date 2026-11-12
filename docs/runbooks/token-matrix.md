# Token matrix

One operator credential, three bot credentials, and no token with platform
administration.

The live state (which token is registered, expiry, probe result) stays in
`~/.config/gh/registry.json`. Token values never appear in this repository.

## Principles

- **SSH is the operator.** Clone, push, tags, and workflow-file edits happen over
  an account SSH key. Workflow files need no `workflow` scope when pushed over
  SSH.
- **PATs are for bots, remote only.** A bot token lives in Actions secrets,
  never in a shell profile, a remote URL, or a Docker image.
- **The UI handles platform operations.** Cancel or rerun a run, disable a
  workflow, change settings, create or delete repositories.
- **No bot holds Administration, Workflows, Actions, Secrets, or Packages.**

## Credentials

| Identity | Method | Permissions | Used for |
| --- | --- | --- | --- |
| operator | SSH ed25519 | git read/write, including `.github/workflows` | local opencode, git |
| `agent-intake` | fine-grained PAT | issues: write, contents: read, metadata: read | parent to child issues, comments |
| `agent-generator` | fine-grained PAT | contents: write, pull requests: write, issues: read, metadata: read | branch, commits, pull request |
| `agent-reviewer` | fine-grained PAT | pull requests: write, contents: read, checks: read, metadata: read | review comments, labels |
| PR CI, release, Pages | `GITHUB_TOKEN` | declared per workflow | per repository |

No token is shared between two bots.

## Why these three

| Workflow | Needs | Token |
| --- | --- | --- |
| PR CI | contents: read | `GITHUB_TOKEN` |
| Release and publish | contents: write, packages: write, id-token | `GITHUB_TOKEN` |
| Intake, cross-repository | issues: write on many repositories | `agent-intake` |
| Generator | contents and pull requests, and must trigger CI | `agent-generator` |
| Reviewer | pull requests and read, distinct identity | `agent-reviewer` |
| Backup | contents: read on many repositories | operator over SSH |
| Workflow sync | git write | operator over SSH |

`agent-generator` exists for one reason beyond permissions: pull requests opened
with `GITHUB_TOKEN` do not trigger other workflows, so their CI never runs. A
PAT-authored pull request does.

## Repository selection

- All 43 public repositories, `private` excluded.
- Fine-grained tokens allow 50 repositories; the largest domain has 20, so
  per-domain tokens remain possible if isolation is ever needed.
- Per-bot is preferred over per-domain because permissions differ by job, while
  a domain is a routing label, not a security boundary.

## Storage and rotation

- Secrets: `AGENT_INTAKE_TOKEN`, `AGENT_GENERATOR_TOKEN`, `AGENT_REVIEWER_TOKEN`
  in the control repository.
- Rotation: 90 days, or immediately when a device or token is suspected lost.
- The operator key is per device and revoked per device.
- The private repository is operator-only: no bot token, no automated clone.

## Identity caveat

A fine-grained PAT acts as the account owner. Pull requests and commits created
with it show `gardusi-gustavo`, not `agent-generator`. Distinct bot authorship
requires GitHub Apps, whose installation tokens appear as
`agent-generator[bot]`. The permission sets above are already App-shaped, so the
migration is a credential swap, not a redesign.

## UI checklist

1. Register the SSH key under Settings, SSH and GPG keys.
2. Create `agent-intake`, `agent-generator`, `agent-reviewer` with the
   permissions above and all 43 public repositories selected.
3. Add the three secrets to the control repository's Actions settings.
4. Re-run the queued CI runs from the Actions tab.
5. Retire the seven domain tokens after the bots work, or reduce them to
   contents: read, issues: write, pull requests: write.
6. Remove `Actions` and `Workflows` from any token: SSH and the UI cover both.

## Related

- [Identity and naming](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/identity-naming.md)
- [Operating model](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/operating-model.md)
- [Auth policy](https://github.com/gardusi-gustavo/contract-json/blob/main/governance/auth.json)
