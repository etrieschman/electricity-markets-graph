# Framework

This document describes the framework underlying the graph: the node typology, edge typology, and design principles. It also captures the reasoning behind specific design choices, since several of them are non-obvious and might otherwise invite well-meaning but wrong revisions.

## Object

The framework treats the U.S. electricity market as a **typed multigraph**. Nodes have one of two types (actor, market). Edges have one of four types (action, money, regulation, information). Multiple edges of different types are allowed between the same pair of nodes — in fact, this is where most of the interesting structure lives.

The graph is the *reference object*. Specific topics (FTR design, capacity adequacy, large-load policy, DCOPF approximation gaps) are *subgraphs* of it.

## Nodes

### Two types

- **Actor** — an institutional entity that makes decisions: ISO/RTO, transmission owner, market participants, end customers, FERC, state PUCs, NERC, state legislatures.
- **Market** — a recurring or standing arrangement where transactions clear. Markets span a *liquidity gradient*:
  - **Centrally-cleared ISO auctions:** DAM, RTM, AS, capacity, FTR
  - **Administratively assigned:** ARR allocation (a formula, not an auction)
  - **Bilateral/OTC:** PPAs, tolling, swaps, futures, interconnection agreements (collapsed into one node at the top level)
  - **Administratively set:** retail tariffs, OATT, transmission revenue requirement, RMR contracts (collapsed into one node at the top level)

### Why these two types and not more

Earlier iterations of the framework included a third type — **physical objects** (generators, transmission lines, loads) — and a fourth — **regulatory constructs** (FERC orders, NERC standards). Both were tested and removed:

- **Regulatory constructs collapse into edges.** A FERC order is an action by FERC that modifies the rules governing some market or actor. NERC standards are constraints NERC imposes on ISOs and TOs. State RPS policies are obligations legislatures impose on LSEs. In every case, the "construct" is really *an actor exercising authority over another node*, which is exactly what a regulation edge is. Treating them as edges rather than nodes simplifies the graph without losing any structure.

- **Physical objects collapse into actor/market attributes.** Generators, lines, and loads exist in the world, but in the graph they participate *via* an actor (the generator firm bidding into DAM) or *via* a market (the network model the ISO supplies as an input to clearing). The "physical reality" of the grid enters the graph through information edges (the ISO supplies a network model to DAM) and action edges (a TO operates a line). For a framework focused on market structure, this is sufficient — the physical layer is presupposed rather than represented.

