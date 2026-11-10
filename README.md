# contract-json

Pure JSON Schema contracts and account-level structured governance manifests.

## Layout

| `schemas/domain/` | data/document contracts |
| `schemas/api/` | API envelopes |
| `schemas/events/` | event payloads |
| `schemas/infra/` | repo and workflow contracts |
| `governance/` | inventory, policy, bundle order, rulesets, and archive history |

## Validation

```bash
bash infra/scripts/ci.sh
```

## Rules

- Public contract/asset package only.
- No application data, secrets, or personal data.
- Versioned by tag.
