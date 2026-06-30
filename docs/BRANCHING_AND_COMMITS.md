# Branching and Commits

This is a personal GitHub learning project. Jira or other ticket IDs are not
required for branches or commits.

## Branches

Choose a branch dynamically from the task:

```text
<type>/<short-kebab-case-purpose>
```

Allowed types are `feature`, `fix`, `docs`, `chore`, `refactor`, `test`, and
`spike`. Keep the purpose short and do not use prompt numbers.

## Commits

Use Conventional Commits by default:

```text
<type>: <short description>
```

If the project owner provides a ticket ID, include it, such as:

```text
fix(ABC-123): handle empty source files
```

If no ticket ID is provided, commit normally without one. Never invent a ticket
ID.

Company repositories may require ticket IDs or a different commit format. Those
rules can apply to company work, but they do not apply to this repository.
