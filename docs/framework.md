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
  - **Bilateral / OTC is a market node.** Earlier versions of the graph treated bilateral contracts as direct actor-to-actor edges, on the reasoning that they don't clear centrally. The current view is that they belong on the liquidity gradient between cleared auctions and administrative rates: PPAs, tolling, bilateral RA, and financial CFDs are recurring arrangements with standardized settlement references (DAM LMPs as the energy benchmark) even though no single counterparty clears them. Without a `bilateral` node, the link between capacity revenues and PPA willingness-to-pay — the missing-money story — has nowhere to live except as prose in an edge description. PPA settlement money still flows actor-to-actor (`lses → generators`), per the money-edge rule below.
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

### The ISO as central counterparty

In this framework, the ISO is the financial counterparty for all centrally-cleared market transactions. Generators don't get paid by "the DAM"; they get paid by the ISO, which collected from load. This is why the largest money flows in the graph run through the ISO — `lses → iso` and `traders → iso` (buyers paying) and `iso → generators`, `iso → lses`, `iso → traders`, `iso → to` (sellers and TOs being paid). Markets connect to the ISO via information edges (clearing results flow to the ISO for settlement) rather than money edges.

Bilateral PPAs (`lses → generators` money) and customer-to-LSE flows (`customers → lses` money) bypass the ISO, since the ISO isn't the counterparty there. Interconnection network upgrades (`generators → to` money) likewise flow directly. This asymmetry — which transactions flow through the ISO vs. directly — is a real structural feature of the system.

### Money edges are actor-to-actor only

A money edge represents value transferred between two balance sheets. A market is a price-and-quantity discovery mechanism, not a balance sheet — DAM doesn't hold money; the ISO does. So money edges in this graph always have an *actor* on each end. A market's role in determining how much money moves is captured by an information edge (clearing produces a price) or a regulation edge (a tariff sets a charge).

This rule eliminates the temptation to draw `dam → ftr` (money) or `lses → oatt` (money). Both collapse into the cleaner pattern: `iso` is the counterparty, the market node carries the price signal via information, and the tariff governs via regulation. Where a flow appears to pass through a market (FTR auction revenue funding ARR distributions, for instance), the actual money lives in the ISO settlement system and the market-to-market edge becomes information (`ftr → arr` information: "FTR auction revenue is the funding source for ARR distributions").

### What mechanism nodes carry

If money never flows through a mechanism node, what is it doing in the graph? A reasonable question — and the first one a reader asks when they see, say, `lses → generators` (money) bypassing the `bilateral` node. The answer: mechanism nodes anchor the *information* and *action* relationships that explain why money has the structure it does. Removing a mechanism node doesn't collapse a money flow; it scatters the explanation of that money flow across multiple actor-actor edges that would have to carry the content in their descriptions.

Concretely, for each mechanism node:

- **`dam`, `rtm`, `as`, `capacity`, `ftr`** — produce clearing prices and clear participation. The price-production is one or more information edges (e.g., `dam → bilateral`, `dam → ftr`); the participation is action edges (e.g., `generators → dam`). Without the node, every price-reference relationship would have to be a direct actor-to-actor information edge.
- **`bilateral`** — collects OTC participation from four distinct actor types (gens, lses, traders, large customers). Anchors the DAM LMP reference (`dam → bilateral`) and the capacity revenue WTP signal (`capacity → bilateral`). Money flows directly between counterparties (`lses → generators` for PPAs), but the *structure* of those contracts is determined here.
- **`oatt`, `retail`** — administrative tariffs. No clearing, no actor action edges, very lightweight. But they anchor jurisdictional distinctions (FERC-set vs. PUC-set) and pricing-method content (4CP, 5CP, NSPL allocation methods for OATT; passthrough formulas for retail) that would otherwise have to live in regulation edge descriptions.
- **`interconnection`** — hosts the queue process. Multiple actor actions converge here (`generators → interconnection`, `to → interconnection`), and outputs feed the ISO's resource model (`interconnection → iso`).
- **`arr`** — hosts the LSE nomination action and the multi-source allocation formula (RTM load + OATT cost allocation + FTR auction revenue all feed in as information edges).

The general pattern: **a mechanism node earns its keep when collapsing it would require spreading its content across multiple new pairwise edges**. By that test, all current mechanism nodes are justified. The `oatt` and `retail` tariff nodes have only 3 incident edges each — low connectivity is structural, not redundancy.

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
