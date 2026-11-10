# DeckFlow Issues and Development Backlog

**CPSC 490 Fall 2026 \| Proof of Concept Review \| Group 5**

This document records the main issues encountered while building and demonstrating DeckFlow, an AI-assisted Pokemon card pre-grading and pricing proof of concept. Each issue connects the problem to the project requirements and design, defines its limits, states testable acceptance checks, names completion evidence, and assigns a plan. Resolved issues remain included because they provide PoC evidence and identify regression checks for the CPSC 491 implementation.

# Backlog Summary

| **ID** | **Issue**                                                       | **Status**                              | **Priority** | **Target**                        |
|--------|-----------------------------------------------------------------|-----------------------------------------|--------------|-----------------------------------|
| DF-01  | Improve automatic card identification accuracy                  | Open for 491                            | Critical     | November 30, continue in CPSC 491 |
| DF-02  | Crop and orient the card before analysis                        | Partially resolved                      | Critical     | November 20                       |
| DF-03  | Calibrate the experimental condition grade                      | Open for 491                            | Critical     | CPSC 491 model milestone          |
| DF-04  | Show a rough graded value when raw pricing exists               | Resolved in PoC                         | High         | November 20                       |
| DF-05  | Return the correct raw market price and variant                 | In progress                             | High         | November 30                       |
| DF-06  | Keep the phone QR upload session available                      | Resolved in PoC, monitor                | High         | November 20                       |
| DF-07  | Start the catalog automatically on a clean computer             | Resolved in PoC, regression test needed | High         | November 20                       |
| DF-08  | Prevent stale containers and browser assets from hiding updates | Resolved development workflow           | Medium       | November 20                       |
| DF-09  | Keep one clear grading workflow in the interface                | Resolved in PoC                         | Medium       | November 20                       |

# Issue Details

## DF-01 Improve automatic card identification accuracy

| **Status**   | Open for 491                                | **Owner**    | Isaac Parada, Technical Lead                       |
|--------------|---------------------------------------------|--------------|----------------------------------------------------|
| **Priority** | Critical                                    | **Effort**   | Large, 3-5 weeks                                   |
| **Target**   | November 30 live demo, continue in CPSC 491 | **Blocking** | A reliable labeled image set and evaluation method |

**Source and result** [Docs/prd.md](Docs/prd.md), card identification requirement; [Docs/design.md](Docs/design.md), OCR and TCGdex catalog matching. The required result is a ranked list that places the exact card printing first or clearly asks the user to confirm a candidate.

**Observed issue** Observed problem: uploaded cards were sometimes labeled as the wrong Pokemon or wrong printing. We added the local TCGdex catalog and candidate list, but unrestricted automatic identification remains experimental.

**Scope** Improve identification from the front image using OCR text, card number, set name, and image similarity. Keep the candidate-selection fallback. This issue does not promise perfect recognition of every Pokemon card or authentication of counterfeit cards.

**Acceptance checks**

- Given the three prepared demo cards under recommended lighting, the correct printing appears in the first three candidates for all three cards.

- When OCR confidence is low, DeckFlow does not silently claim an exact match and instead displays multiple candidates.

- Selecting a candidate updates the card name, set, number, image, and price without hiding the remaining candidates.

- Japanese and English catalog entries do not overwrite one another when card numbers are similar.

**Completion evidence** A repeatable test sheet containing card images, expected TCGdex IDs, candidate ranks, and screenshots of the selected result. The reviewed pull request must include the test output and a client or instructor check during the live demo.

**Uncertainty** OCR quality varies by lighting, artwork, set symbols, language, and card condition.

## DF-02 Crop and orient the card before analysis

| **Status**   | Partially resolved       | **Owner**    | Isaac Parada, Technical Lead                                       |
|--------------|--------------------------|--------------|--------------------------------------------------------------------|
| **Priority** | Critical                 | **Effort**   | Medium, 1-2 weeks                                                  |
| **Target**   | November 20 PoC evidence | **Blocking** | Representative front and back photographs on different backgrounds |

**Source and result** [Docs/prd.md](Docs/prd.md), image capture requirement; [Docs/design.md](Docs/design.md), preprocessing and crop pipeline. The result is an upright image containing only the card so later OCR and grading measurements use the correct pixels.

