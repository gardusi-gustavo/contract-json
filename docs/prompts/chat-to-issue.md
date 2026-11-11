# Chat to issue

End every thinking session by asking the assistant for one JSON block, then turn
it into a durable record and delete the chat.

## Prompt

```text
Summarise this conversation as one JSON object and nothing else.

{
  "title": "short imperative title",
  "repo": "package-go | contract-json | dashboard-news | ... | workflow-manual",
  "kind": "feature | bug | decision | chore | question | reference",
  "priority": 1,
  "size": "S",
  "outcome": "what changes for the user or the system",
  "rationale": "why this matters, in two or three sentences",
  "evidence": ["path/to/file:line", "failing check or observed behaviour"],
  "acceptance": ["observable check that proves it is done"],
  "non_goals": ["what is explicitly out of scope"],
  "rollback": "how to undo it",
  "target": "new | <issue-number>"
}

Rules:
- one idea per object; if there are several, return an array;
- use "target": "new" only when this is new work;
- use an issue number when this is context for existing work;
- if the conversation produced only a question, return
  {"kind": "question", "target": "discard"}.
```

If the queue is full, the assistant still returns an object; `inbox.py` decides
whether it becomes an issue or a comment.

## Command

```bash
# create, or comment according to the queue policy
python3 scripts/inbox.py --input idea.json

# preview without writing anything
python3 scripts/inbox.py --input idea.json --dry-run

# force a comment on an existing issue
python3 scripts/inbox.py --input idea.json --issue 42

# discard a chat that produced no action
python3 scripts/inbox.py --input idea.json --discard
```

## Routing

| `kind` | Destination |
| --- | --- |
| `feature`, `bug`, `chore` | issue or comment |
| `decision` | ADR under `docs/decisions/`, linked from the issue |
| `question` | discard |
| `reference` | `docs/` or the wiki |

## Queue policy

`inbox.py` reads `governance/operating.json` and applies the hysteresis:

| Open issues | Result |
| --- | --- |
| below 30 | new issue |
| 30 to 40 | comment on `target`, or on the closest match |
| above 40 | comment only; intake paused |

Once the issue exists, delete the chat. The issue body must stand alone: the
rationale is the part that disappears with the chat.

## Labels

`source:chat`, `kind:<kind>`, `size:<S|M|L>`, `domain:<prefix>`, and later
`spec:ready` when the five spec sections are present. Labels are applied only
when they already exist in the repository; `inbox.py` skips the rest rather than
failing.

## Related

- [Operating model](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/operating-model.md)
- [Operating budgets](https://github.com/gardusi-gustavo/contract-json/blob/main/governance/operating.json)
