## Question 1

'export_seq', with a single-column ROC-AUC of about 0.93

## Question 2

'export_seq' is not a property of the order. It's the row's position in the exported file, assigned when someone pulled the data out of the order system. All returned orders fall within rows 7 to 600, so whatever determined the row order already knew which orders were returned. The likely story is that whoever built the extract sorted it using return information first and appending the rest, or sorting by a field like last-updated time that changes when a return is processed. The sequence number was assigned after that ordering, so it encodes the outcome.

## Question 3

None of them would have flagged it. They check the data's size and the target's rate, not whether a feature carries information it shouldn't. The only output that hinted at it is the coefficient table, where export_seq likely dwarfs the others, and an ROC-AUC that's suspiciously high for predicting customer behaviour.

## Question 4

The question is: "Could I have obtained this column, with this value, at the moment I needed
the prediction?" You would have to ask whoever owns the system the export came from.