# Prompt: caption the goose easter egg

Copy everything below the line into another agent. The images live in this folder (`easter-egg/`). The folder is gitignored.

---

You are finishing an easter-egg still for a workshop task (expense-claim extraction). The workshop ships an intentionally wrong review skill that rejects every receipt for lacking a goose. This image is the punchline.

## The chosen still

Use `easter-egg/peace-was-never-an-option.jpg` as the only source image. It is a copy of `easter-egg/frame-05-peak.jpg`: a white cel-shaded goose on a flat teal field, shaking a thermal receipt to shreds, paper scraps in the air. Do not regenerate the goose. Do not switch to the other concept stills.

## What to make

1. A captioned poster, saved as `easter-egg/peace-was-never-an-option-captioned.png` (and a `.jpg` if you also want a smaller copy).
2. The caption text, exactly, in this casing:

   **peace was never an option**

   All lowercase. No period. No quotes around it. No extra words.

3. Put the caption on with code (PIL, or HTML/CSS then a screenshot). Do not ask an image model to draw the letters. Image models garble this line.

4. Type treatment:
   - Heavy condensed grotesque or a stencil/military sans, white or near-white, with a thin dark outline or a solid teal bar behind the words so it reads on the scraps.
   - Centered under the goose, or a bottom banner that does not cover the bird or the flying paper.
   - No other text. No watermark. No "Untitled Goose Game" lettering.

5. Keep the flat teal background. Do not add a desk, a logo, or a scene.

## Also, if you have time

Assemble an 8-frame sprite sheet from, in this order:

- `frame-01-hold.jpg`
- `frame-02-anticipation.jpg`
- `frame-03-shake.jpg`
- `frame-04-tear.jpg`
- `frame-05-peak.jpg`
- `frame-06-followthrough.jpg`
- `frame-07-honk.jpg`
- `frame-08-settle.jpg`

Uniform cells, no divider lines, subject roughly centered in each cell. Save as `easter-egg/goose-destroy-sheet.png`. One row of eight, or two rows of four. Add the same caption once under the sheet, again with code, not the image model.

The frames were edited one at a time from `01-sprite-base.jpg`, so the goose drifts a little. Crop/pad so each cell is the same size. Do not redraw the frames unless a cell is unusable.

## Do not

- Do not commit this folder. It is gitignored on purpose.
- Do not drop the image into `README.md` or spoil the goose skill.
- Do not "fix" `.github/skills/review-claim/SKILL.md`.
- Do not use `02-pixel-sprite.jpg`, `03-pos-massacre.jpg`, or `04-office-desk.jpg` unless I ask. Those were rejected concepts.

## When you are done

Show me the captioned still first. Then the sheet if you made one. Tell me the exact pixel size of each file.
