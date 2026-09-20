---
title: KinetiRO Sim — a wastewater plant simulator whose arithmetic is published
date: '2026-09-20'
category: Process_Engineering
confidence: 0.98
tags: [Wastewater treatment, Process simulation, Process design, Activated sludge
    model (ASM3), Membrane filtration, Metcalf & Eddy, IWA, Transparency, Verification,
  Industrial software, Chemical engineering, Environmental engineering, Unit operations,
  'sector:wwtp', 'sector:activated-sludge', 'sector:membrane-extraction']
source: https://www.kinetiro.com/
type: Article
source_type: Article
hash: 71a6a3061104
---
## 🎯 Relevance
This tool is highly useful for process engineers in wastewater treatment for designing, simulating, and verifying plant performance. Its transparency (published arithmetic, verification record) significantly reduces the risk associated with 'black box' software, allowing engineers to confidently stamp designs. It offers a valuable learning opportunity for students and a practical resource for professionals to conduct sanity checks, explore operational scenarios, and assess proposals with auditable calculations. The free beta access lowers the barrier to entry for evaluation and adoption.

## 📖 Content
## Every calculation in KinetiRO Sim is traceable to a published source.

KinetiRO Sim is a wastewater plant designer and simulator that operates in a web browser. Its design equations are published and cited to their sources. KinetiRO sells no equipment and receives no payment from any equipment supplier.

Build the flowsheet, enter the water, calculate. Then look up where every number came from. The biology is ASM3, published as IWA Scientific and Technical Report No. 9. The clarifier, screen, filter and anaerobic sizing methods are Metcalf & Eddy, 5th edition, cited by equation number on the block that uses them. Membrane transport is solution–diffusion, marched element by element the way a projection program does it.

We checked our own code against those references and wrote down what we found. Twelve things were wrong. They are fixed, and the record of all of it is published, including three items recorded as worth completing and not yet completed.

**An account is required to design and calculate.** Exporting is part of a licence, and every beta account is licensed until 1 November 2026 — every export format and no cap on stored projects. No card.

## Basis for relying on the results

### The arithmetic is published, and so is the check

Every design equation, constant and quoted range in the tool was read against Metcalf & Eddy 5th edition and IWA STR No. 9. Twelve equations and twelve tables reproduce the references exactly. Twelve things were wrong: three moved real answers, three were inputs a user could type that the calculation then ignored, and the rest were citations that pointed at the wrong place while the values were right. All twelve are published with what changed.

