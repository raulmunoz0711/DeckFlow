# DeckFlow

## 1. Who did you talk to, and are they the one who pays?

I spoke directly with Dan, the owner of Game Citi TCG near Cal State Fullerton.

Because Dan owns the business and is involved in its day-to-day operation, he is the person who would decide whether a system like DeckFlow creates enough value for the store to use and pay for.

Game Citi buys, evaluates, prices, and sells trading cards, so Dan is directly involved in the type of workflow our project is focused on.

Store website: https://www.gamecititcg.com/

---

## 2. What did they say the problem is, in their words? When did it last happen?

Dan explained that Game Citi regularly has to evaluate trading cards and collections that come into the store.

For valuable cards, employees need to determine exactly what card and version they are looking at, inspect its condition, research its current market value, and decide what the card is worth to the business.

Condition matters because two copies of the same card can have very different values depending on wear, damage, centering, surface condition, and the grade the card might receive from a professional grading company.

Pricing also requires repeated research because card values change over time and can differ significantly between raw cards and professionally graded cards.

The problem we are investigating is that this evaluation process depends heavily on manual inspection, employee knowledge, and repeated price research.

We still need to document a specific recent example from Dan in his own words, including when this workflow last happened, how many cards were evaluated, and how long the process took.

---

## 3. What does it cost them? Give the number. What forces them to act?

We do not yet have a verified dollar amount for the cost of Game Citi's grading and pricing workflow.

The cost comes from several areas.

Employees spend time identifying cards, inspecting condition, researching current prices, comparing raw and graded values, and deciding how much the store should offer or charge.

There is also potential revenue loss if a card is misidentified, incorrectly valued, purchased for too much, sold for too little, or submitted for professional grading when the grading fee does not justify the expected increase in value.

The store is forced to make these decisions because buying and selling cards is part of its normal business. When a customer brings cards into the store, employees need to make a pricing decision quickly enough to complete the transaction.

We still need to ask Dan for the numbers needed to calculate the cost accurately, including:

- How many cards or collections are evaluated each week
- How much employee time is spent evaluating cards
- How much employees involved in the process are paid
- How often professional grading is considered
- How often pricing or condition mistakes create a financial loss
- How much value the store expects to gain from faster or more accurate evaluation

Until we have those numbers from Dan, we should not claim a specific annual cost.

---

## 4. What have they already tried or paid for? Why are they not using what exists?

Today, card evaluation is handled using a combination of employee experience and existing third-party tools.

Employees can use marketplaces and pricing websites to research card values, while professional grading companies such as PSA, CGC, and Beckett provide official grades for cards that are submitted to them.

There are also card-scanning and collection-management applications that can help identify cards or display market prices.

However, these tools generally solve separate parts of the workflow.

An employee may still need to:

1. Identify the exact card and variant
2. Inspect the card manually
3. Estimate its condition
4. Search current market prices
5. Compare raw and graded prices
6. Estimate what grade the card might receive
7. Decide whether professional grading would be financially worthwhile
8. Decide what the store should offer or charge

The opportunity we are investigating is whether those separate steps can be combined into a single evaluation workflow.

We do not yet know exactly which pricing, scanning, grading, or inventory tools Dan currently pays for.

We also do not yet know which existing products he has tested or rejected.

That is information we still need to verify with him directly.

---

## 5. How big is the domain, who already sells this, and what does it cost?

Our domain is trading-card evaluation, grading, and pricing for businesses that buy and sell collectible cards.

The domain includes several groups of businesses and services:

- Local trading-card shops
- Card-show vendors
- Online card sellers
- Trading-card marketplaces
- Collection-management platforms
- Card-scanning applications
- Professional grading companies
- Pricing-data providers

Several companies already operate in parts of this domain.

Professional grading companies such as PSA, CGC, and Beckett charge customers to evaluate cards and assign official grades.

Marketplaces and pricing platforms provide current and historical sales data.

Collection-management and card-scanning applications help users identify cards and track market value.

There are also newer services experimenting with computer vision and automated card-condition analysis.

This shows that people already spend money on card identification, grading, pricing, and inventory management.

However, we still need sourced numbers for:

- The total size of the collectible trading-card market
- The number of trading-card shops and professional sellers
- Professional grading fees
- Marketplace selling fees
- Pricing-platform subscription costs
- Card-scanning software costs
- Existing AI-grading products
- The size of the market specifically for businesses that evaluate cards for resale

Every number added to this section needs to come from a source.

---

