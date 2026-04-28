# System Logics: Work Scenarios

Use this guide when you need to know which memory files to read and update for different types of work.

## Scenario Matrix

| Area | What to Check First | Key Memory Files to Update |
| --- | --- | --- |
| Backend/API | `ARCHITECTURE.md`, `project_state.md` | `task_log.md`, `daily_summary.md`, `artifacts/` for API design |
| Frontend/UI | `DESIGN.md`, `ARCHITECTURE.md` | `task_log.md`, `message_pairs.md`, `artifacts/` for component specs |
| Database/Schema | `ARCHITECTURE.md`, `code_logics.md` | `task_log.md`, `project_state.md`, `artifacts/` for migrations |
| DevOps/CI/CD | `ARCHITECTURE.md`, repo root configs | `task_log.md`, `daily_summary.md`, `artifacts/` for deployment notes |
| Testing | `tests/`, build config | `task_log.md`, `artifacts/` for test strategy docs |
| Bug Fix | `daily_summary.md`, yesterday's `task_log.md` | `task_log.md`, `message_pairs.md`, `artifacts/` for root-cause analysis |
| Refactor | `code_logics.md`, `ARCHITECTURE.md` | `task_log.md`, `project_state.md`, `artifacts/` for migration plans |

## Area-Specific Workflows

### Backend / API Development
1. Read `ARCHITECTURE.md` to understand the stack and module boundaries.
2. Check `project_state.md` for active backend threads or API versioning notes.
3. Before coding, write an artifact in `artifacts/` describing the endpoint contract (URL, method, request/response shape).
4. After implementing, update `code_logics.md` if module interactions changed.
5. Log in `task_log.md` with files touched and any blockers.

### Frontend / UI Development
1. Read `DESIGN.md` for colors, typography, layout rules, and component hierarchy.
2. Check `project_state.md` for active UI threads or design system updates.
3. Before coding, write an artifact describing the component structure, state flow, and any new design tokens.
4. After implementing, update `code_logics.md` if component interactions or state management changed.
5. Log in `task_log.md` with files touched and visual verification notes.

### Database / Schema Changes
1. Read `ARCHITECTURE.md` for the database technology and existing schema overview.
2. Check `project_state.md` for schema version or migration history.
3. Before changing schema, write an artifact in `artifacts/` with:
   - Current schema snapshot
   - Proposed changes with rationale
   - Migration script (if applicable)
   - Rollback plan
4. After applying, update `project_state.md` with new stable facts about the schema.
5. Log in `task_log.md` with migration status and any data integrity checks.

### DevOps / CI/CD / Infrastructure
1. Read `ARCHITECTURE.md` for deployment target and infrastructure overview.
2. Check `project_state.md` for environment configs and secrets management approach.
3. Before changing pipelines, write an artifact in `artifacts/` with:
   - Current pipeline diagram or step list
   - Proposed change and risk assessment
   - Verification steps
4. After applying, update `project_state.md` with new environment facts.
5. Log in `task_log.md` with pipeline run results and any incidents.

### Testing / QA
1. Read `code_logics.md` to understand the testing framework and conventions.
2. Check `daily_summary.md` for recently completed features that need test coverage.
3. Before writing tests, write an artifact in `artifacts/` with:
   - Test plan (unit, integration, e2e)
   - Edge cases and mock strategy
4. After running tests, update `task_log.md` with pass/fail status and flaky test notes.
5. If coverage gaps are found, add to `daily_summary.md` under "Active Tasks".

### Bug Fixes
1. Read `daily_summary.md` for active blockers and recent completions.
2. Read yesterday's `task_log.md` and `end_of_day_summary.md` for context.
3. Write an artifact in `artifacts/` with:
   - Bug reproduction steps
   - Root-cause hypothesis
   - Fix strategy and verification steps
4. After fixing, update `task_log.md` with root cause and resolution.
5. If the bug reveals a systemic issue, update `code_logics.md` or `project_state.md`.

### Refactoring
1. Read `code_logics.md` and `ARCHITECTURE.md` to understand current structure.
2. Check `project_state.md` for any threads that might conflict with refactoring.
3. Write an artifact in `artifacts/` with:
   - Scope of refactor (what changes, what stays)
   - Risk areas and rollback plan
   - Step-by-step execution order
4. After each step, update `task_log.md`.
5. After completion, update `code_logics.md` to reflect the new structure.

## Cross-Cutting Rules

- **Never skip the read chain.** Even if you are "just fixing a typo," read `_agent_rules.md`, `project_state.md`, `system_prompt.md`, `code_logics.md`, `system_logics.md`, and `daily_summary.md` first.
- **Always write an artifact before complex work.** If the task spans more than 2 files or involves design decisions, create an artifact.
- **Update `project_state.md` only for durable facts.** Temporary blockers belong in `daily_summary.md`.
- **Keep `daily_summary.md` short.** Archive or remove items older than a few days.
- **Split early.** If any file exceeds ~50 lines, consider splitting into an artifact or a new root file.
