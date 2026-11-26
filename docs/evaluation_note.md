<!-- This is the Week 8 evaluation note. Copy it to docs/evaluation_note.md and
     write it there in prose, over one to two pages, and put a single table in
     section 2. Every number in sections 1 to 3 comes from your own
     outputs/evaluation.json or outputs/evaluation_folds.csv, and
     docs/week08_homework.md says what goes into each section. The comments are
     not counted, so you may delete them or leave them as they are. -->

# Evaluation note

## 1. How the numbers were made

The data are the 1,996 orders in data/orders_clean.csv, of which 382 were returned, a base rate of 0.1914. Every candidate was scored on the same 25 folds. These are five-fold stratified cross-validation (StratifiedKFold(5, shuffle=True)) repeated with the shuffle seeds 0, 1, 2, 3 and 4. Stratifying keeps the share of returns in each test fold close to the base rate. Every test fold holds 399 or 400 orders, with 76 or 77 returns. In each fold, every model is fitted again from scratch on the other four fifths and scored on the held-out fifth, so no candidate ever sees its test orders.

There are four candidates. My pipeline is the one built in Week 5. It fills missing values with the median and standardises six numeric columns (item price, discount, customer's prior orders, delivery days, order value, quantity). It one-hot encodes four categories (channel, category, payment method, customer region), then fits a logistic regression. Class weight balanced is the same pipeline with class_weight="balanced", the Week 6 change that weights returns more heavily. Decision tree, depth 4 keeps the same features but replaces the logistic regression with a decision tree of depth 4 (random_state=0). The rule is my Week 6 baseline: flag every footwear or apparel order. It is scored as 1 for a flagged order and 0 for every other order, and it is not fitted.

Each candidate gets two scores per fold. ROC-AUC measures how well it ranks returned orders above kept ones. PR-AUC (average precision) measures how well it finds returns, and it has a floor: the share of returns in that test fold, which is what a random ranking would score. Lift is PR-AUC divided by that floor. Every figure below is a mean over the 25 folds, and every sd is np.std over the 25 folds, which divides by 25.

## 2. The table

| Candidate | ROC-AUC | sd | PR-AUC | floor | lift |
|---|---|---|---|---|---|
| the rule | 0.5944 | 0.0271 | 0.2311 | 0.1914 | 1.21 |
| my pipeline | 0.6201 | 0.0347 | 0.2636 | 0.1914 | 1.38 |
| class weight balanced | 0.6196 | 0.0350 | 0.2644 | 0.1914 | 1.38 |
| decision tree, depth 4 | 0.5789 | 0.0274 | 0.2302 | 0.1914 | 1.20 |

My pipeline and its class-weighted version rank best, and are almost identical. Both find returns about 1.38 times as well as chance. The rule and the depth-4 tree are both lower, at about 1.2 times chance. All four rankings are weak: a ROC-AUC of 0.62 is well above 0.5 but far from 1. Because the folds are stratified, the floor barely moves (0.1905 to 0.1930), so here lift and PR-AUC tell the same story. Lift matters when the floor does move. In Thursday's lecture, PR-AUC rose on one split only because its test set held more returns.

## 3. Which differences are findings

To see which changes helped, each alternative was compared with my pipeline on the same fold. The comparison uses the ROC-AUC difference, alternative minus pipeline, so a positive number means the alternative is better. A fold that is hard for one model tends to be hard for all of them. Comparing fold by fold removes that shared difficulty, which comparing two overlapping means would not.

The decision tree is lower than my pipeline by 0.0412 on average, with an sd of 0.0243, and is higher in only 2 of the 25 folds. The difference is about 1.7 times its sd and goes the same way in 23 folds, so I call it a finding: replacing the logistic regression with a depth-4 tree makes the ranking worse.

The rule is lower than my pipeline by 0.0258, sd 0.0194, and is higher in 4 of 25 folds. My pipeline beats my own one-line rule in 21 of 25 folds. That difference is larger than its sd, but only by about a third, so I call it a finding, a modest one. Ten columns and a fitted model buy about 0.026 of ROC-AUC over a rule anyone can apply by hand.

Class weight balanced differs from my pipeline by −0.0006, sd 0.0028, and is higher in 11 of 25 folds, about half. The difference is a fifth of its sd, so it is not a finding: weighting the returns does not change how the pipeline ranks orders. That fits Week 6, where its use was to move the cut-off, not to improve the ranking.

The 25 folds are built from the same 1,996 orders, so their training sets overlap and the folds are not independent. The sds and win counts are therefore evidence, not a statistical test, and I quote no p-values.

## 4. A number from an earlier week, reported again

In Milestone 2 I chose an operating point, a threshold of 0.194 on the model's probability of a return. I reported it as a precision of 0.259 and a recall of 0.678, one number each with no spread, from out-of-fold probabilities averaged over five shuffles. The threshold was also picked on those same probabilities.

Reported again on the 25 folds above, with the model refitted in each fold and the same threshold applied to its test orders, the precision is 0.2562 (sd 0.0218) and the recall 0.6590 (sd 0.0612). Across folds the precision ranges from 0.20 to 0.29. The rule, in the same folds, has a precision of 0.2551 (sd 0.0185) and a recall of 0.6126 (sd 0.0514).

Fold by fold, the model's precision is higher than the rule's by only 0.0011, sd 0.0129, in 12 of 25 folds: no difference. Its recall is higher by 0.0465, sd 0.0443, in 21 of 25 folds. That is just larger than its sd, but the model also flags more orders than the rule (197 against 184 per fold on average), and flagging more raises recall on its own.

My conclusion changes. In Milestone 2 the operating point read as the model beating the rule. Measured properly, at this cut-off the model is exactly as precise as "flag every footwear or apparel order" and finds slightly more returns by flagging slightly more orders. The model's real advantage is the one section 3 shows: it ranks, so the cut-off can move, while the rule is one fixed point.

## 5. What this evaluation cannot tell you

It cannot say how the model would do on next year's orders. The folds are drawn at random from one year of orders, so every test fold sits among training orders from the same months. If customers, prices or the product mix change, the scores above could fall, and only a split in time, training on earlier orders and testing on later ones, would show it.

It says little about customers the model has never seen. Customers place about 2.2 orders each, and random folds put most of them on both sides of the split. When I kept each customer's orders on one side in Week 5, the score dropped slightly, from 0.6199 to 0.6142 (docs/feature_notes.md). That was within the sd, but this evaluation does not test it.

The scores are for a model that is allowed a slightly late view. I kept delivery_days, which is not known at checkout, so that my scores line up with the lab's (docs/milestone2_preprocessing.md). A model used at checkout could not have it, so these numbers are likely a little higher than such a model would score.
