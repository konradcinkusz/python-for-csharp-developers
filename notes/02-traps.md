# 02 — Traps for people arriving from C#

The catalogue of habits that compile in the reader's head and fail in
Python. Each entry is phrased in the reader's own voice, names what Python
does instead, and names the chapter that **elicits** it — a trap is put to
the reader before it is named, and a box that says "wrong" without the
reader having walked into it teaches nothing.

Appendix B is written from this file. **An entry there must name a chapter
that elicits it, and an entry here whose owner is not yet written is a
promise that chapter has to keep.** When a chapter is written, mark its
entries delivered with the section that carries them; when a chapter's
brief changes, re-derive the owner from `tools/chapters.json` rather than
from this file.

Numbered so a chapter can cite an entry. The numbering is by owning chapter
and never reused; a retired entry keeps its number and says why. An owner
reading `Ch. N §N.M, delivered` names the section that elicits the trap in
the written chapter; an owner reading a bare `Ch. N` is still a promise.

## Part I — Runtime and toolchain

| # | The habit, in the reader's voice | What Python does | Owner |
|---|---|---|---|
| 1 | Threads are useless in Python, so I will not bother with them | The GIL serialises *bytecode*; a thread blocked on I/O holds no lock. Threads are the right tool for I/O-bound work and the wrong one for CPU-bound work, and E1 measures both | Ch. 1 |
| 2 | 3.14 is free-threaded now, so the GIL is gone | The free-threaded build is a separate binary, `python3.14t`, opt-in; the default build still has the lock | Ch. 1 |
| 3 | Python has no compile step, so there is nothing like IL | Source is compiled to bytecode and cached in `__pycache__`; `python -m dis` shows it. There is no JIT you can count on by default | Ch. 1 |
| 4 | `if __name__ == "__main__"` is boilerplate | It is the difference between a module that runs when imported and one that runs when executed — the reason a listing can be both importable and runnable | Ch. 1 |
| 5 | `pip install` puts the package on the machine, like a global tool | An environment is a directory; a global install is the one thing every later chapter's listings cannot survive | Ch. 2 |
| 6 | I activate the environment and then run things | `uv run` resolves the environment per invocation; activation is the habit that ships the wrong interpreter to CI | Ch. 2 |
| 7 | `requirements.txt` is the lockfile | It is a wish list with ranges; `uv.lock` is the lockfile, it is committed, and `uv sync --locked` refuses to drift from it | Ch. 2 |
| 8 | A type hint is a type | It is a claim the runtime never checks; `str` can be `None` at run time and nothing says so. A checker is a second compiler you have to invite | Ch. 3 §3.1, delivered |
| 9 | `List[int]`, `Optional[str]`, `Dict[str, Any]` | 2019 spellings; `list[int]`, `str | None` and `dict[str, Any]` on the pinned interpreter, and PEP 695 for generics | Ch. 3 §3.2, delivered |
| 10 | `@dataclass` validates its fields, like a record with a constructor | It generates `__init__`, `__eq__` and `__repr__` and checks nothing; validation at a boundary is pydantic's job | Ch. 3 §3.3, delivered |
| 11 | `def f(items=[])` — an optional list parameter | The default is evaluated once, at definition, and shared by every call. `None` and construct inside | Ch. 3 §3.5, delivered |
| 12 | `Any` is like `dynamic`, a thing I can contain | `Any` propagates: one `Any` in a chain turns everything downstream into `Any`, and the checker reports nothing | Ch. 3 §3.5, delivered |

## Part II — The language, mapped

