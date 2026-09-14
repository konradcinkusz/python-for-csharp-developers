# Shape three: two stages, and the one to copy.
#
# The builder has uv and the lockfile; the runtime has neither. What
# crosses between them is the virtual environment and nothing else, so
# the shipped image contains no package manager, no lockfile and no
# build cache -- which is a smaller attack surface as much as it is a
# smaller image.
#
# The two PYTHON* variables are the ones every Python image sets, and
# they point in opposite directions on purpose: compile the bytecode
# once, at build time, where it goes into an immutable layer
# (UV_COMPILE_BYTECODE=1), and never write any at run time, where it
# would dirty the container's writable layer
# (PYTHONDONTWRITEBYTECODE=1). PYTHONUNBUFFERED=1 is the one people
# discover last: stdout is block-buffered when it is a pipe, and in a
# container it is always a pipe, so without this the logs arrive in
# chunks or, if the process is killed, not at all.

FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.13 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app
# The lockfile before the source, so a source edit does not re-resolve
# and re-download every dependency.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src src
RUN uv sync --frozen --no-dev


FROM python:3.14-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# A number, not a name: the orchestrator's security policy asks whether
# the user is root, and it can only answer that from the numeric id.
RUN useradd --uid 10001 --create-home --shell /usr/sbin/nologin app
USER 10001

WORKDIR /app
COPY --from=builder --chown=10001:10001 /app/.venv /app/.venv
COPY --chown=10001:10001 src src

CMD ["python", "-m", "ops"]
