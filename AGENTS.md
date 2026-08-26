# Agent Instructions

Agents working in this task directory must follow these rules:

- Never read [README.md](./README.md) or [dataset/README.md](./dataset/README.md). The student tells you the task.
- Never read, list, search, or summarize any files or subdirectories inside [dataset/.generate](./dataset/.generate).
- Never read, list, search, or summarize [.instructor](./.instructor).
- Ignore [dataset/display](./dataset/display/) entirely: never read, list, search, or summarize any file or subdirectory inside it. For a displayed `source_XX` receipt, use the corresponding `dataset/source_XX.txt` source text instead.
- Never read check.py.
- Never run check.py. Ask the user to run **Check Extracted Data** from the Run and Debug menu (`Ctrl+Shift+D`).
- Never write a script that parses the sources. Read the files and extract as the user asked. This is for teaching.
- Do not copy [dataset/claim.reference.csv](./dataset/claim.reference.csv) into `claim.csv`. Copy it only if the user says they finished stage 1, or they skip to stage 2.

If you need source data, work only from the source files directly in `dataset/`.