| # | The habit, in the reader's voice | What Python does | Owner |
|---|---|---|---|
| 13 | Override `__eq__` and I have value equality, like overriding `Equals` | Defining `__eq__` sets `__hash__` to `None`: the object is now unhashable and cannot be a `dict` key or `set` member. The headline trap of Chapter 4 | Ch. 4 |
| 14 | `is` is reference equality, so `x is 5` is fine for small ints | It happens to be true for small integers because CPython caches them, and false one magnitude up. `is` is for `None` and sentinels; `==` for values | Ch. 4 |
| 15 | `[[]] * n` gives me `n` lists | It gives one list `n` times; `[[] for _ in range(n)]` gives `n` | Ch. 4 |
| 16 | A class attribute is a static field | It is shared by every instance *and* readable through them, so a mutable class attribute mutated through `self` is mutated for everyone | Ch. 4 |
| 17 | `__str__` is `ToString()` | `__repr__` is what the debugger, the REPL and a list of the objects show; `__str__` is what `print` shows, and falls back to `__repr__` | Ch. 4 |
| 18 | `0.1 + 0.2 == 0.3` is a Python bug | It is IEEE 754 in both languages; the difference is that Python prints the shortest round-tripping repr, so the mismatch is visible. `math.isclose`, or `Decimal` for money | Ch. 4 |
| 19 | `/` on two integers is integer division, as in C# | `/` is true division; `//` floors, and floors towards negative infinity, which `-7 // 2 == -4` demonstrates | Ch. 4 |
| 20 | A decorator is an attribute — metadata a framework reads | A decorator is a function that runs at definition time and can replace what it decorates. It is middleware, not metadata, and Chapter 5's headline | Ch. 5 |
| 21 | A comprehension is LINQ | A list comprehension is eager where `IEnumerable` is deferred; a generator expression is deferred. Materialise once, on purpose | Ch. 5 |
| 22 | A closure in a loop captures the loop variable's value | It captures the variable, late-bound; every closure sees the last value. Bind with a default argument or `functools.partial` | Ch. 5 |
| 23 | `s += piece` in a loop is fine, strings are strings | Quadratic; `"".join(pieces)` is linear | Ch. 5 |
| 24 | A generator is `yield return` | It is, and it also has `send()`, `close()` and a `return` value carried in `StopIteration` — a coroutine before `async` existed | Ch. 5 |
| 25 | `except:` catches everything, like `catch {}` | It catches `KeyboardInterrupt` and `SystemExit` too, which is why the process cannot be stopped. `except Exception:` at most, and log the traceback. ruff reports it as E722 | Ch. 6 §6.4, delivered |
| 26 | Catch `Exception`, log it, continue — defensive | It converts a crash into a silent wrong answer; EAFP means catching the exception you expect, not every one. **The one trap in this chapter that nothing in the book's toolchain reports**, which is why it is the one that reaches production | Ch. 6 §6.4, delivered |
| 27 | `raise e` inside `except` re-throws, like `throw ex;` | **This entry was wrong, and the chapter that owns it measured the correction.** Python keeps the traceback on the exception OBJECT, so `raise e` truncates nothing: every frame under it survives and the re-raise line is *added*, so the re-raising frame appears twice. Bare `raise` is still the better habit — the duplicate frame is noise — but the C# rule does not transfer and neither does the anxiety. What a re-raise can lose is the *link*: `raise New(...)` without `from` sets `__context__` rather than `__cause__` | Ch. 6 §6.4, delivered |
| 28 | `return` in `finally` is harmless | It swallows any in-flight exception and returns as if nothing happened. Not silently on the pinned interpreter: PEP 765 has the compiler emit `SyntaxWarning: 'return' in a 'finally' block`, and ruff reports B012 and SIM107 — and it still swallows, because a warning is not an error | Ch. 6 §6.4, delivered |
| 29 | A method's hint tells me what it raises | Nothing in the type system carries exceptions; a docstring does, nothing verifies it, and Python has no checked exceptions — nor does C#, so what transfers badly is the tooling around them rather than the language | Ch. 6 §6.3, delivered |
| 30 | `KeyError` means something went wrong | `KeyError`, `StopIteration` and `AttributeError` are protocol: a `dict` lookup, an iterator's end and `getattr` all speak through them | Ch. 6 §6.2, delivered |
| 31 | Truthiness is `bool`, like C# | Empty containers, zero, `None` and empty strings are false; `if items:` is idiomatic and `if items is not None:` is a different question | Ch. 6 §6.2, delivered |
| 31a | An exception class is a `FooException` | Python's suffix is `Error`, and ruff's N818 reports a class without it. `JobUnavailable` fails the lint until it is `JobUnavailableError` | Ch. 6 §6.3, delivered |
| 32 | A module is a namespace; importing it is free and pure | A module is an object that runs once, top to bottom; a side effect at import runs for every importer, and a circular import is two modules half-run | Ch. 7 §7.1, delivered |
| 33 | `from x import *` is `using x;` | It copies every public name into the importing module and hides where anything came from; `import x` and `from x import name` | Ch. 7 §7.2, delivered |
| 34 | I can name a variable `list`, `id` or `type` | It shadows the builtin for the rest of the scope, and the failure arrives three functions later | Ch. 7 §7.2, delivered, at module level as well as at name level |
| 35 | I need a DI container | A composition root is a function; `functools.partial` and a `Protocol` do what the container did, and FastAPI's `Depends` is the one container most readers will meet | Ch. 7 §7.5, delivered |

