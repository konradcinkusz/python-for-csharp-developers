# notes/

Planning documents for *Python for .NET Engineers*. They are the reasoning
behind the manifest, not a second copy of it: the chapter sequence, the briefs
and the dependency graph live in `tools/chapters.json`, and anything here that
restates them is the next thing to go stale.

| File | What it is |
|---|---|
| `01-curriculum.md` | Why these fourteen chapters in this order, the release plan, the experiments and their Status column, the guiding project's specification, and the overlap rules against the two companion books |
| `02-traps.md` | The catalogue of C# habits that fail in Python, each with the chapter that owns it. Appendix B is written from this file and every entry there must name a chapter that elicits it |

The rules the companion books earned apply here from the first line: a count
of occurrences is never stated where a list will do; a claim about another
chapter is checked by opening that chapter; a number on the page is computed
by `code/measure/` and reaches the page as `\val{}`, never typed.
