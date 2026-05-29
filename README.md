# How U.S. Electricity Markets Work

A learning tool for the inner workings of U.S. wholesale electricity markets, structured as a typed multigraph and built as a reference object for reading groups, classes, and research on market design.

The graph treats the electricity market as a network of **actors** (institutional entities that make decisions) and **markets** (recurring or standing arrangements where transactions clear, spanning the liquidity gradient from ISO auctions to administratively-set retail tariffs), connected by four types of edges: **action**, **money**, **regulation**, and **information**.

**[View the interactive graph](https://etrieschman.github.io/electricity-markets-graph/)**

## Motivation

Existing organizing frameworks for U.S. electricity markets (Hogan's optimization tree, Stoft's market-failure taxonomy, ISO training materials' product taxonomy, Joskow's regulatory-economics lens) each privilege one dimension of the system and lose the others. This repo proposes a typed multigraph as a unifying object: each existing framework becomes a *view* on the same graph, and the dense edge regions correspond to where contested research questions live (FTR revenue adequacy, capacity-energy interactions, large-load cost allocation, DCOPF approximation gaps).

See [`docs/framework.md`](docs/framework.md) for the full framework description.

## Repo layout

```
.
├── index.html               # The interactive visualization (open in any browser)
├── data/
│   ├── nodes.csv            # All nodes (id, name, category, description, source)
│   └── edges.csv            # All edges (source_node, target_node, type, description, source)
├── scripts/
│   └── regenerate.py        # Reads CSVs, validates, updates index.html (stdlib only)
└── docs/
    └── framework.md         # Framework description and design principles
```

## Workflow

**To view the graph:** open `index.html` in any browser. No installation needed.

**To edit the graph:**

1. Edit `data/nodes.csv` and/or `data/edges.csv` in your editor of choice (any spreadsheet program, or directly in the text)
2. From the repo root, run:
   ```
   python scripts/regenerate.py
   ```
3. Refresh `index.html` in the browser


## CSV schema

**`data/nodes.csv`**

| Column | Description |
|---|---|
| `id` | Lowercase identifier, no spaces. Used as key throughout. |
| `name` | Display name. |
| `category` | Either `actor` or `market`. |
| `description` | What this node is, what it does, why it's distinct. |
| `source` | Citation for the description — paper, FERC order, ISO manual, etc. Optional. |

**`data/edges.csv`**

| Column | Description |
|---|---|
| `source_node` | ID of the source node (where the edge starts). |
| `target_node` | ID of the target node (where the edge ends). |
| `type` | One of `action`, `money`, `regulation`, `information`. |
| `description` | What this edge represents — the specific action, money flow, rule, or information transfer. |
| `source` | Citation for the edge — paper, tariff section, FERC order, etc. Optional. |

Edges are directed. For mutual relationships, add two rows. Multiple edges of different types between the same node pair are expected and valid.

## Contributing

Edits to nodes and edges are welcome — particularly from people with hands-on ISO operations, FERC practice, or market design backgrounds. The current graph is a first pass and known to have gaps. Please reference [`docs/framework.md`](docs/framework.md) for design principles.

## License

MIT — see [LICENSE](LICENSE).
