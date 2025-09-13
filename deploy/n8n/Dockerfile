# Base official n8n image (pick a fixed version for reproducibility)
FROM n8nio/n8n:latest
# Switch to root to create directories, then revert (official image runs as node)
USER root
RUN mkdir -p /app/workflows
COPY docs/workflows/premiere-suites-demo-workflow.json /app/workflows/premiere-suites-demo-workflow.json
# (No import yet; that will come in Step 3)

# Back to the non-root user used by the base image
USER node

# Use the base image's default entrypoint/cmd for now