## Part III — Concurrency

| # | The habit, in the reader's voice | What Python does | Owner |
|---|---|---|---|
| 36 | A coroutine is a `Task`: calling it starts it | A coroutine is cold; calling it builds an object that does nothing until awaited or scheduled. Forgetting the `await` is a warning, not an error | Ch. 8 §8.2, delivered |
| 37 | `create_task` starts the task immediately | It schedules; the body does not run until the caller yields. Measured in the LangChain book's Chapter 3 | Ch. 8 §8.2, delivered |
| 38 | `.Result` on a task deadlocks, so I use `ConfigureAwait(false)` | There is no `SynchronizationContext` and no `ConfigureAwait`; there is one loop, and one blocking call inside it freezes every other coroutine, with no error and no log line | Ch. 8 §8.3, delivered |
| 39 | `gather` is `WhenAll` | `gather` orphans its siblings when one fails; `TaskGroup` cancels them. The two are identical on speed, so the choice is only ever about failure semantics | Ch. 8 §8.4, delivered |
| 40 | Cancellation is a token I poll, so catching `Exception` is how I lose it | Backwards in both halves. It is `CancelledError`, delivered at an `await` -- and it inherits from `BaseException`, so `except Exception` is the clause that lets it THROUGH. What swallows it is a bare `except:`, `except BaseException:`, or an `except asyncio.CancelledError` block with no `raise` under it | Ch. 8 §8.5, delivered |
| 41 | `HttpClient` is a singleton, so `httpx.AsyncClient` is too | The lifetime advice carries -- construct it once, share it, close it -- and the defaults do not: a default `AsyncClient` already has a five-second deadline, applied separately to connect, read, write and pool rather than to the request as a whole | Ch. 8 §8.6, delivered |
| 60 | A `Task` can be awaited twice, so a coroutine can | A `Task` is a handle on work already running and hands out its result as often as you ask; a coroutine IS the work, and awaiting it a second time raises `RuntimeError: cannot reuse already awaited coroutine`. Out of block because numbers are never reused | Ch. 8 §8.2, delivered |

## Part IV — Shipping

