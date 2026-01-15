# Entropic CRMArena Green Agent
# A2A-compliant Green Agent for CRM agent evaluation

FROM python:3.12-slim-bookworm

# Install curl for healthcheck and uv
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    pip install uv

# Create non-root user for security
RUN useradd -m agent
USER agent
WORKDIR /home/agent

# Copy dependency files first (for caching)
COPY --chown=agent:agent pyproject.toml README.md ./
COPY --chown=agent:agent uv.lock ./

# Copy source code
COPY --chown=agent:agent src src
COPY --chown=agent:agent crm crm

# Install dependencies
RUN uv sync --locked

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose A2A port
EXPOSE 9009

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s \
    CMD curl -f http://localhost:9009/.well-known/agent.json || exit 1

# A2A-compliant entrypoint
# AgentBeats passes: --host, --port, --card-url
ENTRYPOINT ["uv", "run", "src/server.py"]
CMD ["--host", "0.0.0.0", "--port", "9009"]