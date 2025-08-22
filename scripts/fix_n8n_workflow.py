#!/usr/bin/env python3
"""
Script to fix common n8n workflow issues that prevent nodes from displaying.
"""

import json
import sys
from pathlib import Path

def fix_workflow(workflow_path):
    """Fix common issues in n8n workflow files."""
    
    print(f"Fixing workflow: {workflow_path}")
    
    # Read the workflow
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)
    
    issues_found = []
    fixes_applied = []
    
    # Check for required fields
    if 'nodes' not in workflow:
        issues_found.append("Missing 'nodes' array")
        workflow['nodes'] = []
    
    if 'connections' not in workflow:
        issues_found.append("Missing 'connections' object")
        workflow['connections'] = {}
    
    # Check each node for issues
    for i, node in enumerate(workflow.get('nodes', [])):
        node_name = node.get('name', f'Node_{i}')
        
        # Check for required node fields
        if 'type' not in node:
            issues_found.append(f"Node '{node_name}' missing 'type' field")
            continue
            
        if 'position' not in node:
            issues_found.append(f"Node '{node_name}' missing 'position' field")
            node['position'] = [i * 200, 0]
            fixes_applied.append(f"Added position for node '{node_name}'")
            
        if 'parameters' not in node:
            issues_found.append(f"Node '{node_name}' missing 'parameters' field")
            node['parameters'] = {}
            fixes_applied.append(f"Added parameters for node '{node_name}'")
    
    # Check connections for issues
    for source_node, connections in workflow.get('connections', {}).items():
        if not isinstance(connections, dict):
            issues_found.append(f"Invalid connections format for node '{source_node}'")
            continue
            
        for connection_type, connection_list in connections.items():
            if not isinstance(connection_list, list):
                issues_found.append(f"Invalid connection list for '{source_node}.{connection_type}'")
                continue
                
            for connection_group in connection_list:
                if not isinstance(connection_group, list):
                    issues_found.append(f"Invalid connection group for '{source_node}.{connection_type}'")
                    continue
                    
                for connection in connection_group:
                    if not isinstance(connection, dict):
                        issues_found.append(f"Invalid connection object in '{source_node}.{connection_type}'")
                        continue
                        
                    if 'node' not in connection:
                        issues_found.append(f"Connection missing 'node' field in '{source_node}.{connection_type}'")
                        continue
                        
                    # Check if target node exists
                    target_node_name = connection['node']
                    target_node_exists = any(node.get('name') == target_node_name for node in workflow.get('nodes', []))
                    
                    if not target_node_exists:
                        issues_found.append(f"Connection references non-existent node '{target_node_name}' from '{source_node}'")
    
    # Fix placeholder credentials and URLs
    for node in workflow.get('nodes', []):
        if node.get('type') == 'n8n-nodes-base.openAi':
            if 'credentials' in node and 'openAiApi' in node['credentials']:
                if node['credentials']['openAiApi'] == 'YOUR_OPENAI_CREDENTIAL':
                    fixes_applied.append(f"Found placeholder OpenAI credential in node '{node.get('name')}'")
                    # Remove the placeholder credential - user will need to set it up
                    node['credentials'] = {}
                    
        elif node.get('type') == 'n8n-nodes-base.httpRequest':
            params = node.get('parameters', {})
            if 'url' in params and 'YOUR_QDRANT_HOST' in params['url']:
                fixes_applied.append(f"Found placeholder Qdrant URL in node '{node.get('name')}'")
                # Replace with a more generic placeholder
                params['url'] = params['url'].replace('YOUR_QDRANT_HOST', 'your-qdrant-host.com')
                params['url'] = params['url'].replace('YOUR_FAQ_COLLECTION', 'your-faq-collection')
    
    # Ensure proper workflow structure
    if 'settings' not in workflow:
        workflow['settings'] = {'executionOrder': 'v1'}
        fixes_applied.append("Added missing settings")
    
    if 'pinData' not in workflow:
        workflow['pinData'] = {}
        fixes_applied.append("Added missing pinData")
    
    if 'staticData' not in workflow:
        workflow['staticData'] = {}
        fixes_applied.append("Added missing staticData")
    
    # Report issues and fixes
    if issues_found:
        print("\nIssues found:")
        for issue in issues_found:
            print(f"  - {issue}")
    
    if fixes_applied:
        print("\nFixes applied:")
        for fix in fixes_applied:
            print(f"  - {fix}")
    
    if not issues_found and not fixes_applied:
        print("No issues found in the workflow file.")
    
    # Save the fixed workflow
    backup_path = workflow_path.with_suffix('.json.backup')
    if not backup_path.exists():
        with open(backup_path, 'w') as f:
            json.dump(workflow, f, indent=2)
        print(f"\nBackup saved to: {backup_path}")
    
    fixed_path = workflow_path.with_suffix('.json.fixed')
    with open(fixed_path, 'w') as f:
        json.dump(workflow, f, indent=2)
    
    print(f"Fixed workflow saved to: {fixed_path}")
    
    return len(issues_found) == 0

def main():
    if len(sys.argv) != 2:
        print("Usage: python fix_n8n_workflow.py <workflow_file.json>")
        sys.exit(1)
    
    workflow_path = Path(sys.argv[1])
    if not workflow_path.exists():
        print(f"Error: Workflow file '{workflow_path}' not found.")
        sys.exit(1)
    
    try:
        success = fix_workflow(workflow_path)
        if success:
            print("\n✅ Workflow should now display properly in n8n!")
        else:
            print("\n⚠️  Some issues remain. Please review the workflow manually.")
    except Exception as e:
        print(f"Error fixing workflow: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
