# Framework

This document describes the framework underlying the graph: the node typology, edge typology, and design principles. It also captures the reasoning where useful.

## Object

The framework treats the U.S. electricity market as a **typed multigraph**. Nodes have one of two types (actor, market). Directed adges have one of four types (action, money, regulation, information). Multiple edges of different types are allowed between the same pair of nodes — in fact, a lot of structure lives in this space.

The graph is the *reference object*. Specific topics (FTR design, capacity adequacy, large-load policy, DCOPF approximation gaps) are *subgraphs* of it.

## Nodes

### Two types

- **Actor** — an institutional entity that makes decisions. Currently: ISO/RTO, transmission owner, **generators** (physical suppliers: gen firms, IPPs, storage, hybrid), **LSEs** (load-serving entities: utilities, retailers, munis, co-ops), **financial traders** (virtual bidders, FTR-only traders, marketers without physical assets), end customers, FERC, state PUCs, NERC, state legislatures.
- **Market** — a recurring or standing arrangement where transactions clear. Markets span a *liquidity gradient*:
  - **Centrally-cleared ISO auctions:** FTR, DAM, AS, RTM, capacity
  - **Administratively assigned:** ARR allocation (a formula, not an auction)
  - **Administratively set:** retail tariffs, OATT, transmission revenue requirement, RMR contracts (collapsed into one `rates` node at the top level)

- **Notes on this decision**
  - **Generators / LSEs / traders are split because they have genuinely different edge profiles.** Generators are the only actors with interconnection, NERC GO/GOP, capacity supply, and AS supply edges. LSEs are the only ones with ARR nomination, retail-customer money inflows, PUC regulation, and RPS obligations. Traders have only DAM/RTM/FTR financial positions — no interconnection, no NERC, no capacity, no retail. Collapsing them hides edges the framework needs to express.
  - **Bilateral / OTC is not a market node.** PPAs, tolling, OTC swaps could be modeled as a clearing arrangement, but they don't clear in the ISO sense (no central counterparty, no auction). Each contract is a direct actor-to-actor relationship. They are represented as direct edges — `lses → generators` (money) for PPA settlement and `generators → lses` (action) for negotiation. DAM LMPs as the settlement reference and capacity revenues as a WTP driver are folded into those edge descriptions.
  - **Regulatory constructs collapse into edges.** A FERC order is an action by FERC that modifies the rules governing some market or actor. NERC standards are constraints NERC imposes on ISOs, TOs, and generators. State RPS policies are obligations legislatures impose on LSEs. In every case, the "construct" is really *an actor exercising authority over another node*, which is exactly what a regulation edge is. Treating them as edges rather than nodes simplifies the graph without losing any structure.
  - **Physical objects collapse into actor/market attributes.** Generators-as-firms are actors; generators-as-physical-equipment are an attribute of those actors. Lines and loads are attributes of TOs and customers respectively. The "physical reality" of the grid enters the graph through information edges (the ISO supplies a network model to DAM) and action edges (a TO operates a line). For a framework focused on market structure, this is sufficient — the physical layer is presupposed rather than represented.

## Edges

### Four types
- **Action** — an actor doing something. Examples: a generator submitting an offer into DAM, an LSE filing a rate case, FERC issuing an order, a customer paying a bill, a TO conducting an interconnection study.
- **Money** — value flowing between nodes. Examples: load paying the ISO for cleared DAM energy, the ISO paying generators from collected revenues, customers paying retail bills, OATT collections flowing to TOs, FTR auction revenues funding ARR distributions.
- **Regulation** — rules constraining behavior or determining how money amounts are set. Examples: FERC approving the ISO tariff, NERC reliability standards binding the ISO, state PUCs setting retail rates, must-offer obligations from the capacity market constraining DAM bidding.
- **Information** — data, models, forecasts, prices, telemetry flowing between nodes. Examples: the ISO supplying a network model to DAM clearing, RTM clearing results flowing back to the ISO for settlement, DAM LMPs being the reference price PPAs settle against, historical load data feeding the ARR allocation formula.

### Edges can exist between any pair of node types

Actor-actor edges: FERC regulates ISO; FERC oversees NERC; PUCs approve LSE tariffs; LSEs procure PPAs from generators.

Market-market edges: DAM positions are the financial baseline RTM settles against; DAM congestion rents fund FTR settlement; capacity must-offer obligations constrain DAM bidding.

Actor-market edges: the canonical ones — generators offering into DAM, LSEs bidding demand, traders taking financial positions, all being regulated by tariffs.

### The ISO as central counterparty

In this framework, the ISO is the financial counterparty for all centrally-cleared market transactions. Generators don't get paid by "the DAM"; they get paid by the ISO, which collected from load. This is why the largest money flows in the graph run through the ISO — `lses → iso` and `traders → iso` (buyers paying) and `iso → generators`, `iso → lses`, `iso → traders` (sellers being paid). Markets connect to the ISO via information edges (clearing results flow to the ISO for settlement) rather than money edges.

Bilateral PPAs (`lses → generators` money) and customer-to-LSE flows (`customers → lses` money) bypass the ISO, since the ISO isn't the counterparty there. This asymmetry — which transactions flow through the ISO vs. directly — is a real structural feature of the system.

## Design principles

### Compression rule

> Two nodes should be collapsed only when they share the same edge types to the same neighbors. If collapsing hides an edge (especially one between them, or to a distinct neighbor), they need to stay separate.

This is the rule that determines node granularity. It explains:

- Why DAM and RTM are separate nodes (the DAM→RTM seam is an information edge that disappears if you collapse them).
- Why ARR allocation is a separate node from the FTR auction (ARR has edges to LSEs and retail tariffs that the FTR auction doesn't).
- Why state PUCs and FERC are separate (different jurisdictions, different downstream edges).
- Why generators, LSEs, and traders are separate actor nodes (their edge sets to markets, regulators, and each other diverge enough that collapsing them hides structure — most visibly in the FTR/ARR loop and the bilateral layer).
- Why thermal and renewable generators are *not* split at the top level (their edges to markets are structurally similar; only attributes differ).

### Tiered detail

The current graph is a *top-level* graph (18 nodes). Several nodes are candidates for expansion into sub-graphs at level 2:

- **Generators** → thermal, renewable, storage, hybrid, demand response (each with subtly different market eligibility and settlement rules)
- **LSEs** → vertically integrated utilities, competitive retailers, munis & co-ops (different regulatory exposure and procurement patterns)
- **Regulated Rates** → retail tariffs, OATT, transmission revenue requirement, RMR contracts
- **DAM** → SCUC, RUC, virtual bidding, settlement
- **End Customers** → residential, commercial, industrial, large flexible loads (data centers as a contested sub-category)

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
