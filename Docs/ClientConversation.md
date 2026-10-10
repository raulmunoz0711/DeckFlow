# **Game Citi TCG | Client Discovery Interview**

**Client:** Dan, store owner
Record type: _Interview notes_

# 1. Existing grading workflow
**Student:** Do customers bring raw cards in and ask whether to submit them to PSA?

**Dan - _interview notes:_**
Yes. Customers regularly bring in raw Pokémon cards and ask for an opinion on their condition and whether professional grading is worthwhile. Dan estimates approximately four to five such inquiries per week, sometimes more.

**Student:** What happened during the most recent customer inquiry?

**Dan -  _interview notes:_**
A customer brought in a Mew card. Dan inspected its condition, including corners, surface, creases and whitening. He judged the card to be in poor condition and advised the customer not to submit it for grading, but to keep it as-is.

**Student:** What does a typical evaluation involve, and how long does it take?

**Dan -  _interview notes:_**
Dan estimates approximately five minutes per card. He inspects the corners; surface; edge whitening, including on the back; dots; print lines; scratches; and front and back centering. This is his visual condition-assessment workflow. Whether the five minutes includes market-price research remains to be clarified.

**Student:** How do you evaluate shop-owned cards?

**Dan -  _interview notes:_**
Dan inspects cards after purchasing them and considers whether to sell them raw or submit them for grading. For cards that are especially high-value or niche, he may instead take them to a card show.

# 2. Consequences, costs, and current baseline
**Student:** What happens when a card expected to receive a 10 comes back as a 9 or 8?

**Dan -  _interview notes:_**
Dan accepts the lower grade and sells the card as a PSA 9 or PSA 8 rather than removing it from the graded case and reselling it raw. This can reduce the expected return on the submission. As an example: a $50 raw card might be worth $400 as a PSA 10 but only 50-100 as a PSA 9. 

**Student:** What submission costs do you consider?

**Dan -  _interview notes:_**
Grading fees and shipping costs. Grading fees vary depending on the number of cards submitted and the value of the card. Exact fee amounts, insurance costs, and selling fees were not provided.

**Student:** What is the bigger problem: time, uncertain predictions, or missed grading opportunities?

**Dan -  _interview notes:_**
Dan highlighted the lengthy process of sending cards to PSA and waiting to receive them back, as well as potentially missing profitable grading opportunities. Time spent evaluating cards is another relevant factor. 

# 3. Existing tools and trust
**Student:** Have you tried an AI pre-grading or scanning tool?

**Dan -  _interview notes:_**
Yes. Dan previously tried a free tool. His process was to inspect the card himself first and then compare his assessment with the scanner's result. He stopped using the tool because he considered its outputs inconsistent and could not trust its grade estimates.

**Student:** What specifically made it unreliable?

**Dan -  _interview notes:_**
The tool's condition metrics and grade estimates often did not match Dan's own assessment. He did not have professional grading results for those same cards to establish whether his assessment or the tool was correct; the issue was a lack of trust and perceived consistency, not a verified  measured accuracy rate.

**Student:** What would happen if no new software were built?

**Dan -  _interview notes:_**
Based on the described workflow, Dan would likely continue inspecting cards manually as he does today. 

# 4. Proposed solution and usefulness
**Student:** Which part of the proposed system would help most?

**Dan -  _interview notes:_**
Dan emphasized receiving a consistent condition evaluation that he could agree with and trust. The proposed system would scan front and back images, identify the card, assess visible condition, communicate uncertain grade estimates, and compare grading economics. 

**Student:** What evidence would help establish trust?

**Dan -  _interview notes:_**
Dan suggested comparing the tool's results with cards that received professional grades, especially PSA 9 and PSA 10 cards, to see whether its predictions align. Repeated-scan consistency and transparent identification of visible defects are reasonable candidate tests

# 5. Paid pre-grading service hypothesis
**Student:** Do customers ask for grading advice, and would you consider charging?

**Dan -  _interview notes:_**
Yes. Dan receives frequent requests for grading and condition opinions and would consider charging for an assessment service.

**Student:** Have you charged for condition opinions before? Why or why not?

**Dan -  _interview notes:_**
Dan has not previously charged for condition opinions. He feels some customers are seeking reassurance or a favorable opinion rather than a candid assessment. He added that customers might prefer whichever shop or vendor gives the most positive answer. 

**Student:** How would you price a trial?

**Dan -  _interview notes:_**
Dan expressed a preference for charging per card and suggested $10 per card. Whether customers will actually pay that price remains untested.

**Student:** What would make a 30-day pilot worthwhile?

**Dan -  _interview notes:_**
Dan identified the number of paid assessments as a useful success measure. He also agreed that net contribution from the service - revenue less incremental labor and operating costs is a reasonable business metric. 

# 6. Acceptance criteria and primary concern
**Student:** Would a scan-to-report workflow be a reasonable minimum?

**Dan -  _interview notes:_**
Dan agreed that scanning a supported card from both sides, identifying it, presenting visible condition findings and a confidence-aware grade estimate, showing market information, and producing a report is a reasonable workflow. Poor images or unidentifiable cards should not produce unjustifiably confident predictions.

**Student:** What is the biggest reason you might not offer the service?

**Dan -  _interview notes:_**
Dan has not seen software that is consistently convincing enough to justify trusting and selling such assessments. He questioned why professional grading companies, such as CGC, have not already made this kind of automated grading standard. His concern is whether the underlying technology can be validated and trusted, rather than whether a user interface can be built.

# 7. Findings, gaps, and next steps
**_Client-confirmed activity:_**
About 4-5 grading-opinion inquiries weekly, sometimes more.

**_Inspection baseline:_**
Approximately 5 minutes for visual card inspection; 

**_Potential offer:_**
Per-card paid pre-grading service; Dan suggested $10 per card.

**_Primary technical risk:_**
Trustworthy and consistent grading estimates, particularly for PSA 9 versus PSA 10.

**_Pilot business measure:_**
Count of paid assessments; net contribution also accepted as reasonable.

**_Not yet validated:_**
Willingness of customers to pay, actual lost-profit amounts, grading accuracy, minimum acceptable reliability, and monthly targets.