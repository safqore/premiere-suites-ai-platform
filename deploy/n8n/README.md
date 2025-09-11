# n8n Deployment (Render)

This directory contains infrastructure/build assets for the n8n service.

## Build Context
Set the Render service "Root Directory" to `deploy/n8n` so that this Dockerfile is used and the build context is this folder only.

## Included Workflow
Currently only `docs/workflows/premiere-suites-demo-workflow.json` is copied into the image (referenced relatively with `../../`). Update the `Dockerfile` to copy additional workflow JSON files if needed:

```
# Example to copy all workflows
# COPY ../../docs/workflows/ /app/workflows/
```

## Environment Variables (Configure in Render)
Required for auto import:
```
N8N_IMPORT_EXPORT_DIR=/app/workflows
N8N_IMPORT_WORKFLOWS=all
```
Security / basics (examples):
```
N8N_PROTOCOL=https
N8N_PORT=5678
N8N_HOST=<your-service-hostname>
WEBHOOK_URL=https://<your-service-hostname>
N8N_ENCRYPTION_KEY=<long-random-string>
```
Optional basic auth:
```
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=<password>
```

## Persistent Data
Attach a persistent disk in Render mounted at `/home/node/.n8n` to retain credentials and workflow edits.

## Future Enhancements
- Add idempotent activation/import script
- Copy multiple workflows
- Introduce a `render.yaml` infra spec