**Observed issue** Observed problem: the preview included too much desk/background, some images flipped or rotated, and the capture outline was not card-shaped. The current PoC includes a card-shaped guide, clipping endpoint, previews, and manual rotation, but difficult photos still need testing.

**Scope** Detect four card corners, perspective-correct the image, remove surrounding background, and normalize orientation. Retain the card-shaped capture guide and manual rotate control as fallbacks. Scratch removal, glare removal, and counterfeit detection are outside this issue.

**Acceptance checks**

- The saved preview contains the complete card with all four edges visible and no large background area.

- Portrait photos remain upright and do not appear mirrored or rotated after upload.

- If automatic boundary detection fails, DeckFlow uses the guide crop and tells the user that the fallback was used.

- Front and back photos are not accidentally swapped.

**Completion evidence** Before-and-after crops for at least six photos, including bright, dark, angled, and worn cards; automated dimension/orientation checks; and a reviewed demonstration using one physical card.

**Uncertainty** Glare, sleeves, shadows, and low-contrast backgrounds can hide card boundaries.

## DF-03 Calibrate the experimental condition grade

| **Status**   | Open for 491             | **Owner**    | Isaac Parada, Technical Lead                                        |
|--------------|--------------------------|--------------|---------------------------------------------------------------------|
| **Priority** | Critical                 | **Effort**   | Large, 4-8 weeks                                                    |
| **Target**   | CPSC 491 model milestone | **Blocking** | Professionally graded reference cards or a licensed labeled dataset |

**Source and result** [Docs/prd.md](Docs/prd.md), unofficial pre-grade requirement; [Docs/design.md](Docs/design.md), centering, corner, edge, and surface analysis. The result is a defensible estimate with a range and visible reasons, not an official PSA or CGC grade.

**Observed issue** Observed problem: the early placeholder repeatedly showed 90, and at one point the damaged sample scored higher than the clean sample. Image-based measurements now produce an experimental estimate, but the model is not yet validated against professional labels.

**Scope** Measure centering, visible corner wear, edge whitening, surface cues, and photo quality; combine them into a reproducible 1-10 estimate; show uncertainty. This work does not certify authenticity or replace professional in-person grading.

**Acceptance checks**

- A visibly damaged prepared card scores lower than the clean prepared card under the same capture setup.

- Running the same images five times produces the same grade and defect list.

- The report provides a grade range and identifies which measurements reduced the score.

- Low-quality photos reduce confidence or request a retake instead of producing a confident high grade.

**Completion evidence** A labeled evaluation set with expected ordering, model or ruleset version, per-card output, error analysis, and a reviewed comparison against known grades where permission and data are available.

**Uncertainty** A normal phone image cannot reliably show every scratch, dent, print defect, or alteration considered by professional graders.

## DF-04 Show a rough graded value when raw pricing exists

| **Status**   | Resolved in PoC          | **Owner**    | Isaac Parada, Technical Lead                          |
|--------------|--------------------------|--------------|-------------------------------------------------------|
| **Priority** | High                     | **Effort**   | Small, completed                                      |
| **Target**   | November 20 PoC evidence | **Blocking** | An exact card printing and a nonzero raw market quote |

**Source and result** [Docs/prd.md](Docs/prd.md), price comparison requirement; [Docs/design.md](Docs/design.md), pricing service. The result is a clearly labeled rough graded-price estimate derived from the live raw quote and the experimental grade.

**Observed issue** Observed problem: every report displayed No verified price because the pricing service returned 0.0 for graded value. We added a grade multiplier model and changed the label to Rough graded-price estimate.

**Scope** Calculate a conservative grade-based estimate only when TCGdex or TCGplayer supplies a raw market value. Interpolate half grades and label the result as unverified. Historical PSA sales collection is outside the current PoC.

**Acceptance checks**

- When raw price is greater than zero, the report shows a nonzero rough graded-price estimate.

- Changing the estimated grade changes the rough graded value according to the documented multiplier table.

- When raw price is unavailable, DeckFlow says the estimate is unavailable and does not invent a dollar value.

- The interface never labels the modeled number as a verified PSA sale or appraisal.

**Completion evidence** Backend calculation test covering grades 1, 5.5, 9, and 10; screenshot of a report showing both values; reviewed commit titled Add rough graded card price estimate.

**Uncertainty** The multiplier is a prototype estimate and is not based on a verified sale for that exact grade.

## DF-05 Return the correct raw market price and variant

