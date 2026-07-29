FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim@sha256:531f855bda2c73cd6ef67d56b733b357cea384185b3022bd09f05e002cd144ca AS base

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

FROM base AS quality

RUN apt-get update \
    && apt-get install --no-install-recommends --yes libatomic1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-install-project

COPY alembic.ini ./
COPY migrations ./migrations
COPY src ./src
COPY tests ./tests
RUN uv sync --locked --no-editable

CMD ["uv", "run", "--no-sync", "pytest"]

FROM base AS runtime

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project

COPY alembic.ini ./
COPY migrations ./migrations
COPY src ./src
RUN uv sync --locked --no-dev --no-editable

RUN useradd --create-home --uid 10001 alliancesim

USER alliancesim

CMD ["alliancesim-api"]
