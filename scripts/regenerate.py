"""
Regenerate the HTML visualization from data/nodes.csv, data/edges.csv,
and data/views.toml.

Usage (from repo root):
    python scripts/regenerate.py

Reads CSVs and the views file, validates them, and rewrites the embedded
data block in index.html. The `source` column on the CSVs is preserved as
metadata but is not currently displayed in the visualization.
"""
import csv
import json
import re
import tomllib
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
NODES_CSV = REPO_ROOT / 'data' / 'nodes.csv'
EDGES_CSV = REPO_ROOT / 'data' / 'edges.csv'
VIEWS_TOML = REPO_ROOT / 'data' / 'views.toml'
HTML = REPO_ROOT / 'index.html'

VALID_EDGE_TYPES = {'action', 'money', 'regulation', 'information'}
VALID_CATEGORIES = {'actor', 'mechanism'}
VALID_SUBCATEGORIES = {
    'actor': {'regulator', 'operator', 'participant'},
    'mechanism': {'market', 'tariff', 'process'},
}


def parse_views_cell(s):
    return [v.strip() for v in (s or '').split(',') if v.strip()]


def read_csvs():
    with NODES_CSV.open(newline='') as f:
        nodes = []
        for row in csv.DictReader(f):
            row['views'] = parse_views_cell(row.get('views', ''))
            nodes.append(row)
    with EDGES_CSV.open(newline='') as f:
        edges = []
        for row in csv.DictReader(f):
            edges.append({
                'source': row['source_node'],
                'target': row['target_node'],
                'type': row['type'],
                'description': row['description'],
                'citation': row.get('source', ''),
                'views': parse_views_cell(row.get('views', '')),
            })
    return {'nodes': nodes, 'edges': edges}


def read_views():
    if not VIEWS_TOML.exists():
        return []
    with VIEWS_TOML.open('rb') as f:
        raw = tomllib.load(f)
    views = []
    for view_id, fields in raw.items():
        v = {'id': view_id, **fields}
        v.setdefault('default_edge_types', list(VALID_EDGE_TYPES))
        v.setdefault('layout', 'fcose')
        v.setdefault('focus', None)
        v.setdefault('narrative', '')
        views.append(v)
    return views


def validate(data, views):
    node_ids = {n['id'] for n in data['nodes']}
    view_ids = {v['id'] for v in views}
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
        for vid in n['views']:
            if vid not in view_ids:
                errors.append(f"Node {n['id']}: references unknown view '{vid}' (must be defined in views.toml)")

    for i, e in enumerate(data['edges']):
        row_num = i + 2  # +2 for header row and 1-indexing
        if e['source'] not in node_ids:
            errors.append(f"Edge row {row_num}: source '{e['source']}' not found in nodes.csv")
        if e['target'] not in node_ids:
            errors.append(f"Edge row {row_num}: target '{e['target']}' not found in nodes.csv")
        if e['type'] not in VALID_EDGE_TYPES:
            errors.append(f"Edge row {row_num}: invalid type '{e['type']}' (must be one of {VALID_EDGE_TYPES})")
        for vid in e['views']:
            if vid not in view_ids:
                errors.append(f"Edge row {row_num}: references unknown view '{vid}' (must be defined in views.toml)")

    for v in views:
        for et in v['default_edge_types']:
            if et not in VALID_EDGE_TYPES:
                errors.append(f"View '{v['id']}': invalid edge type '{et}' in default_edge_types")
        if v.get('focus') and v['focus'] not in node_ids:
            errors.append(f"View '{v['id']}': focus '{v['focus']}' not found in nodes.csv")

    return errors


def main():
    data = read_csvs()
    views = read_views()
    errors = validate(data, views)
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  - {e}")
        print("\nFix these and re-run.")
        return 1

    data['views'] = views

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
        f"v1.0 · {len(data['nodes'])} nodes · {len(data['edges'])} edges",
        html
    )
    HTML.write_text(html)

    edge_counts = Counter(e['type'] for e in data['edges'])
    cited = sum(1 for e in data['edges'] if e['citation']) + sum(1 for n in data['nodes'] if n.get('source'))
    total = len(data['nodes']) + len(data['edges'])

    view_membership = Counter()
    for n in data['nodes']:
        for vid in n['views']:
            view_membership[vid] += 1

    print(f"OK: {len(data['nodes'])} nodes, {len(data['edges'])} edges, {len(views)} view(s)")
    print(f"  Updated {HTML.relative_to(REPO_ROOT)}")
    print(f"  Edge types: {dict(edge_counts)}")
    print(f"  Sourced: {cited}/{total} rows")
    if views:
        print(f"  View node-membership: {dict(view_membership)}")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