| # | The habit, in the reader's voice | What Python does | Owner |
|---|---|---|---|
| 42 | `Depends` is the DI container, so a dependency is a singleton | Per-request by default; a `yield` dependency is a disposable scope; application-lifetime state goes in the lifespan | Ch. 9 |
| 43 | A validation failure is a 400 with `ProblemDetails` | It is a 422 with pydantic's error list, and the shape is pydantic's, not the framework's | Ch. 9 |
| 44 | Settings come from `IOptions<T>` and `appsettings.json` | `pydantic-settings` reads the environment, a `.env` file and secrets directories into a validated model; there is no JSON provider chain | Ch. 9 |
| 45 | More uvicorn workers is more throughput | Workers are processes; each has its own loop, its own pool and its own memory. E5 measures the curve | Ch. 9 |
| 46 | A `Session` is a `DbContext`, so I `commit()` and the objects stay usable | `expire_on_commit=True` by default: every attribute is reloaded on next access, which is a query inside a loop you did not write | Ch. 10 |
| 47 | Relationships are loaded when I read them, as in EF | Lazy by default in both; the N+1 is identical, and `selectinload` is `Include`. E6 counts it | Ch. 10 |
| 48 | Alembic autogenerate is the migration | It is a diff of the models against the database, and it misses renames, type changes and constraints; read every generated migration | Ch. 10 |
| 49 | I need a repository over the ORM | The `Session` is the unit of work and the repository pattern doubles it; Chapter 10 says why that pattern is usually a mistake here | Ch. 10 |
| 50 | A test class per fixture, like `IClassFixture` | pytest fixtures are functions with a scope; the class is optional and usually absent | Ch. 11 |
| 51 | Mock where the thing is defined | Patch where the name is *looked up* — the importing module — or the patch does nothing and the test passes for the wrong reason | Ch. 11 |
| 52 | `assert` is for debug builds | pytest rewrites `assert` to explain itself; it is the assertion library | Ch. 11 |
| 53 | `logging.basicConfig` and I am done | The standard module's configuration is global, import-order-sensitive and the reason structlog exists | Ch. 12 |
| 54 | Correlation id in a static field, like `AsyncLocal` | `contextvars` is `AsyncLocal`; a module-level variable is shared by every request on the loop | Ch. 12 |
| 55 | `FROM python:3.14` and `pip install` in the Dockerfile | Multi-stage with `uv sync --frozen --no-dev`, a non-root user, and the two environment variables. E7 measures the three shapes | Ch. 12 |

## Part V — Python for AI work

| # | The habit, in the reader's voice | What Python does | Owner |
|---|---|---|---|
| 56 | The SDK is magic | Every AI SDK is a pydantic model, an httpx client and a streaming iterator; read the installed, pinned package | Ch. 13, **delivered** §13.1 and §13.5 |
| 57 | `model_validate_json` is `JsonSerializer.Deserialize` | Lax mode coerces where `System.Text.Json` refuses; strict mode is what a C# engineer expects, and E8 prices both | Ch. 13, **delivered** §13.3, priced §13.4 |
| 58 | A notebook is where Python happens | A notebook is a REPL with a memory of every cell you ran in any order; nothing in this book is one, and Chapter 13 says when one is right | Ch. 13, **delivered** §13.7 |
| 60 | The SDK uses the `httpx` I pinned | Both SDKs depend on the `httpx2` distribution, not `httpx`: `isinstance(c._client, httpx.Client)` is False, and of the two SDKs one refuses a mismatched client and the other accepts it | Ch. 13, **delivered** §13.5 |
| 59 | A trace assertion needs a model to evaluate | The first layer of agent-eval-bench is deterministic; it runs with no model, which is why it can run in CI | Ch. 14 |

## Retired

None yet. An entry retires when its chapter is written and finds it false;
it keeps its number and gains the reason.

**Corrected rather than retired, September 2026, writing Chapter 8.** Two
entries had the habit right and the correction wrong, which is a different
thing from being false, so both keep their number and their row:

- **40** said catching `Exception` swallows a cancellation. It does not:
  `asyncio.CancelledError.__mro__` is `(CancelledError, BaseException,
  object)` on the pinned interpreter, so `except Exception` never sees one.
  The entry had the clause that is SAFE in Python named as the dangerous
  one, which is the worst possible advice to give a reader arriving from
  C#. Verified by running it, not by reading the source; `code/ch08/
  cancelled.py` is the demonstration and prints the inheritance chain.
- **41** said `HttpClient` has no default timeout. That half was never
  checked and this repository has no .NET to check it against, so it is
  gone rather than corrected: the row now states only the httpx side, which
  `code/ch08/deadline.py` reads off the installed package.
