# Identity and naming

One job, one name. The suffix is the unit of meaning: it appears in the bot, its
token, its secret, its workflow file, its label, and its branch prefix.

## Convention

| Layer | Pattern | intake | generator | reviewer |
| --- | --- | --- | --- | --- |
| Control repository | `workflow-agent` | — | — | — |
| Bot | `agent-<job>` | `agent-intake` | `agent-generator` | `agent-reviewer` |
| Token | same as bot | `agent-intake` | `agent-generator` | `agent-reviewer` |
| Secret | `AGENT_<JOB>_TOKEN` | `AGENT_INTAKE_TOKEN` | `AGENT_GENERATOR_TOKEN` | `AGENT_REVIEWER_TOKEN` |
| Workflow file | `<job>.yml` | `intake.yml` | `generator.yml` | `reviewer.yml` |
| Label | `agent:<job>` | `agent:intake` | `agent:generator` | `agent:reviewer` |
| Branch | `agent/<job>/<issue>-<slug>` | | | |

The repository is the umbrella. A bot is not a repository: three bot repositories
would duplicate secrets, permissions, and CI for no benefit.

## Repository axes

The `workflow-*` repositories are named by **trigger**, the agents by **job**.
Keep those axes separate:

| Repository | Axis | Holds |
| --- | --- | --- |
| `workflow-agent` | control plane | `intake.yml`, `generator.yml`, `reviewer.yml` |
| `workflow-event` | event trigger | data ingestion |
| `workflow-scheduled` | time trigger | cron jobs |

Recommended adjustment: rename `workflow-manual` to `workflow-agent`. It already
holds the agent control plane, and GitHub redirects the old name, so existing
links keep working. Renaming is a UI action; the references update (governance
manifests, profile README, repository files) is a small pull request.

Do not rename all three repositories to job names. That maps one bot to one
repository and turns a single control plane into three.

The old `/agent` ChatOps dispatcher is retired. "Manual" is a trigger, not a job.
If an interactive bot returns later, name it `agent-manual` and keep it separate.

## Descriptions

Use these for the token description, the repository description, and later the
GitHub App manifest:

| Name | Description |
| --- | --- |
| `agent-intake` | Turns chat summaries into parent issues and fans out one child issue per repository and outcome. Issues only. |
| `agent-generator` | Picks the top queued issue for the focus repository and opens a small pull request. Contents and pull requests only. |
| `agent-reviewer` | Reads pull requests, checks CI, and posts advisory review comments and labels. Read-only code access. |
| `workflow-agent` | Control plane for the intake, generator, and reviewer agents. No application code. |

## Prefilled where GitHub allows it

| Target | Prefill |
| --- | --- |
| New repository | `https://github.com/new?name=workflow-agent&description=Control+plane+for+the+intake,+generator,+and+reviewer+agents.&visibility=public` |
| Repository rename | UI only: Settings, Rename |
| Fine-grained PAT | no prefill URL; copy the permission table |
| GitHub App | manifest flow with prefilled name, description, permissions, events |
| Actions secret | UI only |

## Bot identity

Fine-grained PATs act as the account owner, so bot-authored pull requests show
`gardusi-gustavo`. Distinct authorship requires GitHub Apps, which appear as
`agent-generator[bot]` and can be filtered with `author:agent-generator[bot]`.
Keep the names identical so the PAT-to-App migration changes only the
credential.

## Related

- [Token matrix](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/token-matrix.md)
- [Auth policy](https://github.com/gardusi-gustavo/contract-json/blob/main/governance/auth.json)
