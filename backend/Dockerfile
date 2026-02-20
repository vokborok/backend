FROM python:3.13

ENV PYTHONUNBUFFERED=1

ARG USER_ID
ARG GROUP_ID

RUN groups &&\
    groupadd -g 2500 dev &&\
    useradd -l -u 2500 -g dev dev &&\
    install -d -m 0755 -o dev -g dev /home/dev

WORKDIR /backend/
RUN chown dev:dev /backend

COPY --chown=dev:dev ./pyproject.toml ./alembic.ini /backend/

USER dev

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.4.15 /uv /bin/uv

# Place executables in the environment at the front of the path
ENV PATH="/backend/.venv/bin:$PATH"

# Compile bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
ENV UV_LINK_MODE=copy

ENV PYTHONPATH=/backend

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

COPY --chown=dev:dev app /backend/app
COPY --chown=dev:dev db_migrations /backend/db_migrations

CMD ["fastapi", "run", "--reload", "--workers", "4", "app/main.py"]
