# Import FAQ to Qdrant Workflow to n8n

This guide explains how to import the FAQ to Qdrant workflow into the n8n web UI.

## Method 1: Import via n8n Web UI (Recommended)

### Step 1: Open n8n

1. Start n8n: `n8n start` or access your n8n instance
2. Open your browser and go to `http://localhost:5678`
3. Log in to n8n

### Step 2: Import the Workflow

1. Click on **"Workflows"** in the left sidebar
2. Click the **"Import from file"** button (or use the import icon)
3. Select the file: `docs/workflows/faq_to_qdrant_workflow_simple.json`
4. Click **"Import"**

### Step 3: Configure Environment Variables

1. In the imported workflow, you'll need to set up environment variables
2. Go to **Settings** → **Environment Variables**
3. Add the following variables:
   ```
   QDRANT_URL=https://your-cluster.qdrant.io
   QDRANT_API_KEY=your-qdrant-api-key
   OPENAI_API_KEY=your-openai-api-key
   ```

### Step 4: Configure Node Credentials

1. Click on each HTTP Request node that needs authentication
2. Configure the authentication settings:
   - **Qdrant nodes**: Use "Header Auth" with `api-key` as name and `{{ $env.QDRANT_API_KEY }}` as value
   - **OpenAI node**: Use "Header Auth" with `Authorization` as name and `Bearer {{ $env.OPENAI_API_KEY }}` as value

### Step 5: Activate the Workflow

1. Click the **"Activate"** toggle in the top right
2. The workflow is now ready to receive webhook requests

## Method 2: Manual Creation

If import doesn't work, you can create the workflow manually:

### Step 1: Create New Workflow

1. Click **"Add Workflow"**
2. Name it "FAQ to Qdrant Workflow"

### Step 2: Add Nodes

Add these nodes in order:

1. **Webhook Trigger**

   - Type: Webhook
   - Method: POST
   - Path: `faq-to-qdrant`
   - Response Mode: Respond to Webhook

2. **Read Binary File**

   - Type: Read Binary File
   - File Path: `data/processed/premiere_suites_faq_data.jsonl`

3. **Code Node (Parse JSONL)**

   - Type: Code
   - Copy the JavaScript code from the workflow file

4. **HTTP Request (Delete Collection)**

   - Method: DELETE
   - URL: `{{ $env.QDRANT_URL }}/collections/faq_collection`
   - Authentication: Header Auth with api-key

5. **HTTP Request (Create Collection)**

   - Method: PUT
   - URL: `{{ $env.QDRANT_URL }}/collections/faq_collection`
   - Body: `{"vectors": {"size": 1536, "distance": "Cosine"}}`
   - Authentication: Header Auth with api-key

6. **Code Node (Vectorize FAQs)**

   - Type: Code
   - Copy the JavaScript code from the workflow file

7. **HTTP Request (Get Embeddings)**

   - Method: POST
   - URL: `https://api.openai.com/v1/embeddings`
   - Body: `{"input": "{{ $json.embedding_text }}", "model": "text-embedding-3-small"}`
   - Authentication: Header Auth with Authorization

8. **Code Node (Prepare Upload Data)**

   - Type: Code
   - Copy the JavaScript code from the workflow file

9. **HTTP Request (Upload to Qdrant)**

   - Method: PUT
   - URL: `{{ $env.QDRANT_URL }}/collections/faq_collection/points`
   - Body: `{"points": {{ $json.points }}}`
   - Authentication: Header Auth with api-key

10. **Respond to Webhook**
    - Type: Respond to Webhook
    - Response Body: JSON with success message

### Step 3: Connect Nodes

Connect the nodes in the order listed above.

## Method 3: API Import

You can also import via the n8n API:

```bash
curl -X POST http://localhost:5678/api/v1/workflows \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: your-n8n-api-key" \
  -d @docs/workflows/faq_to_qdrant_workflow_simple.json
```

## Troubleshooting

### Common Issues

1. **Workflow won't import**

   - Check that the JSON file is valid
   - Try the simplified version: `faq_to_qdrant_workflow_simple.json`
   - Clear browser cache and try again

2. **Environment variables not working**

   - Make sure variables are set in n8n Settings → Environment Variables
   - Check that variable names match exactly (case-sensitive)

3. **Authentication errors**

   - Verify API keys are correct
   - Check that authentication is configured in each HTTP Request node
   - Ensure environment variables are properly referenced

4. **File not found errors**
   - Make sure the FAQ data file exists at the specified path
   - Check file permissions
   - Verify the file path in the "Read Binary File" node

### Testing the Workflow

Once imported and configured:

1. **Activate the workflow**
2. **Test with curl:**

   ```bash
   curl -X POST http://localhost:5678/webhook/faq-to-qdrant \
     -H "Content-Type: application/json" \
     -d '{"test": true}'
   ```

3. **Check execution logs** in n8n for any errors

### Getting Help

If you encounter issues:

1. Check the n8n execution logs
2. Verify all environment variables are set
3. Test each node individually
4. Use the simplified workflow version if the full version has issues

The workflow should now be ready to ingest your FAQ data into Qdrant!


