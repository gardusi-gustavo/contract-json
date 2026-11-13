# Identity and naming

One event, one name. The event suffix appears in the template, the consumer file,
the workflow, and the label.

## Convention

| Layer | Pattern | pull request | tag |
| --- | --- | --- | --- |
| Template | `templates/event/<event>.yml` | `templates/event/pull-request.yml` | `templates/event/tag.yml` |
| Consumer file | `.github/workflows/event-<event>.yml` | `event-pull-request.yml` | `event-tag.yml` |
| Workflow name | `event-<event>` | `event-pull-request` | `event-tag` |
| Job id | `ci` / `release` | `ci` | `release` |
| Label | `source:<class>` | `source:pr` | `source:release` |
| Branch | `workflow/<change>` | `workflow/callers` | `workflow/callers` |

The caller job stays `ci` for pull requests so the required check context remains
`ci / ci`.

## Why flat files

GitHub does not traverse subdirectories under `.github/workflows`, and `uses:`
only accepts `.github/workflows/<file>.yml`. The folder structure lives in
`package-yml/templates/event/`; consumers receive flat `event-*.yml` files.

## Repository axes

| Repository | Axis | Holds |
| --- | --- | --- |
| `package-yml` | templates and reusable logic | `event-*`, `experimental-*` |

`workflow-event`, `workflow-manual`, and `workflow-scheduled` are retired. Their
active content moved to `package-yml`, the database repositories, or the
governance records.

Job names live in workflows and labels, not in credentials. There are no bot
accounts and no bot tokens.

## Who runs what

- Workflows run as `github-actions[bot]`, scoped to the repository.
- The operator pushes and merges over SSH and the UI.
- Automation prepares a branch and a pull request; a human opens or merges it so
  `pull_request` CI runs.

## Related

- [Workflow permissions](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/workflow-permissions.md)
- [Auth policy](https://github.com/gardusi-gustavo/contract-json/blob/main/governance/auth.json)
