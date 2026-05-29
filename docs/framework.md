# Framework

This document describes the framework underlying the graph: the node typology, edge typology, and design principles. It also captures the reasoning where useful.

## Object

The framework treats the U.S. electricity market as a **typed multigraph**. Nodes have one of two types (actor, market). Directed adges have one of four types (action, money, regulation, information). Multiple edges of different types are allowed between the same pair of nodes — in fact, a lot of structure lives in this space.

The graph is the *reference object*. Specific topics (FTR design, capacity adequacy, large-load policy, DCOPF approximation gaps) are *subgraphs* of it.

## Nodes

### Two categories, six subcategories

Each node has a **category** (`actor` or `mechanism`) and a **subcategory** that refines it.

**Actor** — an institutional entity that makes decisions. Three subcategories:

- **Regulator** — sets rules with statutory authority. `ferc`, `puc`, `nerc`, `legislature`.
- **Operator** — institutional intermediary that runs markets or owns transmission assets, but doesn't take positions and isn't a principal regulator. `iso`, `to`.
- **Participant** — buys, sells, hedges, or consumes. `generators`, `lses`, `traders`, `customers`.

**Mechanism** — a recurring or standing arrangement that determines transactions. Three subcategories spanning the *liquidity gradient*:

- **Market** — transactions clear, whether by central auction or OTC negotiation. `dam`, `rtm`, `as`, `capacity`, `ftr`, `bilateral`.
- **Tariff** — administratively-set price schedule. No clearing; the rate structure determines what counterparties owe. `oatt` (FERC-regulated, payable by transmission users, remitted to TOs), `retail` (PUC-regulated, payable by customers, collected by LSEs).
- **Process** — recurring multi-step administrative procedure that produces assignments or eligibility. `interconnection` (queue and study), `arr` (allocation formula).

The earlier graph used a binary `actor` / `market` typing and called OATT, retail, and ARR "markets" — a stretch since none of them clear with bids and offers. The current taxonomy fixes that without losing structural content.

- **Notes on this decision**
  - **Generators / LSEs / traders are split because they have genuinely different edge profiles.** Generators are the only actors with interconnection, NERC GO/GOP, capacity supply, and AS supply edges. LSEs are the only ones with ARR nomination, retail-customer money inflows, PUC regulation, and RPS obligations. Traders have only DAM/RTM/FTR/bilateral financial positions — no interconnection, no NERC, no capacity, no retail. Collapsing them hides edges the framework needs to express.
  - **Bilateral / OTC is a market node.** Earlier versions of the graph treated bilateral contracts as direct actor-to-actor edges, on the reasoning that they don't clear centrally. The current view is that they belong on the liquidity gradient between cleared auctions and administrative rates: PPAs, tolling, bilateral RA, and financial CFDs are recurring arrangements with standardized settlement references (DAM LMPs as the energy benchmark) even though no single counterparty clears them. Per the money-through-mechanisms rule below, PPA money flows `lses → bilateral → generators` — the bilateral node is the conceptual venue.
  - **OATT and retail are split because they have different regulators, payers, and recipients.** OATT is FERC-regulated, paid by transmission users (generators, LSEs, traders), and remitted to TOs. Retail tariffs are PUC-regulated, paid by customers, and collected by LSEs. They share no neighbors, so the compression rule keeps them apart.
  - **Regulatory constructs collapse into edges.** A FERC order is an action by FERC that modifies the rules governing some market or actor. NERC standards are constraints NERC imposes on ISOs, TOs, and generators. State RPS policies are obligations legislatures impose on LSEs. In every case, the "construct" is really *an actor exercising authority over another node*, which is exactly what a regulation edge is. Treating them as edges rather than nodes simplifies the graph without losing any structure.
  - **Physical objects collapse into actor/mechanism attributes.** Generators-as-firms are actors; generators-as-physical-equipment are an attribute of those actors. Lines and loads are attributes of TOs and customers respectively. The "physical reality" of the grid enters the graph through information edges (the ISO supplies a network model to DAM) and action edges (a TO operates a line). For a framework focused on market structure, this is sufficient — the physical layer is presupposed rather than represented.

## Edges

### Four types
- **Action** — an actor doing something. Examples: a generator submitting an offer into DAM, an LSE filing a rate case, FERC issuing an order, a customer paying a bill, a TO conducting an interconnection study.
- **Money** — value flowing between nodes. Examples: load paying the ISO for cleared DAM energy, the ISO paying generators from collected revenues, customers paying retail bills, OATT collections flowing to TOs, FTR auction revenues funding ARR distributions.
- **Regulation** — rules constraining behavior or determining how money amounts are set. Examples: FERC approving the ISO tariff, NERC reliability standards binding the ISO, state PUCs setting retail rates, must-offer obligations from the capacity market constraining DAM bidding. Two flavors coexist in the graph: **principal regulation** (a regulator with statutory authority sets the rules — `ferc → iso`, `puc → retail`) and **delegated operational rulemaking** (the ISO sets implementation rules within a FERC-approved tariff — `iso → dam`). Both are "rules constraining behavior" by the definition above, but the source of authority differs.
- **Information** — data, models, forecasts, prices, telemetry flowing between nodes. Examples: the ISO supplying a network model to DAM clearing, RTM clearing results flowing back to the ISO for settlement, DAM LMPs being the reference price PPAs settle against, historical load data feeding the ARR allocation formula.

