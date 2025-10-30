FROM python:3.11-slim

# Create app directory and copy repository

WORKDIR /app
# Copy whole repo into image (build context should be repository root)
COPY .. /app

# Upgrade pip and install build tools
RUN python -m pip install --upgrade pip setuptools wheel

# Ensure the mcp requirements file path exists and install dependencies
RUN pip install -r /app/mcp/requirements.txt

# Install the parent package (pvw-cli) in editable mode so the server
# can import the library from the repo copy inside the image.
RUN pip install -e /app

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# By default run the MCP server. The server communicates over stdio, so
# containers should be started with stdin attached (docker run -i).
ENTRYPOINT ["python", "mcp/server.py"]