| **Status**   | In progress           | **Owner**    | Isaac Parada, Technical Lead                                 |
|--------------|-----------------------|--------------|--------------------------------------------------------------|
| **Priority** | High                  | **Effort**   | Medium, 1-2 weeks                                            |
| **Target**   | November 30 live demo | **Blocking** | Correct TCGdex printing ID and available TCGplayer USD quote |

**Source and result** [Docs/prd.md](Docs/prd.md), market information requirement; [Docs/design.md](Docs/design.md), TCGdex pricing lookup and cache. The result is the available USD market quote for the confirmed printing and a source label that identifies the variant.

**Observed issue** Observed problem: prices sometimes did not appear, the wrong candidate retained a price, and irrelevant Unavailable or Lightly Played rows cluttered the result. The PoC now uses TCGdex with exact candidate selection and a local cache, but variant coverage needs more tests.

**Scope** Resolve the exact catalog ID, select the relevant normal, holofoil, reverse-holo, first-edition, or unlimited quote, cache the response, and explain missing data. Do not show unsupported condition labels such as Lightly Played as if they were verified.

**Acceptance checks**

- Selecting a different candidate requests pricing for that candidate rather than retaining the previous card's value.

- The source label identifies the provider, currency, and selected variant.

- No-price responses remain explicit and never reuse a stale value from another card.

- Cached values are keyed by language and TCGdex card ID and expire according to the documented policy.

**Completion evidence** Integration tests for one normal, one holofoil, one missing-price, and one cached card; API response screenshots; and comparison with the provider response captured at test time.

**Uncertainty** Some printings and conditions have no current market quote; foil and non-foil variants can differ greatly.

## DF-06 Keep the phone QR upload session available

| **Status**   | Resolved in PoC, monitor | **Owner**    | Isaac Parada, Technical Lead                      |
|--------------|--------------------------|--------------|---------------------------------------------------|
| **Priority** | High                     | **Effort**   | Medium, completed for PoC                         |
| **Target**   | November 20 PoC evidence | **Blocking** | Cloudflare tunnel availability and network access |

**Source and result** [Docs/prd.md](Docs/prd.md), mobile capture requirement; [Docs/design.md](Docs/design.md), phone-to-laptop upload session. The result is one QR code that remains visible and accepts repeated front/back card pairs during the demo.

**Observed issue** Observed problem: the QR disappeared after a few seconds and each card required another scan or local IP setup. The PoC now uses a persistent session, upload counter, and automatic secure tunnel, but network fallback instructions are still needed.

**Scope** Create a secure upload session, keep the QR visible, accept both sides, report upload count, and allow another card without rescanning. Permanent hosted accounts and long-term media storage are outside this PoC.

**Acceptance checks**

- The QR remains visible for the full active demo session.

- One scan accepts at least three consecutive front/back card pairs.

- After each successful pair, the laptop receives new previews and the phone resets its pickers.

- Expired, missing-side, or unreachable sessions return a clear recoverable error.

**Completion evidence** Screen recording of three consecutive uploads through one QR, backend session logs, and a live test on the professor's or client's network before the formal demo.

**Uncertainty** School or client networks may block the tunnel, and free tunnel URLs are temporary.

## DF-07 Start the catalog automatically on a clean computer

| **Status**   | Resolved in PoC, regression test needed | **Owner**    | Isaac Parada, Technical Lead                                           |
|--------------|-----------------------------------------|--------------|------------------------------------------------------------------------|
| **Priority** | High                                    | **Effort**   | Medium, completed for PoC                                              |
| **Target**   | November 20 PoC evidence                | **Blocking** | Docker Desktop, internet access for first sync, and sufficient storage |

**Source and result** [Docs/prd.md](Docs/prd.md), deployable classroom demo; [Docs/design.md](Docs/design.md), local SQLite catalog. The result is a Docker startup that prepares or reuses the catalog without requiring the professor to know a separate sync command.

**Observed issue** Observed problem: the professor or teammate had to run docker compose exec backend python sync_catalog.py manually, and different computers showed different readiness. Startup and persisted catalog handling were added, but clean-machine testing should remain in the backlog.

**Scope** Initialize the SQLite catalog, persist it in a volume, expose readiness status, and prevent analysis until catalog readiness is known. Supporting every operating system or running without Docker is outside this issue.

**Acceptance checks**

