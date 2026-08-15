# Eval prompts

Instructor-only. These stand in for a student pasting into Copilot. The agent in this repo must not read `README.md`, so each prompt carries the output contract.

Run with `opencode run`, not `opencode -p`. In this install, `-p` on `run` is a password flag. `opencode run` is the headless equivalent of `claude -p`.

```text
./.instructor/eval/run.sh
```

## Model

Workshop target is GitHub Copilot **Raptor mini** (a GPT-5-mini fine-tune, unlimited on Copilot Free).

This machine has no Raptor mini. We use the paid OpenCode Go endpoint.

| Id | Why |
| --- | --- |
| `opencode-go/hy3` | What we run. Paid Hunyuan 3. Fast enough, not as strong as v4 Pro. |
| `opencode-go/deepseek-v4-flash` | Smaller/faster paid stand-in if hy3 is slow or too loose. |
| `opencode-go/deepseek-v4-pro` | Too strong. A pass here does not mean a Free-tier student will pass. |
| `opencode/hy3-free` | Free queue. Avoid unless Go is down. |

Override: `EVAL_MODEL=opencode-go/deepseek-v4-flash ./.instructor/eval/run.sh`

## Prompts

1. `01-starter.txt` - the shipped wrong prompt. Must go red. GST-both-ways, noise, tip.
2. `02-careful.txt` - a student who read the traps but did not write formulas. The interesting case.
3. `03-precise.txt` - names every trap and the rule. Should be green if the model can follow instructions.
