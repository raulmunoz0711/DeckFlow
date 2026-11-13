# DeckFlow Consulting Proposal

**Prepared for:** Dan, Owner, Game Citi TCG  
**Prepared by:** CPSC 490 Group 5  
**Date:** November 13, 2026  
**Project:** DeckFlow Pokémon Card Pre-Grading and Market-Information Proof of Concept

## 1. Executive summary

Game Citi TCG regularly receives customers who want an opinion about a raw Pokémon card's condition and whether professional grading is worthwhile. Dan, the owner, estimates that the store receives about four to five grading-opinion requests each week. A typical visual inspection takes about five minutes and depends on experience with centering, corners, edges, whitening, scratches, print lines, creases, and surface condition. The financial consequence can be significant: Dan described a card worth about $50 raw that might sell for about $400 as a PSA 10 but only $50–$100 as a PSA 9. The business must make the grading decision before it knows the official result.

We recommend that Game Citi approve a limited DeckFlow pilot. DeckFlow is an AI-assisted decision-support application that accepts front and back card images, identifies a supported Pokémon card, reports visible condition findings, provides an experimental and confidence-aware grade estimate, and displays available market information. It is not an official grading service and will not replace PSA, CGC, TAG, Beckett, or Dan's judgment.

The immediate value is evidence: Game Citi can determine whether a repeatable scan-to-report workflow is trustworthy enough to support a future paid pre-grading service. Dan suggested a trial price of $10 per card. At the current four to five weekly inquiries, the unvalidated maximum revenue opportunity is approximately $40–$50 per week, or about $2,080–$2,600 per year, before labor and operating costs. This is a hypothesis, not a forecast, because customer willingness to pay has not been tested.

We ask Game Citi to approve a controlled proof-of-concept demonstration using supported sample cards, provide feedback on whether the findings are understandable and credible, and allow the team to compare results with professionally graded cards when available. Approval does not commit Game Citi to purchase or deploy the system.

## 2. The client's problem

Game Citi TCG is a trading-card store near Cal State Fullerton. Dan buys, evaluates, prices, and sells trading cards and advises customers about card condition and professional grading. Today, the work is primarily manual. For a card under consideration, an employee must identify the exact printing, inspect visible defects, research raw and graded values, consider grading and shipping costs, and decide whether submission is financially reasonable.

The workflow creates three costs:

1. **Time:** Dan estimates about five minutes for the visual inspection of one card. Whether this includes price research still needs to be measured.
2. **Decision risk:** A card expected to receive a 10 may return as a 9 or 8, sharply reducing the expected return after grading, shipping, and selling costs.
3. **Missed revenue:** Game Citi may pass on cards that could have been profitable to grade, or it may lack a consistent service it can charge customers for.

The need is current because customers already request this advice four to five times per week. Dan recently inspected a Mew card, found poor corners, surface condition, creases, and whitening, and advised the customer not to grade it. He also previously tested a free automated tool but stopped using it because its metrics and grade estimates were inconsistent with his own assessment. His primary concern is not whether a user interface can be built; it is whether the underlying result can be validated and trusted.

The exact annual cost of the current workflow is still missing. The team needs measured pricing-research time, labor cost, actual grading and shipping fees, the number of shop-owned cards considered for grading, and examples of realized losses or missed profits. This proposal therefore reports known activity and a revenue hypothesis without claiming unsupported savings.

## 3. Options considered

### Option A: Continue the manual workflow

This has no software purchase cost and preserves Dan's judgment. It also leaves the process dependent on one person's experience, repeated market research, and an uncertain grading decision. It does not create a standardized report or establish whether a paid assessment service can work.

### Option B: Buy or integrate existing products

Professional graders provide official grades but require shipping, fees, and turnaround time; they do not answer the pre-submission question. Marketplaces and card databases help identify cards and provide price information, while scanning or AI-grading tools attempt parts of the condition workflow. Dan has already tried one free tool and stopped using it because he did not trust its consistency. Existing products remain useful as data sources and benchmarks, but the team has not yet found one validated tool that combines the store's desired front/back capture, transparent condition findings, uncertainty, exact-card market information, and local decision workflow.

The competitive research is incomplete. Vendor-by-vendor prices, claimed accuracy, licensing terms, and integration costs still need sourced comparison before a production purchase decision.

### Option C: Build and evaluate DeckFlow

Building a limited proof of concept lets Game Citi test the highest-risk assumption before paying for a full system: whether ordinary images can produce consistent, transparent, and useful condition evidence. It also lets the workflow use legitimate card-catalog and market-data integrations while presenting uncertainty instead of inventing an answer.