### Edges can exist between any pair of node types

Actor-actor edges: FERC regulates ISO; FERC oversees NERC; PUCs approve LSE tariffs; LSEs procure PPAs from generators.

Market-market edges: DAM positions are the financial baseline RTM settles against; DAM congestion rents fund FTR settlement; capacity must-offer obligations constrain DAM bidding.

Actor-market edges: the canonical ones — generators offering into DAM, LSEs bidding demand, traders taking financial positions, all being regulated by tariffs.

### Money edges: ISO is the counterparty for cleared transactions; bilateral is the exception

For every centrally-cleared transaction (DAM, RTM, AS, capacity, FTR), money flows actor-to-ISO and ISO-to-actor — symmetric in both directions, with the ISO as the legal central counterparty. The cleared markets themselves don't carry money edges; their role is captured in the **information** and **action** edges that show what they determine and who participates.

For bilateral and direct transactions, money flows through the mechanism (bilateral) or counterparty-to-counterparty (retail, direct construction), with no ISO in the path. The full rule, by subcategory:

- **Cleared markets** (DAM, RTM, AS, capacity, FTR): no money edges. Money for cleared transactions flows `actor ↔ iso` directly. The market's role is captured by:
  - `iso → market` (information) — ISO supplies the network model, contingency list, etc.
  - `market → iso` (information) — clearing outputs (LMPs, cleared positions) flow back to ISO for settlement
  - `actor → market` (action) — bids and offers submitted into clearing
