# The C# side

Appendix D solves twenty interview problems in both languages, and this is
where its C# half lives and is compiled. The decision to compile it at all
is recorded in `CLAUDE.md` under *Resolved questions*; the short version is
that this book's promise is that every listing runs in CI, and an appendix
whose C# half nobody compiled would break that promise in the one place the
book carries the most code.

## Why it already exists, before Appendix D

Because the book already makes C# claims, and they are the class of claim a
reader is most likely to know better than the author. Two had already been
found wrong by hand, and the first run of this project found a third:
Chapter 4 said C# formats a `double` to fifteen significant digits and hides
the representation error. That was true of .NET Framework and of .NET Core
before 3.0. On .NET 10 `(0.1 + 0.2).ToString()` is `0.30000000000000004` —
the same string Python prints. The chapter and `notes/02-traps.md` entry 18
are corrected, and the claim is now asserted here instead of remembered.

`Solutions/Claims/` holds the C# a chapter compares itself against, and
`Solutions.Tests/` asserts each claim against the section it backs. A claim
that stops being true fails a build rather than sitting on a page.

## Running it

    cd code/csharp && dotnet test

or `make csharp` from the repository root, which is what CI runs.

## Conventions

- **Warnings are errors**, because a claim that compiles with a warning is a
  claim half made. `CS0659` is the one deliberate exception, suppressed in
  `Solutions/Solutions.csproj`: `Ch04.cs` has to override `Equals` without
  `GetHashCode` to demonstrate what C# does when you do, which is the whole
  point of Chapter 4's comparison.
- **An XML comment may not contain two consecutive hyphens.** It is the same
  shape as the typewriter-font ligature trap Chapter 2 records, and it cost
  a build here too.
- The SDK is pinned in `global.json` and in the workflow, and
  `tools/check_structure.py --pins` compares both against `\dotnetver` in
  `preamble.tex`, the same way uv's pin is compared.