- On a clean clone, docker compose up --build reaches a healthy catalog without a separate manual command.

- A second launch reuses the catalog instead of downloading all cards again.

- The catalog-status endpoint reports ready, source, and card count.

- If sync fails, the interface reports the failure and provides a retry path rather than a blank screen.

**Completion evidence** Clean-install terminal log, catalog-status response showing a nonzero card count, restart timing, and a reviewed test on a second MacBook.

**Uncertainty** A first-time English and Japanese catalog download can be slow or interrupted.

## DF-08 Prevent stale containers and browser assets from hiding updates

| **Status**   | Resolved development workflow | **Owner**    | Isaac Parada, Technical Lead                                       |
|--------------|-------------------------------|--------------|--------------------------------------------------------------------|
| **Priority** | Medium                        | **Effort**   | Small, completed                                                   |
| **Target**   | November 20 PoC evidence      | **Blocking** | Developers must run commands from the correct Git clone and branch |

**Source and result** [Docs/design.md](Docs/design.md), Docker deployment workflow. The result is a documented rebuild and verification procedure that confirms the browser is serving the intended branch and image.

**Observed issue** Observed problem: changes appeared to do nothing because an old DeckFlow folder was not a Git repository and an older Compose project continued serving localhost. We cloned the correct Isaac branch, stopped the old project, rebuilt without cache, and hard-refreshed the browser.

**Scope** Document branch checks, stop conflicting Compose projects, rebuild changed services, verify container status, and hard-refresh the browser. This issue does not replace continuous deployment or automated release versioning.

**Acceptance checks**

- The terminal confirms the intended branch before build and push.

- Only one gateway owns localhost port 5173.

- A no-cache rebuild displays the new Rough graded-price estimate label.

- The documented commands work from a fresh Git-connected clone without editing the old untracked folder.

**Completion evidence** Terminal output for branch, Compose status, and rebuilt image; browser screenshot showing the new label; README demo steps reviewed by another team member.

**Uncertainty** Docker project names differ when the repository folder name changes, so an older gateway can keep port 5173.

## DF-09 Keep one clear grading workflow in the interface

| **Status**   | Resolved in PoC          | **Owner**    | Raul Munoz, Team Lead; Isaac Parada, Technical Lead |
|--------------|--------------------------|--------------|-----------------------------------------------------|
| **Priority** | Medium                   | **Effort**   | Small, completed                                    |
| **Target**   | November 20 PoC evidence | **Blocking** | Agreement on the minimum PoC workflow               |

**Source and result** [Docs/prd.md](Docs/prd.md), single-card assessment user story; [Docs/design.md](Docs/design.md), capture-process-report flow. The result is one grading path that handles demo images, laptop camera capture, and phone upload without presenting three competing grading modes.

**Observed issue** Observed problem: the interface continued to show three options after the project changed to one AI grading workflow; loading feedback was also difficult to see. The PoC now uses a single assessment flow with an AI status indicator and animated loading state.

**Scope** Remove redundant mode tabs, keep one Analyze action, show progress, then display identity, grade, defects, prices, and history. Account management, collections, and selling are separate future features.

**Acceptance checks**

- The main page presents one card-grading workflow rather than three grading tabs.

- The user can complete front capture, back capture, analysis, candidate confirmation, and report review in order.

- Loading feedback remains visible while the backend processes images.

- Errors do not replace the entire page with a white screen.

**Completion evidence** Usability walkthrough, screenshots of each step, client feedback from Game Citi TCG, and a reviewed frontend pull request.

**Uncertainty** Client feedback may require additional entry points later, but they should not duplicate the same task.

# Recommended Review Order

For the November 20 PoC evidence submission, review DF-02, DF-04, DF-06, DF-07, DF-08, and DF-09 first because they can be demonstrated with the existing code. For the November 30 live demo, prioritize DF-01 and DF-05 so the selected card and raw market price are defensible. DF-03 is the largest CPSC 491 risk because an accurate grade requires labeled reference data and controlled evaluation, not only additional interface work.

# Definition of Done for Each GitHub Issue

- The issue links the relevant PRD requirement and design section.

- The scope states what is included and what is intentionally excluded.

- All acceptance checks have an attached pass or fail result.

- The pull request, test output, screenshot, or client check named as evidence is attached.

- The owner records remaining uncertainty and moves incomplete work to a follow-up issue.
