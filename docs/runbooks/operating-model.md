# Operating model

How ideas become merged code with a predictable amount of attention and money.

The machine-readable form of this runbook is
[operating.json](https://github.com/gardusi-gustavo/contract-json/blob/main/governance/operating.json).

## The loop

```text
think in chat          one conversation = one idea
      │
      ├── decision  ──→ ADR (docs/decisions/)
      ├── action    ──→ issue or comment on an existing issue
      ├── question  ──→ answer, then delete the chat
      └── reference ──→ docs or wiki
      │
      ▼
delete the chat        the issue is the durable record
      │
      ▼
distill                problem, evidence, acceptance, non-goals, rollback
      │
      ▼
generate               one small PR from a `spec:ready` issue
      │
      ▼
review                 ~12 minutes, fixed checklist, cooling-off
      │
      ▼
merge                  closes exactly one issue or thread
```

A chat is a scratchpad, not storage. If its outcome is not actionable, a decision,
or a reference, delete it without creating anything.

## Routing

| What the chat produced | Destination | Kept |
| --- | --- | --- |
| A decision worth remembering | `docs/decisions/NNNN-<slug>.md` | permanently |
| Work with a concrete outcome | GitHub issue | until merged |
| Context about open work | Comment on the existing issue or PR | until merged |
| A question | Answer in the chat, then delete | no |
| Reference material | `docs/` or the wiki | permanently |
| Four or more ideas | One project issue with a checklist | until the project closes |

## Budgets are bands

Stay between the floor and the roof. Empty is not the goal; flow is.

| Resource, per day | Floor (L) | Roof (R) | Target |
| --- | ---: | ---: | ---: |
| AI spend | $0.50 | $1.50 | $1.00 |
| Review | 60 min | 180 min | 120 min |
| Chat and thinking | 30 min | 90 min | 60 min |
| Focused work | 90 min | 270 min | 180 min |
| Merged PRs | 5 | 15 | 10 |
| New issues | 5 | 15 | 10 |

The 12-minute unit is what makes the review band and the merge band agree:
120 minutes divided by 10 PRs is 12, and 180 divided by 15 is also 12. A PR that
cannot be reviewed in about 12 minutes is too large: at most 4 files, 250 changed
lines, 5 commits.

## Queues and hysteresis

Caps use two thresholds so intake does not oscillate around a single number.

| Open issues | Behaviour |
| --- | --- |
| below 30 | new issues allowed |
| 30 to 40 | comments on existing issues only |
| above 40 | intake paused; review and merge until back under 30 |

| Ready PRs across all repositories | Behaviour |
| --- | --- |
| below 5 | generate and promote drafts |
| 5 to 15 | normal |
| above 15 | stop generating; review only |

Per repository: at most one ready PR and one draft PR. Drafts are a buffer, not
debt; a draft older than a week is a signal to close the issue.

## Readability gate

No specification, no pull request. Before generation an issue must carry:

- problem: what is wrong or missing;
- evidence: file paths, line numbers, failing checks, or data;
- acceptance: how to tell it is done;
- non-goals: what is explicitly out of scope;
- rollback: how to undo it.

The distillation is a short comment on the issue, labelled `spec:ready`. Approving
five lines takes seconds; reviewing an implementation built on an unstated goal
takes hours.

## Review protocol

Fixed order, time-boxed, no exceptions:

1. Correctness: does the diff do what the spec says?
2. Evidence: is every claim backed by a path or a test?
3. Scope: only the files the issue names?
4. Tests: does CI cover the change, and did it run?
5. Rollback: is the undo path real?

Additional rules:

- never merge in the session that generated or reviewed the PR; wait at least 4 hours;
- one PR closes one issue or one thread;
- a PR larger than 4 files or 250 lines goes back for splitting.

## Seasons

| Season | Focus | Review | Chat | Merged PRs | AI spend |
| --- | ---: | ---: | ---: | ---: | ---: |
| build | 180 min | 120 min | 60 min | 10 | $1.00 |
| maintain | 75 min | 45 min | 30 min | 3 | $0.40 |

Switch seasons explicitly. A maintain week is not a failure; an unstated build
season is.

## Rituals

| Cadence | Ritual | Output |
| --- | --- | --- |
| daily | review the ready queue, merge within the band | 5 to 15 merges |
| weekly | triage comments, close stale issues, update the band check | queue between 30 and 40 |
| monthly | restore drill and token rotation | fresh device proven to rebuild in 30 minutes |

## Anti-patterns

- Keeping a chat as a todo list instead of creating an issue or deleting it.
- Creating an issue only to avoid deleting a chat.
- Merging in the same session as generation.
- Growing a PR to finish an issue faster.
- Treating an empty queue as success; an empty queue means underuse.
- Adding a second tracker; comments on issues are part of the same tracker.

## Related

- [Local workspace](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/local-workspace.md)
- [Portable setup](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/portable-setup.md)
- [Chat to issue](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/prompts/chat-to-issue.md)
- [Operating budgets](https://github.com/gardusi-gustavo/contract-json/blob/main/governance/operating.json)
