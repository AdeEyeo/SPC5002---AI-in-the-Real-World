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

<!-- Set each alternative against your pipeline through the mean difference, its
     sd and the wins out of 25, and say which of the differences you would call
     a finding and why. The folds share training orders, so the comparison is
     evidence but no statistical test, which needs saying once. -->

## 4. A number from an earlier week, reported again

<!-- Report again, the Week 8 way, one number that you reported before from a
     single split or without a spread, and say whether your conclusion
     changes. -->

## 5. What this evaluation cannot tell you

<!-- Name at least one thing that this evaluation cannot tell you and explain
     why the folds you used are unable to show it. -->
