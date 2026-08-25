# Reflection — Mid-Course Project

## AI tools used and how

I used Claude (claude-sonnet) throughout this project as a coding assistant. My workflow was prompt → inspect output → run tests → accept, edit, or reject before moving on. I never pasted AI output directly into the codebase without reading it first.

For the backend work I used targeted prompts: one per layer (model, storage, route, tests). For the frontend I wrote one prompt per component (filter bar, tag chips, modal field). For documentation I wrote the content myself based on actual decisions made during implementation, using AI only to help structure the markdown.

## One moment AI genuinely helped

The most useful AI contribution was the complete, correct implementation of the `validate_tags` field validator for both `TaskCreate` and `TaskUpdate` in a single pass. Writing Pydantic validators correctly — especially handling the `Optional[list[str]]` case in `TaskUpdate` where `None` means "no change" versus `[]` meaning "clear all tags" — involves a subtle distinction that is easy to get wrong. The AI got this right on the first attempt, which saved significant debugging time. I verified it by running `test_patch_task_tags_can_be_cleared` and `test_patch_unrelated_update_preserves_tags` back-to-back to confirm both cases worked.

## One moment AI slowed me down

When I asked for the search implementation, the AI returned a version using Python's `re` module for pattern matching. It imported `re` and used `re.search(re.escape(q), text, re.IGNORECASE)`. This was technically correct but introduced unnecessary complexity — a simple `q_lower in title.lower()` string check is more readable, has no import, and cannot throw a `re.error` if a user types a character like `(` or `*` as their search term. I had to read the implementation carefully to catch this, reject it, and rewrite the filter logic with the simpler string approach. Without the inspection step, a subtle regex-related bug could have surfaced only when a user typed punctuation in the search box.

## One place where my review changed the result

The AI's first proposal for tags in `TaskUpdate` made `tags` a required field — not optional. This meant any PATCH request that did not include `tags` would either fail validation or silently clear all the task's tags. I caught this by reading the model definition and comparing it to how `title`, `description`, and `assignee` are handled — all are `Optional` so they can be omitted from a PATCH without side effects. I corrected `tags` to `Optional[list[str]] = None` and added the test `test_patch_unrelated_update_preserves_tags` specifically to lock in this behavior. That test would have failed on the AI's original model, which is exactly the kind of regression the test suite is designed to catch.
