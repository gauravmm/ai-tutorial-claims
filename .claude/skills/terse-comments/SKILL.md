---
name: terse-comments
description: Write or tighten a comment or docstring in this repo - state the decision, then only what the code cannot say. Use when writing a new comment or docstring, when asked to make one shorter or less wordy, or when one argues its case instead of stating it. Applies on top of ste-writing, which governs sentence form.
---

# terse-comments

Expect to cut a third to a half of what you first write. That ratio is a smell, not a target: a comment already made of nothing but distinct facts is finished, and cutting to hit a number takes one of them.

## First: is it agent-facing?

A docstring on a function registered as an agent tool is the model's spec, and so is any string that reaches a prompt. Apply sentence form only. Never delete anything there for being redundant: a tool docstring that restates an argument is doing its job, and the enumerated options, examples and limits are the behavior. If shortening would drop one, leave the sentence long.

Everything below this section is for text a human reads. When you cannot tell which you are looking at, treat it as agent-facing.

## Docstrings

**Paragraph 1 is the contract.** What it returns or does, in one sentence where you can. Then any behavior that looks like a bug and is not, stated flatly as intended.

**Paragraph 2 is what the code cannot say.** External API quirks, why an obvious alternative was rejected, a consequence with no local symptom.

There is no third paragraph. Suspect the break, not the content: a third paragraph usually holds a real fact that belongs at the end of the second, so merge it rather than dropping it.

## Comments

A comment has no contract paragraph, because it cannot restate a signature. Lead with the decision it explains, then the reason that decision is not obvious. One paragraph, unless two decisions share the site.

The code sits directly below, so "inferable" bites harder than in a docstring. A comment that narrates the next line goes, and so does one whose consequence the reader meets two lines later anyway.

## Cut

- **The justification chain.** "This is intended behavior" beats the scenario that proves it, and an abstract failure rarely needs its worked example.
- **The closing flourish.** A last sentence that re-frames or summarizes what you just said.
- **The contrast clause.** "...the way it could in the workspace", "...rather than the shape that would repeat instead". The claim already stands without it.
- **The pointer that then restates.** "Same reasoning as above", followed by the reasoning. Pick one.
- **Vendor mechanism trivia.** Name the constraint you hit, not the feature matrix you learned it from.
- **Orientation.** Where a thing lives, which module it borrows transport from, what another file argues. All discoverable.
- **Advice, down to its imperative.** "Reaching a second bot means replacing that global with a registry keyed by target" -> "A second bot needs a registry keyed by target".

## Keep

- External behavior you would have to test to learn: "Vikunja rejects a label filter given a title rather than an id".
- Why the obvious call was not used, and the failure it would have caused.
- A consequence invisible from the code in front of you: "a silently failed advance would re-raise the job forever".
- The security reason for a boundary. "The inbox must not write the instructions that govern it" survives every cut.
- Exact contract terms: half-open window notation, ordering, units, what is paired with what.
- **A repeated idiom, verbatim at every site.** "Never fatal: a checkpoint that cannot be written must not cost Gaurav his turn" reads as duplication and is not. The repetition is what makes the pattern legible, so never dedupe one to a pointer.

## Two places say the same thing

Keep the one at the higher altitude and cut the other. A fact about the whole module belongs in the module docstring, and a per-function pass that trims it there loses it for good, because the function that also stated it will be trimmed by the same rule on its own turn.

Check before cutting either copy. This is the one failure in this skill that destroys information rather than merely bruising it.

## Notes

Shorter beats grammatically ideal. Passive voice is fine when it costs fewer words.

Verify before you compress. Shortening a claim re-asserts it, and the pass that produced this skill carried forward a docstring saying labels were re-checked in a function that never looks at them.