## 6. What is hard about it that someone with AI could not do in a weekend, and can your team do it in a year?

The difficult part is not creating an application that scans a card and displays a price.

A generalist using AI could build a simple card-scanning interface or price-lookup application in a weekend.

The difficult part is making the grading and pricing results accurate and reliable enough for a real card shop to use when making financial decisions.

For the AI-grading portion, the system would need to analyze card images and identify defects such as:

- Edge wear
- Corner wear
- Whitening
- Surface scratches
- Print defects
- Centering problems
- Creases
- Other visible damage

The system would also need to handle differences in lighting, glare, camera angle, image quality, card sleeves, and background conditions.

It would need training and evaluation data from cards with known conditions or professional grades so that we can measure whether the model is actually accurate.

The system also has to correctly identify the exact card and variant. Cards that look very similar can have different sets, printings, rarities, languages, or market values.

Misidentifying a card would make the grading and pricing results unreliable.

For the dynamic-pricing portion, the system needs to combine the card's identity and estimated condition with current market data.

The same card can have very different values depending on whether it is raw or professionally graded and what grade it receives.

The pricing system may need to consider:

- Current raw-card prices
- Recent completed sales
- Expected graded values
- Professional grading fees
- Marketplace fees
- Condition
- Predicted grade
- Confidence in the prediction
- Market changes over time

The system also needs to handle missing sales data, stale prices, rare cards, unusual variants, and cards where very few recent sales exist.

The real technical depth comes from combining computer vision, machine learning, card recognition, model evaluation, pricing-data integration, and business decision logic into one reliable workflow.

A basic demonstration could be created quickly.

A system accurate enough to influence real buying, selling, and grading decisions would require data collection, model training, evaluation, testing, and repeated improvement.

We believe a useful prototype is achievable within a year if we control the scope and begin with a limited set of supported cards instead of trying to grade every trading card immediately.

---

## 7. What do you still not know?

There are several major unknowns that could determine whether the project is viable.

### Training Data

We do not yet know whether enough high-quality labeled card images exist for training and evaluating the grading model.

We need images that include reliable information about the card's condition or known professional grade.

If we cannot obtain enough useful training data, the AI-grading portion of the project may need to change.

### Grading Accuracy

We do not yet know how accurately a computer-vision model can estimate card condition from normal camera images.

Professional graders may inspect small defects that are difficult to capture with standard lighting and cameras.

We need to compare our system against cards with known grades to determine whether the estimates are useful.

### Image Capture

We do not yet know what camera, lighting, background, and image angles will be required.

A model may perform well with controlled images but fail when cards are photographed under normal store conditions.

### Card Identification

We do not yet know how accurately we can distinguish between similar card versions, sets, printings, and variants.

Misidentification could produce an incorrect market price even if the condition estimate is accurate.

### Pricing Data

We do not yet know which platforms can provide the current and historical sales data we need.

We need to determine:

- Whether they provide APIs
- What the APIs cost
- Their rate limits
- Their terms of use
- Whether automated access is allowed
- Whether enough recent sales exist for uncommon cards

### Dynamic Pricing Logic

We do not yet know the best way to translate card identity, condition, predicted grade, and market data into a recommended value.

We need to determine how much weight should be given to recent sales, condition, grading costs, marketplace fees, and uncertainty.

### Client Trust

We do not yet know how accurate the system must be before Dan would trust it during a real transaction.

A model that is technically impressive but not trusted by the store would not solve the business problem.

### Business Value

We still need to determine how much time and money Game Citi currently spends evaluating cards and whether a faster or more consistent process creates enough value for Dan to pay for the system.

### Scope

We do not yet know which cards should be supported first.

Trying to support every Pokémon card, every trading-card game, and every possible card condition immediately would likely make the project too large.

The first version may need to focus on Pokémon cards, higher-value cards, specific sets, or another limited category.

---

## Team Problems / Major Technical Risks

- AI card-condition and grade estimation
- Training-data availability
- Training-data quality and labeling
- Detecting small physical defects from images
- Handling lighting, glare, and camera-angle differences
- Card and variant misidentification
- Measuring model accuracy against professionally graded cards
- Determining confidence in predicted grades
- Reliable current and historical pricing data
- Pricing API availability and restrictions
- Handling cards with little or no recent sales data
- Connecting condition estimates to market value
- Comparing raw value with expected graded value
- Accounting for grading fees and marketplace fees
- Keeping pricing recommendations current as the market changes
- Determining how accurate the system must be for Game Citi to trust it