# AI-Assisted Development Workflow

This repository uses AI as an implementation assistant, not as the owner of the
system.

## AI responsibilities

- Implement clearly scoped tasks and acceptance criteria.
- Inspect existing context before changing files.
- Keep changes small, focused, reversible, and easy to review.
- Use only synthetic data and stop if data sensitivity is unclear.
- Run relevant validation and report what ran or was skipped.
- Update docs when behavior, architecture, setup, commands, or scope changes.
- Clearly distinguish current behavior from plans.

AI agents must not invent production usage, scale, compliance, security,
reliability, performance, or business-impact claims. They must not expand a task
into adjacent features without explicit approval.

## Human responsibilities

Humans own:

- Architecture and scope decisions
- Data provenance, privacy, and safety
- Production-readiness and compliance judgments
- Review of code, SQL, models, tests, and generated data
- Merge approval and final acceptance

## Recommended task cycle

1. Start with a focused brief using
   [`TASK_BRIEF_TEMPLATE.md`](TASK_BRIEF_TEMPLATE.md).
2. Inspect the current branch, working tree, relevant docs, and implementation.
3. Implement only the requested slice.
4. Validate behavior and review the diff for safety and scope.
5. Update documentation and the decision log when needed.
6. Request human review before merge.
