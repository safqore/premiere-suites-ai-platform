# MANUAL DEPLOYMENT STEPS

## Deploying Web Frontend on Vercel

1. Visit: https://vercel.com/safqore-admins-projects  
2. New → Project → Connect Git repository → Select the subfolder containing the frontend code → Deploy.

## Deploying n8n Backend on Render

1. New → Web Service → Existing Image → use: `docker.n8n.io/n8nio/n8n`  
   Name: `premiere-suites-n8n-backend`  
   Tier: Free (current)  
   Click Deploy.
2. On first load: create the admin user (reuse the established password policy).
3. Enter the Community Edition activation key (unlocks selected features).
4. Import workflow: `docs/workflows/premiere-suites-demo-workflow.json`  
   Set workflow name (e.g. `premiere-suites-demo-workflow`).
5. Configure credentials (intentionally high‑level; restricted knowledge).
6. Webhook URL correction:  
   Shipped JSON often references: `http://localhost:5678/webhook/chat-interface`  
   Must change to: `https://premiere-suites-n8n-backend.onrender.com/webhook/chat-interface`  
   (Remove port 5678; enforce HTTPS.)

---

# AUTOMATED DEPLOYMENT (CURRENT STATE & GAPS)

Automation attempts exist:
- Frontend: `.github/workflows/vercel.yml`
- Backend (n8n container trigger + workflow import attempt pathing): `.github/workflows/render.yml`

Primary current limitation:
- Every container redeploy on Render (Free tier) starts “from scratch” because no persistent disk is attached (disks require a paid plan).
- n8n defaults to an internal SQLite file inside the container filesystem; this is ephemeral in stateless deploys.
- Result: Admin user, credentials, workflows, encryption key, and activation state are lost each time.

Target future state (one‑way model):
- All authoritative configuration (workflows, environment variable templates, seed logic) lives in Git locally.
- CI/CD (local → remote) performs a push-only deployment. No edits are ever made directly in the hosted environment (no two‑way sync).
- Live system state can be rebuilt deterministically from the repository plus secrets stored securely (Render / Vercel / secret manager).
