FROM python:3.12-slim-bookworm
COPY --from=eclipse-temurin:21-jdk /opt/java/openjdk /opt/java/openjdk
COPY --from=ghcr.io/astral-sh/uv:0.10.10 /uv /usr/local/bin/uv
ENV JAVA_HOME=/opt/java/openjdk PATH="/opt/java/openjdk/bin:/app/.venv/bin:${PATH}" PYTHONDONTWRITEBYTECODE=1 SOURCECHECK_DATA=/data SOURCECHECK_TOOLS=/data/tools SOURCECHECK_MODELS=/data/models
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY sourcecheck ./sourcecheck
COPY bridge ./bridge
COPY configs ./configs
COPY fixtures ./fixtures
RUN uv sync --frozen --no-dev --no-editable
EXPOSE 8770
ENTRYPOINT ["/app/.venv/bin/python", "-m", "sourcecheck"]
CMD ["serve", "--host", "0.0.0.0", "--port", "8770"]
