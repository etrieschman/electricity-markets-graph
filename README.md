# Electricity Markets — A Framework Graph

A typed multigraph of U.S. wholesale electricity market structure, built as a reference object for reading groups, classes, and research on market design.

The graph treats the electricity market as a network of **actors** (institutional entities that make decisions) and **markets** (recurring or standing arrangements where transactions clear, spanning the liquidity gradient from ISO auctions to bilateral PPAs to administratively-set retail tariffs), connected by four types of edges: **action**, **money**, **regulation**, and **information**.

→ **[View the interactive graph](https://YOUR_USERNAME.github.io/electricity-markets-graph/)** *(after enabling GitHub Pages)*

## Motivation

Existing organizing frameworks for U.S. electricity markets (Hogan's optimization tree, Stoft's market-failure taxonomy, ISO training materials' product taxonomy, Joskow's regulatory-economics lens) each privilege one dimension of the system and lose the others. This repo proposes a typed multigraph as a unifying object: each existing framework becomes a *view* on the same graph, and the dense edge regions correspond to where contested research questions live (FTR revenue adequacy, capacity-energy interactions, large-load cost allocation, DCOPF approximation gaps).

See [`docs/framework.md`](docs/framework.md) for the full framework description and design history.

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

The script uses only the Python standard library — no dependencies to install. It validates that all edge source/target IDs match real nodes and that all categories and types are valid; it refuses to write the HTML if anything fails.

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

## Publishing the graph

To make the graph viewable as a webpage:

1. Push the repo to GitHub
2. Go to **Settings → Pages**
3. Set source to `main` branch, `/` (root)
4. Wait ~1 minute for the URL to go live at `https://YOUR_USERNAME.github.io/electricity-markets-graph/`
5. Update the link at the top of this README

## Contributing

Edits to nodes and edges are welcome — particularly from people with hands-on ISO operations, FERC practice, or market design backgrounds. The current graph is a first pass and known to have gaps.

**Adding or removing nodes** should follow the compression rule:

> Two nodes should be collapsed only when they share the same edge types to the same neighbors. If collapsing hides an edge (especially one between them, or to a distinct neighbor), they need to stay separate.

This rule is what gives the graph its current granularity. If you find a node that violates it (genuinely distinct edges suggest it should be split) or two nodes that satisfy it (collapse them), please open an issue.

**Adding or modifying edges** is more flexible. The four edge types are:

- **action** — an actor doing something (bidding, dispatching, filing, voting)
- **money** — value flowing between nodes (settlements, payments, cost recovery)
- **regulation** — rules constraining behavior or determining money amounts
- **information** — data, models, forecasts, prices, telemetry flowing between nodes

When adding edges or nodes, please populate the `source` column where possible — even informal references (`PJM Manual 11`, `Hogan 1992`, `FERC Order 2023`) help future contributors verify the framework against the literature and operational reality.

## Status

**v0.1** — initial enumeration. 17 nodes, 77 edges, 0 sources cited. Expect substantial revision as the framework is stress-tested against real research questions and operational practices.

## License

MIT — see [LICENSE](LICENSE).
