# AGENTS.md

## Purpose
`cubrid-cookbook` collects runnable, production-style examples for the CUBRID ecosystem.

## Read First
- `README.md`
- `PRD.md`
- `CONTRIBUTING.md`
- `docs/agent-playbook.md`

## Working Rules
- Treat examples as user-facing reference implementations, not throwaway demos.
- Keep language parity and naming conventions consistent where equivalent examples exist.
- If an example's setup or dependencies change, update the surrounding docs in the same change.
- Avoid adding hidden prerequisites that are not documented.

## Validation
- `make up`
- Run the smallest relevant example for the language you changed.
- `make down`

## Project Context — Performance Loop System

> This repo provides the **reproducible demo** for the ecosystem.
> Board: [CUBRID Ecosystem Roadmap](https://github.com/orgs/cubrid-labs/projects/2)

### Role

cubrid-cookbook must enable `docker compose up && make demo` for anyone to experience the ecosystem.
All examples must produce predictable, verifiable output.

### Related Issues

| Issue | Phase | Priority |
|-------|-------|----------|
| #7 Standardize expected outputs and one-command demo | R5 | Must-Have |
| #5 Verify Rust examples after crates.io publish | R4 | Nice-to-Have |
