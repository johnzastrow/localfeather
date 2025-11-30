# Agent Guide: ActaLog

This guide makes it easy for AI agents and humans to collaborate on this codebase. It explains how to run, test, and safely change things with minimal context switching.

## Quickstart



## Project Map


## Conventions for Agents

- Keep public behavior stable; add tests when changing handler/service logic.
- Prefer small scoped PRs; update docs if behavior or endpoints change.
- Follow Clean Architecture boundaries:
- Log and validate inputs; avoid panics; return typed errors from services.

## Common Tasks

1) Run full checks (lint + test)


2) Update DB schema
- Create migration via make migrate-create name=your_change
- Implement up/down SQL under internal/repository/migrations/ or top-level migrations/ (follow existing pattern)
- Update repositories + tests

## Prompts That Work Well



## Security and Safety

- Validate all inputs at handlers; sanitize IDs and strings.
- Never log secrets or tokens.
- Use context timeouts for DB calls in services/repos.
- JWT secrets must come from config; keep defaults safe.

## Versioning

The application version is defined in TBD and surfaced at /version and logs. Increment on behavior changes.

## CI/CD

Lightweight CI can run: 

## Troubleshooting

- Build cache is local to project (.cache); clear if weird errors occur.