This collapse was contested in early iterations and is worth flagging for future contributors. The argument for re-introducing a physical layer would be that some research questions are awkward to state without it (inertia loss, AC infeasibility, dynamic phenomena outside any market model). The argument against is that the same questions can be stated as information edges (the ISO's network model failing to represent some physical phenomenon) without adding a node category. We chose the simpler framework on the principle that any category should earn its keep with concrete edge cases that need it.

## Edges

### Four types

- **Action** — an actor doing something. Examples: a generator submitting an offer into DAM, an LSE filing a rate case, FERC issuing an order, a customer paying a bill, a TO conducting an interconnection study.
- **Money** — value flowing between nodes. Examples: load paying the ISO for cleared DAM energy, the ISO paying generators from collected revenues, customers paying retail bills, OATT collections flowing to TOs, FTR auction revenues funding ARR distributions.
- **Regulation** — rules constraining behavior or determining how money amounts are set. Examples: FERC approving the ISO tariff, NERC reliability standards binding the ISO, state PUCs setting retail rates, must-offer obligations from the capacity market constraining DAM bidding.
- **Information** — data, models, forecasts, prices, telemetry flowing between nodes. Examples: the ISO supplying a network model to DAM clearing, RTM clearing results flowing back to the ISO for settlement, DAM LMPs being the reference price PPAs settle against, historical load data feeding the ARR allocation formula.

### Why these four and not more or fewer

Earlier iterations had six edge types (adding "physical" and "cost recovery" as separate categories) and five (separating "participation" from other actions). Both were stress-tested and collapsed:

- **Physical operation** is a special case of action (a generator dispatching energy is doing something) or information (telemetry flowing to the ISO). It doesn't need its own type.
- **Cost recovery** is a special case of money flow. The distinction earlier iterations tried to draw (between market-cleared payments and tariff-allocated payments) is really an attribute of the regulation edge governing the money flow, not of the flow itself.
- **Participation** is a special case of action (submitting a bid is an action). The temptation to separate participation from physical action is real but doesn't add expressive power.

The current four types are the minimum needed to express the framework without losing structure under stress tests. They were arrived at by progressive collapse.

### Edges can exist between any pair of node types

Actor-actor edges: FERC regulates ISO; market monitors report to FERC; PUCs approve LSE tariffs.

Market-market edges: DAM positions are the financial baseline RTM settles against; capacity market clearing prices affect PPA willingness-to-pay.

Actor-market edges: the canonical ones — participants bidding into markets, settling through markets, being regulated by tariffs.

### The ISO as central counterparty

A subtle point worth highlighting: in this framework, the ISO is the financial counterparty for all centrally-cleared market transactions. Generators don't get paid by "the DAM"; they get paid by the ISO, which collected from load. This is why the two largest money edges in the graph are `participants → iso` (buyers paying) and `iso → participants` (sellers being paid), with markets connected to the ISO via information edges (clearing results flow to the ISO for settlement) rather than money edges.

Bilateral contracts and customer-to-LSE flows bypass the ISO, since the ISO isn't the counterparty there. This asymmetry — which transactions flow through the ISO vs. directly — is a real structural feature of the system.

## Design principles

### Compression rule

> Two nodes should be collapsed only when they share the same edge types to the same neighbors. If collapsing hides an edge (especially one between them, or to a distinct neighbor), they need to stay separate.

This is the rule that determines node granularity. It explains:

- Why DAM and RTM are separate nodes (the DAM→RTM seam is an information edge that disappears if you collapse them).
- Why ARR allocation is a separate node from the FTR auction (ARR has edges to LSEs and retail tariffs that the FTR auction doesn't).
- Why state PUCs and FERC are separate (different jurisdictions, different downstream edges).
- Why thermal and renewable generators are collapsed into "market participants" at the top level (their edges to markets are structurally similar; only attributes differ).

The rule is also a *research lens*: places where two things are "almost the same but with subtly different edges" are exactly where definitional fights happen (is a data center load? is BTM solar a generator? is a virtual bidder a market participant in the same sense as a physical generator?). The framework provides a precise way to ask these questions.

### Tiered detail

The current graph is a *top-level* graph (~17 nodes). Several nodes are intended to expand into sub-graphs at level 2:

- **Market Participants** → generator firms, LSEs, IPPs, financial traders, marketers, DER aggregators, DR providers
- **Bilateral / OTC** → PPAs, tolling, bilateral RA, OTC swaps, exchange-traded futures, interconnection agreements
- **Regulated Rates** → retail tariffs, OATT, transmission revenue requirement, RMR contracts
- **DAM** → SCUC, RUC, virtual bidding, settlement
- **End Customers** → residential, commercial, industrial, large flexible loads (data centers as a contested sub-category)

Expansion is not currently implemented in the visualization but is the natural next feature.

## Provenance

The framework was developed iteratively in conversation, starting from an attempt to organize topics for a reading group on electricity markets. The progression was:

1. Topic-based organization (financial contracts / market operations / resource adequacy / regulated entities) → abandoned because the categories mixed timescale, product type, and actor type.
2. Matrix of timescale × stakeholder → abandoned because cells are unevenly populated and the interesting content lives on the edges between cells.
3. Relational graph with multiple node types (physical, actor, market, optimization, price, contract, regulation) → progressively compressed by stress-testing each category against concrete cases (ARR allocation, DCOPF/ACOPF gap, storage as load-and-generation, large flexible loads).
4. Current framework: two node types, four edge types, governed by the compression rule.

The compression rule itself was articulated late in the process, when it became clear that "this collapse is too much" and "this collapse is fine" were not arbitrary judgments but followed a principle.

## What's not in the graph

Deliberate omissions worth noting:

- **Adjacent markets** (RECs, RGGI, California cap-and-trade) are not currently represented. They could be added as additional market nodes; doing so would create regulation and money edges to participants and state regulators.
- **DERs and distribution-level operations** are mostly out of scope. Order 2222 starts to bridge this, but distribution-level markets and aggregation are not yet first-class nodes.
- **Inter-RTO seams** (PJM-MISO joint operating agreement, etc.) are not represented. These would be ISO-to-ISO information and coordination edges.
- **Storage and hybrid resources** are folded into market participants but really require their own treatment because their edge structure differs (they are both load and generation).
- **Vertically integrated utilities** in non-restructured regions are folded into market participants for simplicity but really play multiple structural roles.

These are candidates for expansion as the framework matures.
