# 1. Overview
DeckFlow is a TCG card pre-grading system that will scan cards, evaluate visual defects, and provide an unofficial grade estimiation. It will also provide a price estimation and determine a time frame in which the card should be sold.

# 2. Purpose and value  
The purpose of DeckFlow is to provide Game Citi TCG informed decisions on the grading potential and value of their cards.

Currently, Game Citi TCG manually evaluates trading cards to determine their condition and whether submitting them for professional grading would be worthwhile. This process requires employees to inspect physical defects and research potential card values.

DeckFlow aims to improve this process by providing consistent pre-grading estimates, current market valuations, dynamic pricing recommendations, and suggested selling time frames.

The system could provide value to Game Citi TCG by reducing the time required to evaluate cards, improving pricing decisions, identifying potentially profitable grading opportunities, and creating an opportunity to offer paid pre-grading assessments to customers.
# 3. Objectives and success metrics
DeckFlow's primary objective is to help Game Citi TCG generate additional revenue through paid card assessments while improving the efficiency and consistency of its card evaluation process.

## Success Metrics
- Achieve at least 85% of estimated grades within one grade level of known professional graders.
- Achieve a price estimate the follows the market and would likely sell at said price
- Generate an assessment report within 15 seconds after valid images are uploaded

# 4. User personas
The primary user is an employee or owner at Game Citi TCG who assists customers who bring in cards with card evaluations. The employees work a regular wage and this would not increase their wage and instead would fall under as part of the job description. The employees have general tech knowledge and have an onsite computer they can use. Their responsibility will be to either use their phone or store laptop to scan the cards into the system and read the report on the card.

# 5. Features and user stories
- Feature 1: Card identification
User story: As a Game Citi employee, I want to scan a trading card so that I can identify its exact name, set, and version.

- Feature 2: Unofficial pre-grading
User story: As a Game Citi employee, I want to scan the front and back of a card and receive an estimated grade so that I can determine whether professional grading may be worthwhile.

- Feature 3: Dynamic pricing
User story: As a card shop owner, I want DeckFlow to adjust its suggested selling prices based on market changes so that I can keep my inventory competitively priced.

# 6. Non-functional requirements
1. Performance:
Complete analysis within 30 seconds for 90% of valid scans

2. Identification Accuracy:
At least 90% of cards scan are identified correctly

3. Grading Accuracy:
At least 85% of the cards have within 1 grade of known grading companies (PSA, TAG, etc.)

4. Reliability:
At least 90% of valid scans complete without system failire

5. Repeatability:
If a card is scanned more than once, at least 95% of the the card should produce the same grade. 

# 7. Assumptions, dependencies, and constraints
DeckFlow assumes that images captured using commercially available cameras can provide enough visual detail to detect card defects and generate unofficial grade estimates that are sufficiently accurate and consistent for Game Citi TCG to trust.

- Access to cards with known professional grades and legally usable reference images.
- Camera resolution and lighting sufficient to reveal defects.
- Access to legitimate historical and current market-price data.
- API costs, usage limits, and data licensing.
- Development time, equipment costs, and the team's technical resources.

# 8. User flows and design
1. Scan Trading Card:
Capture front and back images of card

2. Identify Card:
Determine name, set, and version

3. Evaluate condition:
Detect defects and provide grade estimations

4. Analyze market data:
Estimate value and dynamic selling price

5. Recommend selling window:
Sell now or consier selling later

# 9. Release criteria and timeline
TBD

# 10. Out of scope
DeckFlow will not replace professional grading companies such as PSA, CGC, or TAG. Its grade estimates will remain unofficial and will not guarantee the grade a card receives after professional submission. It is just an automated tested system that will give more confidence to the user on potential grade of the card.

# 11. Open questions
- Which trading card games and card sets should DeckFlow support initially?
- What minimum grading accuracy would Dan trust for paid assessments?
- Will employees use phones, store computers, or a dedicated scanner?
- Which legitimate market-data sources can provide recent and historical sales prices?
- Should dynamic prices update automatically or only when requested?
- How much historical data is necessary to recommend a selling window?
- Would Game Citi charge customers per assessment, and will customers pay?
- What maximum equipment and operating cost would make DeckFlow worthwhile?
- Should DeckFlow recommend whether to submit a card for grading before recommending when to sell it?