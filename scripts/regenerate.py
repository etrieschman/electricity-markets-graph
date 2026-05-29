"""
Regenerate the HTML visualization from data/nodes.csv and data/edges.csv.

Usage (from repo root):
    python scripts/regenerate.py

Reads both CSVs, validates them, and rewrites the embedded data block
in index.html. The `source` column is preserved as metadata but is not
currently displayed in the visualization.
"""
import csv
import json
import re
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
NODES_CSV = REPO_ROOT / 'data' / 'nodes.csv'
EDGES_CSV = REPO_ROOT / 'data' / 'edges.csv'
HTML = REPO_ROOT / 'index.html'

VALID_EDGE_TYPES = {'action', 'money', 'regulation', 'information'}
VALID_CATEGORIES = {'actor', 'mechanism'}
VALID_SUBCATEGORIES = {
    'actor': {'regulator', 'operator', 'participant'},
    'mechanism': {'market', 'tariff', 'process'},
}


def read_csvs():
    with NODES_CSV.open(newline='') as f:
        nodes = [dict(row) for row in csv.DictReader(f)]
    with EDGES_CSV.open(newline='') as f:
        edges = []
        for row in csv.DictReader(f):
            # Rename source_node/target_node to source/target for the graph data
            edges.append({
                'source': row['source_node'],
                'target': row['target_node'],
                'type': row['type'],
                'description': row['description'],
                'citation': row.get('source', ''),  # preserve citation but rename to avoid collision
            })
    return {'nodes': nodes, 'edges': edges}


def validate(data):
    node_ids = {n['id'] for n in data['nodes']}
    errors = []

    seen_ids = set()
    for n in data['nodes']:
        if not n['id']:
            errors.append("Node with empty id")
            continue
        if n['id'] in seen_ids:
            errors.append(f"Duplicate node id: {n['id']}")
        seen_ids.add(n['id'])
        if n['category'] not in VALID_CATEGORIES:
            errors.append(f"Node {n['id']}: invalid category '{n['category']}' (must be one of {VALID_CATEGORIES})")
            continue
        sub = n.get('subcategory', '')
        if sub not in VALID_SUBCATEGORIES[n['category']]:
            errors.append(f"Node {n['id']}: invalid subcategory '{sub}' for category '{n['category']}' (must be one of {VALID_SUBCATEGORIES[n['category']]})")

    for i, e in enumerate(data['edges']):
        row_num = i + 2  # +2 for header row and 1-indexing
        if e['source'] not in node_ids:
            errors.append(f"Edge row {row_num}: source '{e['source']}' not found in nodes.csv")
        if e['target'] not in node_ids:
            errors.append(f"Edge row {row_num}: target '{e['target']}' not found in nodes.csv")
        if e['type'] not in VALID_EDGE_TYPES:
            errors.append(f"Edge row {row_num}: invalid type '{e['type']}' (must be one of {VALID_EDGE_TYPES})")
    return errors


def main():
    data = read_csvs()
    errors = validate(data)
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  - {e}")
        print("\nFix these in the CSVs and re-run.")
        return 1

    html = HTML.read_text()
    data_str = json.dumps(data)
    replacement = f'const GRAPH_DATA = {data_str};'
    html = re.sub(
        r'const GRAPH_DATA = \{.*?\};',
        lambda m: replacement,
        html,
        count=1,
        flags=re.DOTALL
    )
    html = re.sub(
        r'v\d+\.\d+ · \d+ nodes · \d+ edges',
        f"v0.1 · {len(data['nodes'])} nodes · {len(data['edges'])} edges",
        html
    )
    HTML.write_text(html)

    edge_counts = Counter(e['type'] for e in data['edges'])
    cited = sum(1 for e in data['edges'] if e['citation']) + sum(1 for n in data['nodes'] if n.get('source'))
    total = len(data['nodes']) + len(data['edges'])

    print(f"OK: {len(data['nodes'])} nodes, {len(data['edges'])} edges")
    print(f"  Updated {HTML.relative_to(REPO_ROOT)}")
    print(f"  Edge types: {dict(edge_counts)}")
    print(f"  Sourced: {cited}/{total} rows")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