[The verification record](https://www.kinetiro.com/sim/verification/)
### No supplier is favoured

The membrane library carries 19 named commercial elements from Hydranautics, LG Chem and Veolia side by side, plus a generic element and a fully user-defined one in each membrane block. Nothing ranks them, nothing defaults to a brand, and no supplier pays to be there — because we do not sell equipment and take nothing from anyone who does.

[What the tool models](https://www.kinetiro.com/sim/)
### The limits are documented

Sealed `.eaqua` files — encrypted deliverables — are still being built, and the page describing them already says what they will not protect against: a recipient able to open one can copy its contents, no scheme running on the reader's own computer prevents that, and KinetiRO does not claim otherwise. The limits are recorded in the source comments and published here for the same reason.

[What sealed files will do](https://www.kinetiro.com/sim/#sealed)

## Three readers, and where each should start

### An engineer sizing a plant, establishing what the software models

21 unit operations, ASM3 with thirteen components and twelve processes, an element-by-element membrane march tracking fourteen ions separately, and more than fifty design checks that compare the design against the ranges in the references. Solved at steady state, with the exclusions stated.

[What KinetiRO Sim does](https://www.kinetiro.com/sim/)
### An engineering manager assessing seats for a team

One plan for an engineer, one for a company. Both unlock exactly the same capability — the difference is who holds the licence and who administers the seats, and that is a fact about the code rather than a promise in the marketing. The price is not set yet; during the beta every account has full access.

[What each plan includes](https://www.kinetiro.com/pricing/)
### A reader assessing whether a figure produced by software they did not write can be relied upon

The verification record is more informative than the feature list. It publishes twelve defects the check identified in KinetiRO's own code, three items recorded as worth completing and not yet completed, and the worked figures for each.

[The verification record](https://www.kinetiro.com/sim/verification/)

## Why a published equation is worth more than a proprietary one

### Every value's source is available without leaving the panel

Each unit operation carries its own reference sheet: the design ranges it checks the design against, and the table or equation number they came from. Metcalf & Eddy by equation and page, IWA STR No. 9 for the activated sludge model. An engineer putting a stamp on a design needs to know the tool follows a reference they can open, not that it does something clever they cannot audit.

[How it calculates](https://www.kinetiro.com/sim/calculation/)
### The mass balances close because of how the stoichiometry is built, not because they were adjusted.

The ASM3 stoichiometry is derived from COD, nitrogen and charge conservation rather than typed in as a matrix of coefficients. A balance that closes by construction cannot be quietly wrong in the way a balance that closes by tuning can.

[How it calculates](https://www.kinetiro.com/sim/calculation/)
### When the check found something wrong, we published it rather than fixing it quietly.

A blower that took a discharge pressure and an efficiency and used neither. A dissolved-oxygen saturation curve that read 5.6% low at 40 °C and fed the aeration answer directly. A measured TKN the model read and threw away, which on the shipped example overstated influent nitrogen by 91%. All fixed, all written down, all still on the page.

[The verification record](https://www.kinetiro.com/sim/verification/)

## During the beta, every account has everything

Full access for the whole beta period: every unit operation, every design check, every reference sheet, ASM3, the membrane march and every export format — with no cap on stored projects. It is a complimentary licence rather than a trial, so nothing expires in a fortnight and no card is asked for.

What we are asking for in return is the thing a price cannot buy: tell us where it is wrong.

Afterwards there will be a free plan and there will be paid ones, and the line between them is already decided even though the price is not. A student checking a textbook problem, an operator asking what happens if the sludge age drops two days, an engineer sanity-checking somebody's proposal — none of them should pay us anything, and none of them will. A firm issuing a document it will be held to needs unlimited storage and an export it can put its name on. That is where the line is, and it is the honest place for it.

An account remains required. Announcing that condition at the outset was judged preferable to allowing anonymous design and presenting the restriction afterwards.

[What each plan includes](https://www.kinetiro.com/pricing/)

## Open it and try to break it

The most direct assessment is to model a plant whose performance is already known and compare the result. Where the two disagree, KinetiRO asks to be informed: send the project file and the figure expected. The defects the verification identified in KinetiRO's own code are already published, and an addition to that record is less costly than an undetected error.

An account is required. During the beta every account gets full access, and no card is asked for.

## 💡 Key Insights
- KinetiRO Sim is a web-based wastewater plant designer and simulator with all calculations traceable to published sources.
- The simulator utilizes established models like ASM3 (IWA STR No. 9) for biology and Metcalf & Eddy (5th edition) for unit operation sizing (clarifier, screen, filter, anaerobic).
- A rigorous verification process identified and publicly documented 12 defects in the software's code, demonstrating transparency and commitment to accuracy.
- The mass balances are constructed from fundamental conservation principles (COD, nitrogen, charge) rather than being adjusted, ensuring inherent correctness.
- The tool models 21 unit operations, ASM3 with 13 components and 12 processes, and element-by-element membrane transport tracking 14 ions.
- KinetiRO does not sell equipment or favor any supplier, offering an unbiased membrane library with commercial elements from various brands.
- During the beta period, all accounts receive full access to all features, export formats, and unlimited project storage without requiring payment, in exchange for user feedback.

## 📚 References
- KinetiRO Sim — a wastewater plant simulator whose arithmetic is published, KinetiRO, URL: https://www.kinetiro.com/ *(source)*
- Metcalf & Eddy, Wastewater Engineering: Treatment and Resource Recovery, 5th Edition *(cited)*
- IWA Scientific and Technical Report No. 9 (ASM3) *(cited)*
- Commercial membrane elements (Hydranautics, LG Chem, Veolia) *(cited)*

## 🏷️ Classification
The content describes a web-based simulator for designing and analyzing wastewater treatment plants, directly aligning with the 'Conception, simulation' aspects of Process_Engineering.
