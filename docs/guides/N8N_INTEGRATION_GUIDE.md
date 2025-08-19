# n8n Integration Guide for Premiere Suites Property Search

This guide will help you set up n8n workflows to automate property searches using your Qdrant Cloud vector database.

## What is n8n?

n8n is a powerful workflow automation tool that allows you to:

- **Connect different services** (Slack, Email, CRM, etc.)
- **Automate repetitive tasks** with visual workflows
- **Create webhooks** for external integrations
- **Process data** between different systems
- **Trigger actions** based on events

## Architecture Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Trigger   │───▶│    n8n      │───▶│  Embedding  │───▶│   Qdrant    │
│  (Slack,    │    │  Workflow   │    │   Service   │    │    Cloud    │
│   Email,    │    │             │    │             │    │             │
│   Webhook)  │    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
└─────────────┘    │   Response  │◀───│   Results   │◀───│   Search    │
                   │   Formatter │    │   Formatter │    │   Results   │
                   └─────────────┘    └─────────────┘    └─────────────┘
```

## Prerequisites

- Qdrant Cloud setup completed
- Docker and Docker Compose installed
- Your property data loaded in Qdrant Cloud

## Quick Setup

### 1. Run the n8n Setup Script

```bash
python n8n_setup.py
```

This will create:

- n8n workflow configurations
- Docker Compose files
- Embedding service
- Environment configurations
- Usage examples

### 2. Start n8n with Docker

```bash
docker-compose -f docker-compose.n8n.yml up -d
```

### 3. Access n8n Interface

Open your browser and go to: http://localhost:5678

Login with:

- Username: `admin`
- Password: `your-secure-password` (update in n8n.env)

## Workflow Examples

### 1. Basic Property Search Webhook

**Purpose**: Accept HTTP requests and return property search results

**Workflow Steps**:

1. **Webhook Trigger** - Accepts POST requests
2. **HTTP Request** - Calls Qdrant Cloud API
3. **Set Node** - Formats response
4. **Respond to Webhook** - Returns JSON response

**Usage**:

```bash
curl -X POST http://localhost:5678/webhook/property-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "luxury apartment with pool",
    "limit": 5,
    "city": "Toronto"
  }'
```

### 2. Slack Bot Integration

**Purpose**: Allow users to search properties via Slack messages

**Workflow Steps**:

1. **Slack Trigger** - Listens for messages
2. **IF Node** - Checks if message contains search keywords
3. **Code Node** - Extracts search parameters
4. **HTTP Request** - Calls embedding service
5. **HTTP Request** - Searches Qdrant Cloud
6. **Code Node** - Formats results for Slack
7. **Slack Node** - Sends response back

**Example Slack Commands**:

- `find apartment in Toronto`
- `luxury property with pool`
- `pet friendly apartment in Vancouver`

### 3. Email Automation

**Purpose**: Process property inquiries from emails

**Workflow Steps**:

1. **Email Trigger** - Monitors email inbox
2. **Code Node** - Parses email content
3. **HTTP Request** - Searches properties
4. **Code Node** - Generates HTML response
5. **Email Node** - Sends formatted results

### 4. CRM Integration

**Purpose**: Automatically find properties for new leads

**Workflow Steps**:

1. **CRM Trigger** - New lead created
2. **Code Node** - Extracts property requirements
3. **HTTP Request** - Searches matching properties
4. **Code Node** - Formats recommendations
5. **CRM Node** - Updates lead with properties
6. **Email Node** - Sends follow-up email

## Advanced Workflows

### 1. Multi-Step Property Search

```javascript
// Step 1: Generate embedding
const embeddingResponse = await fetch(
  "http://embedding-service:5000/generate-embedding",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: $input.query }),
  }
);

// Step 2: Search Qdrant
const searchResponse = await fetch(
  `${$env.QDRANT_URL}/collections/premiere_suites_properties/points/search`,
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "api-key": $env.QDRANT_API_KEY,
    },
    body: JSON.stringify({
      vector: embeddingResponse.embedding,
      limit: $input.limit || 10,
      with_payload: true,
    }),
  }
);

