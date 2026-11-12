# Chat to issue

End a thinking session by asking the assistant for a JSON block. Turn the block
into a parent issue in the profile repository, then fan out into one child issue
per repository and outcome. Delete the chat.

## Stage 1: capture the chat as a parent issue

```text
Summarise this conversation as one JSON object and nothing else.

{
  "title": "short imperative title",
  "summary": "what we discussed, in two or three sentences",
  "kind": "idea | decision | bug | question | process",
  "priority": "P0 | P1 | P2 | P3",
  "repos": ["package-go", "contract-sql", "unknown"],
  "decisions": ["what was decided, if anything"],
  "open_questions": ["what is still unresolved"],
  "actions": ["what should happen next"]
}

Rules:
- one chat produces exactly one object;
- "repos" may be empty or "unknown" at this stage; do not force a decision;
- if the conversation produced no action and no decision, return
  {"kind": "question", "actions": []}.
```

## Stage 2: fan out into child issues

After the parent exists, ask for the children:

```text
Expand each action into child issues.

{
  "parent": 42,
  "children": [
    {
      "title": "short imperative title",
      "repo": "package-go",
      "kind": "feature | bug | chore",
      "priority": "P0 | P1 | P2 | P3",
      "size": "S | M | L",
      "outcome": "what changes",
      "rationale": "why it matters",
      "evidence": ["path/to/file:line"],
      "acceptance": ["observable check"],
      "non_goals": ["out of scope"],
      "rollback": "how to undo",
      "group": "optional shared slug",
      "depends_on": [123]
    }
  ]
}

Rules:
- one child = one repository and one outcome;
- two outcomes in the same repository are two children;
- work spanning repositories shares a "group" and orders
  contract -> package -> workflow/database -> dashboard/game;
- at most 8 children; more means the chat was a project.
```

## Commands

```bash
# create the parent issue in the profile repository
python3 scripts/inbox.py --input parent.json

# create child issues and link them to the parent
python3 scripts/inbox.py --input children.json --parent 42

# preview without writing anything
python3 scripts/inbox.py --input parent.json --dry-run

# discard a chat that produced no action
python3 scripts/inbox.py --input parent.json --discard
```

## Stages

| Stage | Meaning |
| --- | --- |
| `stage:captured` | parent exists, not triaged |
| `stage:triaged` | priority set, target repositories listed |
| `stage:fanned-out` | children exist |
| `stage:specced` | child has the five spec sections |
| `stage:queued` | child is eligible for the scheduler |
| `stage:generating` | a PR is being produced |
| `stage:review` | a PR is open |
| `stage:done` | merged |
| `stage:failed` | needs a human decision |

## Queue policy

`inbox.py` reads `governance/operating.json` and applies per-repository limits:

| Target | Resume | Pause |
| --- | ---: | ---: |
| Profile inbox | 80 | 100 |
| Work repository | 15 | 20 |

When a work repository is at its cap, fan-out is deferred: the parent stays
`stage:triaged` with a comment `deferred: repo at cap`. Nothing is lost and no
global cap is involved.

## Labels

`source:chat`, `kind:<kind>`, `size:<S|M|L>`, `domain:<prefix>`,
`priority:<P0-P3>`, and later `spec:ready`.

Labels are applied only when they already exist in the target repository;
`inbox.py` skips the rest rather than failing.

## Related

- [Operating model](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/operating-model.md)
- [Operating budgets](https://github.com/gardusi-gustavo/contract-json/blob/main/governance/operating.json)
