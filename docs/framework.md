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

### Money edges flow through mechanism nodes

Every wholesale transaction has a *mechanism* that mediates it — a market that clears it, a tariff that sets its amount, or a process that administers it. Money edges in this graph follow that mediation: rather than drawing money directly actor-to-actor with the mechanism as a side-note, the money path is `buyer → mechanism → seller`.

Examples:

- DAM cleared energy: `lses → dam` (money) and `dam → generators` (money). The LSE pays the DAM, the DAM pays the generator.
- Bilateral PPA: `lses → bilateral` (money) and `bilateral → generators` (money).
- Retail bill: `customers → retail` (money) and `retail → lses` (money).
- OATT transmission service: `lses → oatt` (money), `oatt → to` (money).
- ARR cash distribution: `ftr → arr` (money), `arr → lses` (money).
- Network upgrade construction: `generators → interconnection` (money), `interconnection → to` (money).

The earlier graph drew these as actor-to-actor edges with the ISO sitting in the middle of cleared markets (`lses → iso → generators` for DAM, etc.). That actor-to-actor model was a defensible abstraction of the cash-flow accounting reality — the ISO does literally hold settlement cash temporarily — but it created two problems. First, it made some mechanism nodes (bilateral most visibly, but also OATT and retail) look decorative: money bypassed them entirely, and the node's role had to be reconstructed from info and action edges. Second, it was inconsistent — markets weren't really in the money path at all, so why call them markets? The current model resolves both: the mechanism is the conceptual counterparty, and what makes a node a market (or a tariff, or a process) is that money runs through it.

### The ISO as operator and administrator

Under the money-through-mechanisms rule, the ISO has *zero* direct money edges in the graph. It operates the markets (regulation edges: `iso → dam`, `iso → rtm`, etc.) and administers settlement (information edges: `dam → iso`, `oatt → iso` and ISO publishes prices, dispatch, settlement statements to participants). The ISO's role is captured at the operator-and-administrator layer rather than the money-flow layer.

This is an abstraction: in literal accounting reality, the ISO is the legal central counterparty for cleared markets and holds settlement cash. The graph model abstracts this by treating each market as the conceptual venue where the transaction clears, with the ISO operating the market rather than being the counterparty for it. Lay readers think this way already ("the LSE buys from DAM"); the graph now matches that intuition without losing the structural fact of ISO operation, which lives in the regulation and information edges.

Bilateral PPAs work the same way — `lses → bilateral → generators` (money), with no central counterparty implied. The bilateral node represents the OTC layer as a *venue*; conventions like DAM LMP settlement reference and ISDA-style master agreements are the standardization that makes it a market even without a central clearer.

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

These are candidates for expansion as the framework matures.
