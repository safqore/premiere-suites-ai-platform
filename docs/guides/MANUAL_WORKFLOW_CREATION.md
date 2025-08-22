# Manual Workflow Creation in n8n

This guide will walk you through creating the FAQ to Qdrant workflow manually in n8n, ensuring all connections work properly.

## Step 1: Create New Workflow

1. Open n8n at `http://localhost:5678`
2. Click **"Add Workflow"**
3. Name it "FAQ to Qdrant Workflow"

## Step 2: Add Webhook Trigger

1. Click the **"+"** button to add a node
2. Search for **"Webhook"**
3. Select **"Webhook"** node
4. Configure the node:
   - **HTTP Method**: POST
   - **Path**: `faq-to-qdrant`
   - **Response Mode**: Respond to Webhook
5. Click **"Save"**

## Step 3: Add Read Binary File Node

1. Click the **"+"** button again
2. Search for **"Read Binary File"**
3. Select **"Read Binary File"** node
4. Configure the node:
   - **File Path**: `data/processed/premiere_suites_faq_data.jsonl`
5. Click **"Save"**
6. **Connect**: Drag from Webhook Trigger to Read Binary File

## Step 4: Add Code Node (Parse JSONL)

1. Click the **"+"** button
2. Search for **"Code"**
3. Select **"Code"** node
4. Configure the node:

   - **Language**: JavaScript
   - **Code**:

   ```javascript
   // Parse JSONL file content
   const fileContent = $input.first().json.data;
   const lines = fileContent.split("\n").filter((line) => line.trim());

   const faqData = [];
   let metadata = null;
   let summary = null;

   for (const line of lines) {
     try {
       const parsed = JSON.parse(line);

       if (parsed.type === "metadata") {
         metadata = parsed;
       } else if (parsed.type === "summary") {
         summary = parsed;
       } else if (parsed.type === "faq") {
         faqData.push(parsed);
       }
     } catch (error) {
       console.log("Error parsing line:", line, error);
     }
   }

   return [
     {
       json: {
         metadata,
         summary,
         faqs: faqData,
         total_faqs: faqData.length,
       },
     },
   ];
   ```

5. Click **"Save"**
6. **Connect**: Drag from Read Binary File to Code node

## Step 5: Add HTTP Request Node (Delete Collection)

1. Click the **"+"** button
2. Search for **"HTTP Request"**
3. Select **"HTTP Request"** node
4. Configure the node:
   - **Method**: DELETE
   - **URL**: `{{ $env.QDRANT_URL }}/collections/faq_collection`
   - **Authentication**: Header Auth
   - **Name**: `api-key`
   - **Value**: `{{ $env.QDRANT_API_KEY }}`
5. Click **"Save"**
6. **Connect**: Drag from Code node to HTTP Request node

## Step 6: Add HTTP Request Node (Create Collection)

1. Click the **"+"** button
2. Search for **"HTTP Request"**
3. Select **"HTTP Request"** node
4. Configure the node:
   - **Method**: PUT
   - **URL**: `{{ $env.QDRANT_URL }}/collections/faq_collection`
   - **Authentication**: Header Auth
   - **Name**: `api-key`
   - **Value**: `{{ $env.QDRANT_API_KEY }}`
   - **Send Body**: ✓
   - **Body Parameters**:
     - **Name**: `vectors`
     - **Value**: `{"size": 1536, "distance": "Cosine"}`
5. Click **"Save"**
6. **Connect**: Drag from Delete Collection to Create Collection

## Step 7: Add Code Node (Vectorize FAQs)

1. Click the **"+"** button
2. Search for **"Code"**
3. Select **"Code"** node
4. Configure the node:

   - **Language**: JavaScript
   - **Code**:

   ```javascript
   // Vectorize FAQ data
   const faqs = $input.first().json.faqs;
   const vectorizedFaqs = [];

   for (const faq of faqs) {
     const textForEmbedding = `Question: ${faq.question}\nAnswer: ${faq.answer}`;

     vectorizedFaqs.push({
       id: faq.id,
       question: faq.question,
       answer: faq.answer,
       category: faq.category,
       tags: faq.tags,
       source_url: faq.source_url,
       text_chunk: faq.text_chunk,
       embedding_text: textForEmbedding,
     });
   }

   return [
     {
       json: {
         vectorized_faqs: vectorizedFaqs,
         total_count: vectorizedFaqs.length,
       },
     },
   ];
   ```