// Step 3: Format results
return {
  results: searchResponse.result,
  total_found: searchResponse.result.length,
  query: $input.query,
};
```

### 2. Property Comparison Workflow

**Purpose**: Compare multiple properties and rank them

**Steps**:

1. Search for properties based on criteria
2. Calculate similarity scores
3. Rank properties by multiple factors
4. Generate comparison report
5. Send results via preferred channel

### 3. Automated Property Alerts

**Purpose**: Notify users when new properties match their criteria

**Steps**:

1. Store user preferences in database
2. Periodically check for new properties
3. Match against stored preferences
4. Send notifications for matches
5. Track user engagement

## Integration Examples

### Slack Integration

```javascript
// Slack message handler
if ($input.text.includes("find apartment")) {
  const city = extractCity($input.text);
  const requirements = extractRequirements($input.text);

  const properties = await searchProperties({
    query: requirements,
    city: city,
    limit: 5,
  });

  return formatSlackResponse(properties);
}
```

### Email Integration

```javascript
// Email parser
const emailContent = $input.body;
const requirements = parseEmailRequirements(emailContent);
const contactInfo = extractContactInfo(emailContent);

const properties = await searchProperties(requirements);

return {
  to: contactInfo.email,
  subject: `Property Recommendations for ${requirements.city}`,
  html: generatePropertyEmail(properties),
};
```

### Webhook Integration

```javascript
// Webhook handler
const { query, filters } = $input.body;

const properties = await searchProperties({
  query: query,
  ...filters,
});

return {
  status: "success",
  data: properties,
  timestamp: new Date().toISOString(),
};
```

## Environment Variables

Create a `.env` file for n8n:

```bash
# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key

# n8n Configuration
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your-secure-password

# External Services
SLACK_BOT_TOKEN=xoxb-your-slack-token
EMAIL_SERVICE_API_KEY=your-email-api-key
CRM_API_KEY=your-crm-api-key
```

## Testing Your Workflows

### 1. Test Webhook Endpoints

```bash
# Test property search
curl -X POST http://localhost:5678/webhook/property-search \
  -H "Content-Type: application/json" \
  -d '{"query": "luxury apartment", "limit": 3}'

# Test property filter
curl -X POST http://localhost:5678/webhook/property-filter \
  -H "Content-Type: application/json" \
  -d '{"query": "apartment", "city": "Toronto", "min_rating": 4.0}'
```

### 2. Test Embedding Service

```bash
curl -X POST http://localhost:5000/generate-embedding \
  -H "Content-Type: application/json" \
  -d '{"text": "luxury apartment with pool"}'
```

### 3. Monitor Workflow Execution

- Check n8n execution logs
- Monitor Qdrant Cloud usage
- Verify response times
- Test error handling

## Troubleshooting

### Common Issues

1. **n8n Won't Start**

   - Check Docker is running
   - Verify ports 5678 and 5000 are available
   - Check environment variables

2. **Workflow Execution Fails**

   - Verify Qdrant Cloud credentials
   - Check embedding service is running
   - Review n8n execution logs

3. **Slow Response Times**

   - Monitor Qdrant Cloud performance
   - Check embedding service load
   - Optimize workflow steps

4. **Authentication Errors**
   - Verify API keys are correct
   - Check Qdrant Cloud cluster status
   - Ensure proper headers are sent

### Debugging Tips

1. **Enable Debug Logging**

   ```bash
   N8N_LOG_LEVEL=debug docker-compose -f docker-compose.n8n.yml up
   ```

2. **Test Individual Components**

   - Test embedding service directly
   - Test Qdrant Cloud API directly
   - Test n8n webhooks separately

3. **Monitor Resources**
   - Check Docker container logs
   - Monitor CPU and memory usage
   - Check network connectivity

## Best Practices

### 1. Security

- Use environment variables for sensitive data
- Implement proper authentication
- Validate input data
- Rate limit webhook endpoints

### 2. Performance

- Cache frequently used embeddings
- Batch similar requests
- Use async operations where possible
- Monitor response times

### 3. Reliability

- Implement error handling
- Add retry logic for failed requests
- Use health checks
- Monitor workflow success rates

### 4. Scalability

- Use connection pooling
- Implement request queuing
- Monitor resource usage
- Plan for traffic spikes

## Next Steps

1. **Customize Workflows**: Adapt the provided workflows to your specific needs
2. **Add More Integrations**: Connect with your existing tools and services
3. **Implement Analytics**: Track usage patterns and optimize performance
4. **Scale Up**: Add more properties and expand search capabilities
5. **User Interface**: Create a web interface for property searches

## Support

- **n8n Documentation**: https://docs.n8n.io/
- **n8n Community**: https://community.n8n.io/
- **Qdrant Cloud Docs**: https://cloud.qdrant.io/docs/
- **GitHub Issues**: Create issues for specific problems

For specific help with your setup:

1. Check the logs: `docker-compose -f docker-compose.n8n.yml logs`
2. Verify credentials and environment variables
3. Test individual components
4. Review the workflow execution history in n8n
