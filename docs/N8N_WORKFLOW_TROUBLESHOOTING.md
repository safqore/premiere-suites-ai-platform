# n8n Workflow Troubleshooting Guide

## Common Issues When Nodes Don't Display or Connect

### 1. **Placeholder Credentials and URLs**

**Problem**: Nodes with placeholder credentials or URLs may not display properly.

**Solution**:

- Replace `"YOUR_OPENAI_CREDENTIAL"` with actual credential names
- Replace `"YOUR_QDRANT_HOST"` and `"YOUR_FAQ_COLLECTION"` with actual values
- Or remove credentials entirely and set them up in n8n after importing

### 2. **Missing Required Fields**

**Problem**: Nodes missing required fields like `position`, `parameters`, or `type`.

**Solution**: Ensure each node has:

```json
{
  "name": "Node Name",
  "type": "n8n-nodes-base.nodeType",
  "typeVersion": 1,
  "position": [x, y],
  "parameters": {}
}
```

### 3. **Invalid Connections**

**Problem**: Connections referencing non-existent nodes or having invalid structure.

**Solution**: Check that:

- All connection target nodes exist
- Connection structure follows n8n format
- No circular references

### 4. **Complex Workflow Structure**

**Problem**: Very complex workflows with many conditional branches may not render properly.

**Solution**:

- Start with a simplified version
- Gradually add complexity
- Test each section independently

## Quick Fixes

### Option 1: Use the Simplified Workflow

Import `docs/workflows/Premier Suites Concierge v1 (Simplified).json` which has:

- Basic structure that should display properly
- No external dependencies
- Simple conditional logic

### Option 2: Use the Fixed Workflow

Import `docs/workflows/Premier Suites Concierge v1 (Hardened).json.fixed` which has:

- All placeholder issues resolved
- Proper structure maintained
- Ready for credential setup

### Option 3: Manual Import Steps

1. Create a new workflow in n8n
2. Add a Webhook node manually
3. Add Function nodes for logic
4. Add IF nodes for conditions
5. Add Respond to Webhook node
6. Connect them manually

## Import Process

1. **In n8n**:

   - Go to Workflows
   - Click "Import from file"
   - Select the workflow JSON file
   - Click "Import"

2. **After Import**:
   - Check if nodes are visible
   - Verify connections are drawn
   - Set up any missing credentials
   - Test the workflow

## Testing the Workflow

1. **Activate the workflow**
2. **Copy the webhook URL**
3. **Test with curl or Postman**:

```bash
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "sessionId": "test123"}'
```

## Common Error Messages

- **"Node not found"**: Check node names in connections
- **"Invalid credential"**: Set up credentials in n8n
- **"Connection failed"**: Verify target nodes exist
- **"Workflow not active"**: Activate the workflow first

## Getting Help

If issues persist:

1. Check the n8n execution logs
2. Verify JSON syntax is valid
3. Try importing the simplified version first
4. Contact n8n support for complex issues

## Files Available

- `Premier Suites Concierge v1 (Simplified).json` - Basic working version
- `Premier Suites Concierge v1 (Hardened).json.fixed` - Fixed complex version
- `fix_n8n_workflow.py` - Script to fix common issues
