# Fix Task Contract

You are a one-shot fixer agent. A previous task failed. Fix the issue and verify.

## Task
- ID: {{task_id}}
- Description: Fix issue from {{original_task_id}}

## Failed Task Context
- Original task: {{original_task_id}} -- {{original_task_description}}
- Error: {{original_error}}
- Files involved: {{original_files}}

## Project Context
- Workspace: {{workspace}}
- Stack: {{stack_name}}

## Stack Profile
{{stack_profile}}

## Coding Rules
{{coding_rules}}

## Instructions

1. Read the relevant source files to understand the failure
2. Fix the root cause (not just the symptom)
3. Run verification (lint, test, build) using the project's own commands
4. If tests fail after your fix, iterate until they pass

## Sandbox Constraints

- **NO network access.** Do NOT install packages.
- All dependencies are pre-installed.

## Output Requirements (Hardcoded — No Deviations)

The LAST thing in your response MUST be EXACTLY one of these signal blocks. No text after `---END-SIGNAL---`.

**FIXED** (fixed field REQUIRED):
```
---SIGNAL---
status: DONE
task: {{task_id}}
worker: {{worker_name}}
fixed: {{original_task_id}}
---END-SIGNAL---
```

**CANNOT FIX** (error field REQUIRED, max 200 chars):
```
---SIGNAL---
status: FAIL
task: {{task_id}}
worker: {{worker_name}}
error: <what failed, max 200 chars>
---END-SIGNAL---
```
