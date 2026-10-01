# 1. The industry
Game Citi TCG operates in the for-profit trading-card retail and resale industry. Businesses like Game Citi make money from sealed trading-card products, buying and reselling individual cards and collections, facilitating trades, and potentially selling through online marketplaces.

The U.S. trading card game market generated an estimated $6.07 billion in 2025, according to Grand View Research. The secondary market—where individual cards are bought and resold—is particularly relevant to our domain because the value of a card can change dramatically based on its condition and whether it receives a professional grade.

Our specific domain is not the entire trading-card industry. It is for-profit card shops and sellers that acquire raw cards and must decide which cards are financially worth submitting to professional grading companies such as PSA.

For these businesses, grading is an investment decision. The business has a raw card worth some amount today, pays grading and associated costs, waits for the card to return, and hopes the resulting grade increases the card's resale value enough to justify those costs.
Game Citi is currently our only interviewed client, so we cannot yet claim how many card shops experience this problem or how significant it is across the industry.

# 2. Who else has this problem
Our current client is Dan, owner of Game Citi TCG near Cal State Fullerton. We're investigating the decision a card business makes about whether a raw card is worth professionally grading.
The potential domain extends beyond Game Citi to other for-profit card shops, card-show vendors, resellers, and businesses that regularly purchase raw collections. However, we have only interviewed Game Citi so far, so whether those other businesses experience the problem at a meaningful scale is still an assumption we need to validate.

The decision matters because the same card can have substantially different market values depending on its professional grade. A seller therefore has to consider:

|raw card value → condition → likely grade → graded value → grading costs → selling costs → expected profit|

Businesses already spend money addressing this problem. Professional grading itself is a paid service, and card businesses also spend employee or owner time inspecting cards, researching comparable sales, and deciding which cards warrant submission.

The important question for our research isn't merely whether collectors like knowing grades. It's whether for-profit sellers make enough grading decisions that improving the quality and speed of those decisions has measurable financial value.

# 3. How it is handled today and what it costs
Today, the decision is largely made through manual inspection and market research.
A seller examines a raw card's condition. They consider characteristics such as:
- centering
- corners
- edges
- surface condition
- scratches or print defects
They then estimate what grade the card might receive and compare the card's raw value against sales of professionally graded copies.
The financial decision might look like this:

Raw value: $100

Potential PSA 8 value: $110
Potential PSA 9 value: $175
Potential PSA 10 value: $500

If the seller believes the card has a strong chance of receiving a 10, grading could potentially create significant value. If it's likely an 8, selling the card raw may make more financial sense.
But the business has uncertainty because the grade is unknown until after the money has been spent and the card has been submitted.
That makes this primarily a revenue and investment-decision problem, rather than simply a labor cost problem.
The actual calculation should eventually account for:
|Expected graded sale price − grading fees − shipping − marketplace fees − acquisition cost − other costs|
and compare that with:
Expected raw sale price − selling costs

Online selling also has meaningful transaction costs. For example, eBay's fee structure for trading cards includes a percentage of the total sale amount, meaning a higher graded sale price doesn't translate directly into the same increase in profit.

We still need Game Citi-specific numbers from Dan: how many cards he considers for grading, how many he actually submits, what he typically spends on grading, how he currently estimates grades, and whether bad grading decisions have caused measurable losses or missed profits.
Those numbers will determine the actual economic size of the problem for our client.

# 4. What has been tried or sold
There are already several products and services addressing portions of this problem.

The largest established solution is professional grading itself, particularly companies such as PSA. A seller physically submits a card, pays a grading fee, and receives an authenticated and professionally graded card.
There are also scanning and card-identification applications that help users identify cards and retrieve market information, and there are companies exploring automated or AI-assisted approaches to card grading.
That means our research question cannot simply be:

“Can AI grade a Pokémon card?”

Other companies are already attempting that.

The more interesting business problem is whether current tools allow a card shop to efficiently answer:
“Before I spend money sending this card to PSA, what grade is it likely to receive, what is that prediction's confidence, and does the expected financial return make grading this particular card worthwhile?”
That's where the potential value lies.

A human can inspect one card and manually research prices. What becomes difficult at scale is consistently examining hundreds of cards, estimating grade probabilities, looking up raw and grade-specific market values, incorporating grading and selling costs, and calculating which cards have the highest expected return.

The system would therefore need to provide decision support, rather than pretending to replace professional grading.

We still need to research existing AI pre-grading products in detail, including their prices, claimed accuracy, limitations and market-data capabilities, and ask Dan whether he has used or considered any of them.

# 5. What is still unknown
There are several major assumptions we need to validate before deciding whether this is a viable project.

First, we don't know how large this problem is for Game Citi. We need to ask Dan how many raw cards he evaluates for grading each month, how many he submits, how much time he spends evaluating them, and how often the resulting professional grade differs significantly from what he expected.

Second, we don't know whether image-based analysis can predict professional grades accurately enough to be financially useful. Professional grading considers small defects in centering, corners, edges and surfaces. We need to determine whether controlled front/back images contain enough information to detect those defects and whether we can obtain enough cards with known professional grades to create and evaluate a model.

Third, training data may be a major constraint. We would need images of cards paired with reliable grading outcomes. We need to determine where that dataset can legally come from, whether an existing dataset is available, or whether we would need to create our own.

Fourth, we need legitimate market-price data. To compare raw and graded values, we need recent sales information for the exact card at different grades. We need to investigate available APIs, their costs, rate limits, licensing requirements and terms of service rather than assuming we can scrape marketplace websites.

Fifth, we don't know how accurate the system must be to create business value. An incorrect prediction could cause a business to spend money grading a card that isn't worth grading, or pass on one that would have been profitable. We need to establish acceptable error rates with Dan and evaluate predictions against cards that subsequently receive real professional grades.

Sixth, we need to understand existing competition. We need to identify existing AI grading/pre-grading products, what they charge, how they work, and most importantly why Dan isn't already using one. 