5. Click **"Save"**
6. **Connect**: Drag from Create Collection to Code node

## Step 8: Add HTTP Request Node (Get Embeddings)

1. Click the **"+"** button
2. Search for **"HTTP Request"**
3. Select **"HTTP Request"** node
4. Configure the node:
   - **Method**: POST
   - **URL**: `https://api.openai.com/v1/embeddings`
   - **Authentication**: Header Auth
   - **Name**: `Authorization`
   - **Value**: `Bearer {{ $env.OPENAI_API_KEY }}`
   - **Send Body**: ✓
   - **Body Parameters**:
     - **Name**: `input`
     - **Value**: `{{ $json.embedding_text }}`
     - **Name**: `model`
     - **Value**: `text-embedding-3-small`
5. Click **"Save"**
6. **Connect**: Drag from Vectorize FAQs to HTTP Request node

## Step 9: Add Code Node (Prepare Upload Data)

1. Click the **"+"** button
2. Search for **"Code"**
3. Select **"Code"** node
4. Configure the node:

   - **Language**: JavaScript
   - **Code**:

   ```javascript
   // Prepare data for Qdrant upload
   const faqs = $input.all();
   const uploadData = [];

   for (const faq of faqs) {
     const faqData = faq.json;
     const embedding = faqData.data[0].embedding;

     uploadData.push({
       id: faqData.id,
       vector: embedding,
       payload: {
         question: faqData.question,
         answer: faqData.answer,
         category: faqData.category,
         tags: faqData.tags,
         source_url: faqData.source_url,
         text_chunk: faqData.text_chunk,
         timestamp: new Date().toISOString(),
       },
     });
   }

   return [
     {
       json: {
         points: uploadData,
         total_points: uploadData.length,
       },
     },
   ];
   ```

5. Click **"Save"**
6. **Connect**: Drag from Get Embeddings to Code node

## Step 10: Add HTTP Request Node (Upload to Qdrant)

1. Click the **"+"** button
2. Search for **"HTTP Request"**
3. Select **"HTTP Request"** node
4. Configure the node:
   - **Method**: PUT
   - **URL**: `{{ $env.QDRANT_URL }}/collections/faq_collection/points`
   - **Authentication**: Header Auth
   - **Name**: `api-key`
   - **Value**: `{{ $env.QDRANT_API_KEY }}`
   - **Send Body**: ✓
   - **Body Parameters**:
     - **Name**: `points`
     - **Value**: `{{ $json.points }}`
5. Click **"Save"**
6. **Connect**: Drag from Prepare Upload Data to HTTP Request node

## Step 11: Add Respond to Webhook Node

1. Click the **"+"** button
2. Search for **"Respond to Webhook"**
3. Select **"Respond to Webhook"** node
4. Configure the node:
   - **Respond With**: JSON
   - **Response Body**:
   ```json
   {
     "status": "success",
     "message": "FAQ data ingested successfully",
     "collection": "faq_collection",
     "total_faqs": "{{ $('Parse JSONL').first().json.total_faqs }}",
     "vector_size": 1536,
     "timestamp": "{{ new Date().toISOString() }}"
   }
   ```
5. Click **"Save"**
6. **Connect**: Drag from Upload to Qdrant to Respond to Webhook

## Step 12: Set Environment Variables

1. Go to **Settings** → **Environment Variables**
2. Add these variables:
   ```
   QDRANT_URL=https://your-cluster.qdrant.io
   QDRANT_API_KEY=your-qdrant-api-key
   OPENAI_API_KEY=your-openai-api-key
   ```

## Step 13: Activate and Test

1. Click the **"Activate"** toggle in the top right
2. Test with curl:
   ```bash
   curl -X POST http://localhost:5678/webhook/faq-to-qdrant \
     -H "Content-Type: application/json" \
     -d '{"test": true}'
   ```

## Troubleshooting

### If connections don't work:

1. Make sure you're dragging from the **output dot** of one node to the **input dot** of the next node
2. The connection line should appear when you drag
3. If it doesn't connect, try clicking and dragging again

### If nodes don't save:

1. Make sure all required fields are filled
2. Check that the node configuration is complete
3. Try refreshing the page and starting over

### If environment variables don't work:

1. Make sure they're set in n8n Settings → Environment Variables
2. Check that the variable names match exactly
3. Restart n8n after adding environment variables

This manual approach ensures that all connections are properly established and the workflow will work correctly!