We recommend Option C for a limited evaluation, not an immediate production deployment. It produces client-specific evidence and preserves the option to integrate or purchase an existing service later if that proves more reliable or economical.

## 4. Proposed solution

### Objectives and success measures

The CPSC 490 proof of concept will demonstrate one complete scan-to-report workflow. The intended checks are:

- A supported card can be captured from the front and back.
- The correct printing appears among the identification candidates for the prepared demo cards.
- A visibly damaged prepared card receives a worse condition result than a clean prepared card under the same capture setup.
- Repeating the same prepared input produces the same result.
- A report is produced within 30 seconds for at least 90% of valid prepared demo attempts.
- Poor or incomplete images produce a retake or uncertainty message instead of a confident grade.
- Market information is shown only when it is available for the confirmed card printing.

The PRD's longer-term targets of 90% identification accuracy, 85% of grade estimates within one grade of a professional result, and 95% repeatability are not yet proven. They require a larger labeled evaluation set and belong to future validation, not a claim about the current PoC.

### What the PoC will build

1. A browser-based card-assessment flow that accepts front and back images from the laptop or phone-upload session.
2. Image preparation that crops and orients the card and rejects unusable inputs.
3. Card identification using OCR and the TCGdex catalog, with a candidate-confirmation fallback.
4. An experimental condition estimate based on visible centering, edge, corner, surface, and image-quality cues.
5. Available raw market information for the confirmed printing and a clearly labeled rough graded-value model when the required inputs exist.
6. A result report that shows card identity, findings, estimate, confidence or warnings, and price-source information.
7. A Docker-based demonstration that can run on a clean MacBook.

### How it works

The employee captures the card's front and back. The backend validates and prepares the images, identifies likely card records, and asks the user to confirm a candidate when confidence is insufficient. The condition component measures visible features and produces an experimental estimate with reasons and warnings. The pricing component retrieves available data for the confirmed catalog record. The interface combines the results into one report.

### Out of scope

- Official grading, authentication, counterfeit detection, or a guarantee of a PSA/CGC/TAG/Beckett result
- Automatic submission to a grading company or automatic sale of a card
- Support for every trading-card game, every Pokémon printing, or every language in the PoC
- A production payment system, customer accounts, inventory system, or permanent storage of customer images
- A production-grade selling-window prediction when reliable historical data is unavailable
- Claims of financial return that have not been measured with Game Citi

## 5. Evidence so far

The PoC has shown that the team can run a browser application through Docker, accept card images, maintain a local TCGdex catalog, display identification candidates, retrieve some market information, and generate an experimental report. A phone QR upload session and repeated uploads have also been demonstrated during development.

The negative results are more important than the interface progress:

- Early grading output behaved like a placeholder and repeatedly showed the same value.
- A damaged card once scored better than a cleaner card, showing that the grading logic was not calibrated.
- Card images were sometimes cropped incorrectly, rotated, or mirrored.
- Automatic identification sometimes selected the wrong Pokémon or wrong printing.
- Pricing was absent or attached to the wrong candidate in some runs.
- Docker caching and old local folders made updates appear missing.
- The current system has not been evaluated against a statistically meaningful set of professionally graded cards.

These results mean the team has demonstrated integration feasibility but has not demonstrated professional grading accuracy. The live demo will present the system as an experimental decision-support PoC and will show failure handling rather than hide uncertainty.

Dan confirmed that a scan-to-report workflow would be a reasonable minimum. He values consistency, visible defect findings, uncertainty, and comparison with professionally graded cards. He would consider a $10-per-card assessment trial, but customer willingness to pay remains untested. His strongest objection is that he has not seen automated grading software convincing enough to trust and sell.

## 6. Value and cost

At four to five customer inquiries per week and Dan's suggested $10 trial price, DeckFlow's initial gross-revenue hypothesis is $40–$50 per week. If the rate continued for 52 weeks, that would be approximately $2,080–$2,600 in annual gross revenue before labor, taxes, payment fees, software costs, and equipment. The team should not present this range as guaranteed revenue.

There may also be value from avoiding poor grading submissions and identifying profitable opportunities, but the team does not yet have enough client data to assign a dollar amount. A single card can have a large value difference between a PSA 9 and PSA 10, yet this does not prove that DeckFlow can predict that difference reliably.

The CPSC 490 PoC has no software-development charge to Game Citi. Expected operating costs for a pilot include employee time, ordinary phone or laptop equipment, hosting if the system moves beyond local Docker, and any paid market-data or model service. The exact production cost is missing because hosting, data licensing, retention, and support requirements have not been selected.

