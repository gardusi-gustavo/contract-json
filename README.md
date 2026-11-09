# package-json

Pure JSON Schema contract registry.

## Layout

| `schemas/domain/` | data/document contracts |
| `schemas/api/` | API envelopes |
| `schemas/events/` | event payloads |
| `schemas/infra/` | repo and workflow contracts |

## Validation

```bash
bash infra/scripts/ci.sh
```

## Rules

- Public contract/asset package only.
- No application data, secrets, or personal data.
- Versioned by tag.
