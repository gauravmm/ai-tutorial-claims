# CLAUDE.md

## Docs and comments

- Keep documents as short as possible.
- Docs and comments carry only information that is not obvious, not innately discoverable from the code/repo, and not redundant with either.
- No historical information (what changed, what it used to be, why something was rejected) in docs or comments unless specifically allowed. Git history keeps it discoverable.
- Do not line-wrap markdown. Write one line per paragraph or bullet.
- ASCII only in Python files, README.md and CLAUDE.md (pre-commit enforces this): no en/em dashes, curly quotes, or other Unicode gremlins. `.github/skills/` is exempt because the goose joke skill needs emoji. `.instructor/PROPOSAL.md` is exempt because it is implementer notes.

## Layout

- No `src/` and no importable package. Do not invent `ai_tutorial_claims/`. This is a workshop task, not a library.
- `check.py` stays at the repo root and is stdlib-only so a bare Codespace can Run and Debug with no uv or pip.
- `.instructor/` is the instructor kit. A Codespace deletes it on create (`.devcontainer/strip-instructor.sh`). `dataset/.generate/` keeps only `checksums.csv` and `ground_truth.csv` so the student checker still runs.
- Hide `dataset/.generate/` and `.instructor/` with `files.exclude` and `search.exclude`. Never put answers in student-facing files.
- `claim.csv` is student output and is gitignored. `dataset/claim.reference.csv` is committed.
- The office-desk goose still is `.devcontainer/office-desk.jpg`. The student README hides it in a `details` block under stretch goals. Explorer hides the file.

## Workflow

- `python3 .instructor/test_claims.py` is the self-check. It regenerates via `.instructor/generate/build.py` and diffs against the committed artifacts. Students never run this.
- `uvx ruff@0.16.3 check .`, `uvx ruff@0.16.3 format .`, `uvx pyright@1.1.411` and `npx markdownlint-cli2@0.23.2 --fix "**/*.md"` are what pre-commit and CI run. Pyright runs in strict mode.
- A bare code fence fails MD040. Tag every fence, and use `text` for output, paths and pseudo-code.
- Make intermediate commits freely when you work autonomously. When you code interactively with the user, do not commit until the user asks. Expect tweak-review cycles and flatten them into one commit.

## The task

- Ground truth is in git so a Codespace can check. `AGENTS.md` forbids the agent from reading `dataset/.generate` or `check.py`, and from running `check.py`. Students use the "Check Extracted Data" launch config.
- The review skill at `.github/skills/review-claim/` is intentionally wrong (geese). Do not fix it. Do not spoil it in `README.md`.
- Stage 2 has no checker. Do not add `review.csv` or `check_review.py`.
- Categories are assigned by source, never inferred.
- Money is SGD only. GST is 9%. No FX.
- Do not write a student-facing parse script. The exercise is prompting.
- `claim.csv` is student output. `dataset/claim.reference.csv` is the known-good stage-1 file.
