# Operating model

How ideas become merged code with a predictable amount of attention and money.

The machine-readable form of this runbook is
[operating.json](https://github.com/gardusi-gustavo/contract-json/blob/main/governance/operating.json).

## The loop

```text
think in chat                    one conversation = one parent issue
      │
      ▼
parent issue (profile)           summary, decisions, priority
      │
      ▼
fan-out                          one child per repository and outcome
      │
      ▼
spec                             problem, evidence, acceptance, non-goals, rollback
      │
      ▼
focus repo                       one repository at a time, highest priority first
      │
      ▼
1 ready + 2 draft PRs            clear that repository's queue
      │
      ▼
review and merge                 ~12 minutes per PR
```

A chat is a scratchpad, not storage. Once its summary exists as a parent issue, the
chat is deleted. The issue is the durable record.

## Backlog depth versus work in progress

Two different limits, deliberately:

- **Depth** is how much may wait. The inbox holds up to 100 issues; each work
  repository holds up to 20. A low-value repository may wait indefinitely.
- **WIP** is how much may move. Each repository has at most one ready PR and two
  draft PRs, regardless of how large its backlog is.

There are no global caps. Priority and the focus rule decide what runs, not a
global number.

## Caps

| Scope | Limit |
| --- | ---: |
| Inbox open issues | 80 resume, 100 pause |
| Work repository open issues | 15 resume, 20 pause |
| Ready PRs per repository | 1 |
| Draft PRs per repository | 2 |
| Children per parent | 8 |
| Draft age | 7 days |
| `someday` age before close | 90 days |

## Focus scheduling

```text
candidates = repositories with issues labelled stage:queued
rank(repo) = (min priority, oldest queued issue, name)
focus      = first candidate that still has a free slot

fill focus: one ready PR for the top issue
            two draft PRs for the next two issues
stop.       no other repository is touched in this run
```

- One repository per generator run prevents a runaway across 43 repositories
  without a global cap.
- Focus persists until that repository has no queued issue above P3.
- Drafts are the repository's depth-first queue: when the ready PR merges, promote
  the oldest draft and open a new one.
- A P0 in another repository may preempt only through the human `focus:repo`
  label. There are no silent context switches.

## Review order

Ready PRs are reviewed in repository-priority order, not arrival order. Drafts do
not enter the review queue until promoted.

A repository that never rises above P3 is never generated, and that is intended.
Starvation is allowed but visible: the weekly ritual reports the oldest queued
issue per repository and how long each repository has waited.

## Day shape

Hardest first. The inbox is the pleasant task, so it goes last.

| Order | Block | Time | Mode |
| --- | --- | ---: | --- |
| 1 | Status sweep: CI, open PRs, pick the target | 5 min | review |
| 2 | Deep review and merge | 60 to 180 min | review |
| 3 | Queue check: promote drafts, requeue failures | 5 to 10 min | ops |
| 4 | Chat, thinking, capture | 30 to 90 min | ideation |
| 5 | Inbox wrap-up | 15 to 45 min | triage |

Rules:

- no inbox triage before the review block; capture is allowed any time and takes
  under two minutes, triage does not;
- focus lock: finish a PR before opening another;
- merge before generate: a repository with a ready PR gets no new work;
- triage stops after a batch of 10 issues.

## Modes

| Mode | May do | May not do |
| --- | --- | --- |
| review | read diffs, run checks, merge | create issues, triage |
| ops | promote drafts, retry, requeue | review code |
| ideation | chat, capture summaries | triage, write code |
| triage | label, fan-out, prioritize, close | write code, review |

## Fan-out

- The unit of work is `(repository, outcome)`, not the chat. Two outcomes in one
  repository become two children.
- One child produces one PR; a child never spans repositories.
- Work that spans repositories becomes a group: shared label `group:<slug>`,
  `depends-on` links, and order `contract → package → workflow or database →
  dashboard or game`.
- If the target repository is at its issue cap, the parent stays `stage:triaged`
  with a comment `deferred: repo at cap`. Nothing is lost.
- More than eight children means the chat was a project; split the parent.

## Readability gate

No specification, no pull request. An issue must carry:

- problem: what is wrong or missing;
- evidence: paths, line numbers, failing checks, or data;
- acceptance: how to tell it is done;
- non-goals: what is out of scope;
- rollback: how to undo it.

The distillation is a short comment labelled `spec:ready`. Approving five lines
takes seconds; reviewing an implementation built on an unstated goal takes hours.

## Review protocol

Fixed order, time-boxed:

1. correctness: does the diff do what the spec says?
2. evidence: is every claim backed by a path or a test?
3. scope: only the files the issue names?
4. tests: does CI cover the change, and did it run?
5. rollback: is the undo path real?

Additional rules:

- never merge in the session that generated or reviewed the PR; wait at least four
  hours;
- one PR closes one issue or one thread;
- more than four files or 250 changed lines goes back for splitting;
- UI work is accepted by screenshot plus a human `verdict:like` or
  `verdict:dislike`; unit tests cover logic, not taste.

## Append-only

- new information is a new comment, never a rewritten body;
- new work is a new commit on the same branch, up to five, never an amend, rebase,
  or force-push;
- scope grew: close the PR and split the issue;
- failed: comment with logs and label `stage:failed`, do not patch by hand;
- a human pushing to a bot branch marks it `manual:touched`; the bot stops managing
  it.

## Failure loop

Every failure becomes an artifact:

1. the bot comments with the tail of the log and labels `stage:failed`;
2. two attempts per issue and three revisions per PR, then a human decides;
3. the human appends context or `/retry`; the issue stays, the branch is discarded;
4. recurring failures get `process:lesson`;
5. the weekly ritual turns lessons into rules, through a pull request to this
   runbook or to `operating.json`.

## Seasons

| Season | Focus | Review | Chat | Inbox | Merged PRs | AI spend |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| build | 210 min | 120 min | 45 min | 30 min | 10 | $1.00 |
| maintain | 120 min | 60 min | 30 min | 15 min | 3 | $0.40 |

Switch seasons explicitly. A maintain week is not a failure; an unstated build
season is.

## Anti-patterns

- keeping a chat as a todo list instead of creating a parent issue or deleting it;
- creating an issue only to avoid deleting a chat;
- triaging before reviewing;
- merging in the same session as generation;
- growing a PR to finish an issue faster;
- adding global caps where priority and focus already decide;
- treating an empty queue as success.

## Related

- [Local workspace](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/local-workspace.md)
- [Portable setup](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/portable-setup.md)
- [Chat to issue](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/prompts/chat-to-issue.md)
- [Operating budgets](https://github.com/gardusi-gustavo/contract-json/blob/main/governance/operating.json)