- **Bilateral**: money flows through. `lses → bilateral → generators`, `customers → bilateral → generators`. Bilateral has no central counterparty, so the bilateral node IS the conceptual venue. (This is the principled exception to "cleared markets have no money edges" — bilateral isn't centrally cleared.)
- **Tariffs** (transmission tariffs, retail): money flows around. For OATT, the cash flows `lses → iso → to` with `oatt → iso` (information) determining amounts. For retail, the cash flows `customers → lses` with `retail → customers` (information) determining amounts.
- **Processes** (ARR, interconnection): money flows around. ARR's cash distribution runs through the ISO (`iso → lses`) with `ftr → arr` (information) explaining the funding source. Interconnection's cash runs direct (`generators → to` for construction, `generators → iso` for study deposits).

Examples:

- DAM cleared energy: `lses → iso` and `iso → generators` (money). The DAM node has `iso → dam` (info) for the network model, `dam → iso` (info) for clearing outputs, and `lses → dam` (action) for bidding — but no money.
- Bilateral PPA: `lses → bilateral → generators` (money). Bilateral is the venue; no ISO.
- Transmission tariff: `lses → iso → to` (money). The `oatt` node sets the amount via information.
- ARR cash: `iso → lses` (money), funded from FTR auction revenue collected via `lses → iso` and `traders → iso`. The `ftr → arr` (information) edge explains the formula's funding source.
- Retail bill: `customers → lses` (money). No ISO, no PUC in the cash path; the PUC sets the tariff via regulation, the LSE collects under it.
- Network upgrade: `generators → to` (money). Direct contract; no ISO in cash path.

### The ISO as operator, administrator, and central counterparty

The ISO has three distinct roles in the graph:

1. **Operator** — runs cleared markets, ARR allocation, and interconnection studies. Visible via regulation edges (`iso → dam`, `iso → rtm`, `iso → arr`, `iso → interconnection`, etc.).
2. **Administrator** — distributes prices, dispatch instructions, settlement statements; reads clearing outputs from each market for settlement. Visible via information edges (`dam → iso`, `iso → generators` info, etc.).
3. **Central counterparty** — collects from buyers and pays sellers across all centrally-cleared transactions, plus administers OATT collection and ARR distribution. Visible via money edges: `actor → iso` (LSEs/generators/traders paying for cleared positions) and `iso → actor` (ISO paying out cleared revenues, ARR cash, FTR settlements, OATT remittances).

The ISO money edges are intentionally bundled. A single `lses → iso` (money) edge carries the LSE's DAM share, RTM share, capacity share, AS uplift share, FTR auction buys, and OATT uplift — because the ISO settles them as one aggregate payment per settlement run. This matches how settlement statements actually arrive in practice: one statement per ISO, not per market.

Bilateral, retail, and direct construction sit outside the CCP role — these flow counterparty-to-counterparty without ISO in the path. That distinction — which transactions are centrally-cleared vs. not — is a real structural feature of the system.

## Design principles

### Compression rule

> Two nodes should be collapsed only when they share the same edge types to the same neighbors. If collapsing hides an edge (especially one between them, or to a distinct neighbor), they need to stay separate.

This is the rule that determines node granularity. It explains:

- Why DAM and RTM are separate nodes (the DAM→RTM seam is an information edge that disappears if you collapse them).
- Why ARR allocation is a separate node from the FTR auction (ARR has edges to LSEs and retail that the FTR auction doesn't).
- Why state PUCs and FERC are separate (different jurisdictions, different downstream edges).
- Why generators, LSEs, and traders are separate actor nodes (their edge sets to markets, regulators, and each other diverge enough that collapsing them hides structure — most visibly in the FTR/ARR loop and the bilateral layer).
- Why OATT and retail are separate nodes (different regulators, different payers, different recipients).
- Why thermal and renewable generators are *not* split at the top level (their edges to markets are structurally similar; only attributes differ).

### Tiered detail

The current graph is a *top-level* graph (20 nodes). Several nodes are candidates for expansion into sub-graphs at level 2:

- **Generators** → thermal, renewable, storage, hybrid, demand response (each with subtly different market eligibility and settlement rules)
- **LSEs** → vertically integrated utilities, competitive retailers, munis & co-ops (different regulatory exposure and procurement patterns)
- **Bilateral** → physical PPAs, tolling, bilateral RA, financial CFDs and basis swaps (different counterparty mixes and settlement structures)
- **DAM** → SCUC, RUC, virtual bidding, settlement (also the natural home for the OPF / LMP decomposition details — energy, losses, congestion as dual variables on the network constraints)
- **RTM** → SCED, ORDC and scarcity pricing, imbalance settlement
- **OATT** → transmission service, transmission revenue requirement, RMR (FERC-jurisdictional flavors)
- **End Customers** → residential, commercial, industrial, large flexible loads (data centers as a contested sub-category)
- **Transmission planning** → a *new* level-2 candidate. Order 1000 regional planning is structurally similar to interconnection (recurring multi-stakeholder process with cost allocation rules) but is currently folded into `to → ferc` action and `iso → to` information edges. Worth splitting out if transmission cost allocation grows in salience.
- **DR aggregator** → another level-2 candidate. Order 2222 mediation between customers and wholesale markets currently has no representation; the `customers → rtm` direct edge was removed as glossing this mediation.

Expansion is not currently implemented in the visualization but is the natural next feature.

## What's not in the graph

Deliberate omissions worth noting:

- **Adjacent markets** (RECs, RGGI, California cap-and-trade) are not currently represented. They could be added as additional market nodes; doing so would create regulation and money edges to LSEs, generators, and state regulators.
- **DER aggregators and DR providers** are not represented as distinct actor nodes. Order 2222 has begun to bring distribution-side resources into wholesale markets, but representing their structural role properly requires a distribution-level node (DSO/utility-as-DSO) which the current graph doesn't have.
- **Distribution-level operations** (DSO functions, distribution-level markets, retail-tariff DR programs beyond the wholesale interface) are mostly out of scope.
- **Inter-RTO seams** (PJM-MISO joint operating agreement, etc.) are not represented. These would be ISO-to-ISO information and coordination edges.
- **Storage and hybrid resources** are folded into generators but really have edge structure that differs from pure generators (they are both load and generation; they have charging-energy money flows TO the ISO).
- **Vertically integrated utility actors** in non-restructured regions are folded into generators and LSEs as appropriate, but in practice the same legal entity plays both roles plus owns transmission — a structural fact the current graph elides.
- **Market monitors / IMM** (Independent Market Monitor) are not separate actor nodes; their oversight role is currently rolled into FERC. If split out, they would have information edges to FERC and the ISO, and a quasi-regulatory edge to market participants.
- **Reliability operations** — TLRs, EEAs, operator emergency procedures, must-run for reliability, and other non-market levers the ISO uses for grid security are abstracted out. The framework focuses on market structure; the operational reliability layer is captured only through `iso → to` information (outage/dispatch coordination) and the ISO's role description. Modeling this layer properly would warrant a separate "operational" edge type or a sub-graph below the ISO.
- **LMP decomposition and the OPF dual structure** — the network model, binding constraints, and shadow prices that produce LMPs (energy + losses + congestion components) are abstracted into single information edges (`iso → dam` model in, `dam → iso` clearing out). This is Hogan's likely critique: the OPF and its duals are *the* mechanism by which nodal market design works. Listed as a level-2 candidate under DAM, but worth understanding the current graph treats the clearing engine as a black box.
- **Quantitative weights and edge magnitudes** — edges are typed but not weighted. A reader can see that `lses → iso` (money) exists but not how big it is relative to `customers → lses` (money) or `lses → bilateral` (money). Modeling magnitudes would require pulling in real data from ISO settlement reports and would let the graph support "follow the money" analysis at the scale level.
- **Cross-ISO variation as topology** — variation across PJM/MISO/ISO-NE/NYISO/CAISO/ERCOT lives in node descriptions and narrative prose (e.g., 4CP vs. 5CP for transmission allocation; ERCOT's energy-only design lacking a capacity market). The graph topology itself is one-size-fits-all. A future "graph diff" capability — viewing PJM-minus-ERCOT, for instance — would make the cross-ISO variation a first-class object.

These are candidates for expansion as the framework matures.