A future 30-day pilot should measure paid assessments, gross revenue, employee minutes per assessment, incremental operating cost, error/retake rate, and net contribution. Game Citi should continue only if the measured benefit exceeds operating cost and Dan considers the reports trustworthy.

## 7. Risks and responsible use

| Risk | Impact | Handling |
|---|---|---|
| Inaccurate grade estimate | A poor grading or pricing decision could lose money. | Label all estimates unofficial, show reasons and uncertainty, request human confirmation, and prevent use as an official appraisal. |
| Insufficient labeled data | Accuracy claims cannot be validated. | Limit the scope, build a controlled evaluation set, record model/rules versions, and report negative results. |
| Poor image quality | Glare, sleeves, angle, blur, or shadows can hide defects. | Validate both images, provide a card-shaped guide, detect failed crops, and request a retake. |
| Wrong card or variant | The displayed market value may be incorrect. | Present ranked candidates and require confirmation when confidence is low; key prices by exact catalog ID and language. |
| Missing or stale market data | The user may rely on an outdated or invented price. | Display source, variant, currency, and availability; cache responsibly; never invent a price. |
| Privacy and retention | Card or customer images could be retained unnecessarily. | Do not require personal information for the PoC, use temporary upload sessions, restrict access, and define deletion before a pilot. |
| Security | Upload endpoints and stored data may be abused. | Validate file types and sizes, use random session identifiers, restrict origins and access, avoid exposing API keys, and log errors without sensitive images. |
| Licensing and terms | Catalog images, pricing data, or training images may not permit reuse. | Use documented APIs, retain source attribution, review terms before production, and do not scrape restricted marketplaces. |
| Automation bias | Employees may treat a confident-looking result as fact. | Keep Dan or an employee as the decision maker and show limitations beside the result. |
| Financial interpretation | A modeled graded value could be mistaken for a verified sale. | Label modeled values clearly and separate them from observed raw-market quotes. |

## 8. Plan and team

### CPSC 490 milestones

| Milestone | Result |
|---|---|
| November 13 | Complete proposal draft on `main` and reviewable GitHub issues for the PoC |
| November 20 | Working PoC evidence, test results, and updated issue status |
| November 30 | Live demo and documented client reaction |
| December 4 | Final proposal and revised CPSC 491 recommendation based on evidence |
| December 7 | Readiness review and rehearsal |

### Team ownership

- **Raul Munoz, Team Lead:** schedule, integration, Docker demo readiness, and final merge to `main`.
- **Jovanny Reyes, Client Lead:** client communication, demo feedback, and business-value evidence.
- **Isaac Parada, Technical Lead:** backend integration, image processing, identification, condition-estimate tests, and technical evidence.
- **Anthony Jimenez, Writing Lead:** proposal coordination, source review, issue/document consistency, and final proofreading.

The GitHub issues are the detailed CPSC 490 work plan. Each issue identifies one result, owner, acceptance criteria, test, and failure cases. Work counts as done only when every acceptance item has evidence attached to the issue or linked pull request. Work that cannot be completed or validated in 490 will be reported as a finding, not silently moved into the PoC definition of done.

## 9. Sources and authorship

### Project sources

- [Product Requirements Document](prd.md)
- [System Design](design.md)
- [Competitive Brief](competitive_brief.md)
- [Domain and Decision Memo](memo.md)
- [Client Discovery Interview](ClientConversation.md)
- [Project Brief and Open Questions](brief.md)
- Game Citi TCG website: <https://www.gamecititcg.com/>

The proposal uses client figures only when they appear in the interview notes. The $2,080–$2,600 annual range is an arithmetic scenario based on four to five weekly inquiries at $10 each; it is not a validated forecast. External market-size, vendor-price, professional-grading-fee, and marketplace-fee claims require source verification before the final proposal.

### Authorship and AI use

- **Executive summary and value/cost:** proposed owner is Jovanny Reyes, with Raul Munoz review.
- **Client problem and evidence:** proposed owner is Jovanny Reyes.
- **Options and competitive discussion:** proposed owner is Anthony Jimenez.
- **Solution, risks, and technical plan:** proposed owner is Isaac Parada.
- **Final integration and approval request:** proposed owner is Raul Munoz.

The team must confirm these assignments and replace this note with the final authorship record. AI tools were used to organize existing repository evidence, convert requirements into an initial proposal structure, and edit wording. Team members remain responsible for checking every claim, source, calculation, acceptance criterion, and technical statement. AI-generated text is not treated as client evidence and no unsupported metric is presented as fact.
