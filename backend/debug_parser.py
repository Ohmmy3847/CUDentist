"""
Debug Rule Parser
"""
from app.services.flow_parser import FlowParser
from app.core.flows import FLOWS

# Test parsing pain flow
pain_flow = FLOWS["อาการปวด"]
parser = FlowParser(pain_flow)

print("=" * 60)
print("Parsed Nodes:")
print("=" * 60)
for node_id, node in parser.nodes.items():
    print(f"{node_id}: {node.node_type} - {node.content[:50]}")
    if node.children:
        for condition, child in node.children:
            print(f"  -> [{condition}] {child.node_id}")
print()

print("=" * 60)
print("Start Node:")
print("=" * 60)
if parser.start_node:
    print(f"ID: {parser.start_node.node_id}")
    print(f"Type: {parser.start_node.node_type}")
    print(f"Content: {parser.start_node.content}")
else:
    print("NO START NODE FOUND!")
print()

print("=" * 60)
print("Evaluating with pain_score=0:")
print("=" * 60)
result = parser.evaluate({"pain_score": 0})
print(f"Result: {result['risk_level']}")
print(f"Reason: {result['reason']}")
print(f"Path ({len(result['path'])} nodes):")
for step in result['path']:
    print(f"  {step['node_id']}: {step['type']} - {step['content'][:60]}")
