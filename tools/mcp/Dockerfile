FROM python:3.11-slim

WORKDIR /app

# Copy the repository into the image (build context should be the repo root).
COPY . /app

# Upgrade pip and install build tools
RUN python -m pip install --upgrade pip setuptools wheel

# Install the CLI and the MCP server as separate local packages.
RUN pip install -e /app
RUN pip install -e /app/tools/mcp

ENV PYTHONUNBUFFERED=1

# Run the MCP server over stdio.
ENTRYPOINT ["pvw-mcp"]
