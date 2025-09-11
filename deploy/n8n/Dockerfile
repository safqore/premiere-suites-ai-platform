FROM n8nio/n8n:latest

# Build context is deploy/n8n, so reach back to repo root with ../.. as needed.
# Copy only the demo workflow for now. You can switch to copying the entire workflows dir later.
COPY ../../docs/workflows/premiere-suites-demo-workflow.json /app/workflows/premiere-suites-demo-workflow.json

# Environment-based import handled by Render service env vars:
#   N8N_IMPORT_EXPORT_DIR=/app/workflows
#   N8N_IMPORT_WORKFLOWS=all
