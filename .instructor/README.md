# Instructor kit

This folder is for people who maintain the task. It is not for attendees.

A GitHub Codespace runs `.devcontainer/strip-instructor.sh` on create and deletes this folder. Work on the task on a laptop. To keep the folder in a Codespace, set `KEEP_INSTRUCTOR=1` before create.

## Contents

| Path | What |
| --- | --- |
| `CLAUDE.md` | Layout and workshop rules for agents that edit this repo |
| `PROPOSAL.md` | Locked design |
| `generate/` | Receipt model, formatters, `build.py` |
| `eval/` | Student-like prompts and `run.sh` |
| `test_claims.py` | Regenerate-and-diff self-check |
| `easter-egg/` | Goose art handoff |

`check.py` still reads `dataset/.generate/checksums.csv` and `ground_truth.csv`. Those stay in the student tree, hidden, so Run and Debug works after this folder is gone.

## Commands

```text
python3 .instructor/generate/build.py
python3 .instructor/test_claims.py
./.instructor/eval/run.sh
```
