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
