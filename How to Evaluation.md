# Evaluating Entity Matching with Fuzzy Similarity

## Slide 1 – Objective

**Evaluating Entity Matching with Fuzzy Similarity**

- **Goal:** Compare predicted entities from a model with ground truth entities using fuzzy matching.
- **Data Source:** Example tweets with annotated ground truth (`T1`, `T2`, …) and model predictions (`NER_T1`, `NER_T2`, …).
- **Evaluation Method:** Entity-level matching, no TN counted.

---

## Slide 2 – Step 1: Build Comparable Sets

**Ground Truth Set (golds):** Keys starting with `T` but not `NER_`  
Example:  
```text
["I-45", "N. Main Street", "Austin"]
```

**Prediction Set (preds):** Keys starting with `NER_`  
Example:  
```text
["Houston", "I - 45", "N", "Main Street", "TX"]
```

---

## Slide 3 – Step 2: Normalize and Compute Similarity

**Normalization:**
1. Convert to lowercase.
2. Remove spaces, hyphens, and dots.  
   - `"I - 45"` and `"I-45"` → `i45`
   - `"N. Main Street"` → `nmainstreet`

**Similarity Metric:**
- Use `difflib.SequenceMatcher` ratio.
- **Threshold:** `0.85`
- Only pairs with similarity ≥ 0.85 are eligible matches.

---

## Slide 4 – Step 3: Greedy Matching

**Process:**
1. For every prediction–truth pair:  
   - Compute similarity score.
2. Collect all pairs `(score, pred_index, gold_index)`.
3. Sort all pairs by score (descending).
4. Match greedily:  
   - Skip if score < 0.85.  
   - Skip if either prediction or truth already matched.  
   - Otherwise, match and count as **True Positive (TP)**.

**After matching:**
- Unmatched predictions → **False Positives (FP)**.
- Unmatched truths → **False Negatives (FN)**.

---

## Slide 5 – Example: Post `901958356973301760`

**Ground Truths:**  
```text
["I-45", "N. Main Street"]
```

**Predictions:**  
```text
["Houston", "I - 45", "N", "Main Street"]
```

**Key Similarities:**
- `"I - 45"` vs `"I-45"` = **1.0000** → TP (+1)
- `"Main Street"` vs `"N. Main Street"` = **0.9524** → TP (+1)
- Others < 0.85 → No match

**Results:**
- Unmatched Predictions: `"Houston"`, `"N"` → FP +2
- Unmatched Truths: None → FN +0

---

## Slide 6 – Example: Post `901431863536996352`

**Ground Truths:**  
```text
["Austin"]
```

**Predictions:**  
```text
["Austin", "TX"]
```

**Key Similarities:**
- `"Austin"` vs `"Austin"` = **1.0000** → TP (+1)
- `"TX"` vs `"Austin"` = **0.25** → No match

**Results:**
- Unmatched Predictions: `"TX"` → FP +1
- Unmatched Truths: None → FN +0

---

## Slide 7 – Totals Across All Posts

- **True Positives (TP):** 2 (Post 1) + 1 (Post 2) = **3**
- **False Positives (FP):** 2 (Post 1) + 1 (Post 2) = **3**
- **False Negatives (FN):** 0 + 0 = **0**

---

## Slide 8 – Metrics Calculation

**Precision**  
\[
\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}} = \frac{3}{3 + 3} = 0.5
\]

**Recall**  
\[
\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}} = \frac{3}{3 + 0} = 1.0
\]

**F1-score**  
\[
F1 = \frac{2 \times 0.5 \times 1.0}{0.5 + 1.0} = 0.6667
\]

**Entity Accuracy** (no TN counted)  
\[
\text{Accuracy} = \frac{\text{TP}}{\text{TP} + \text{FP} + \text{FN}} = \frac{3}{3 + 3 + 0} = 0.5
\]

---

## Slide 9 – Why No TN

**True Negative (TN):**  
Cases where both truth and prediction are “not an entity.”

**In entity-level evaluation:**
- We do not enumerate all possible non-entity spans.
- Non-entities vastly outnumber entities → TN not defined.
- Hence, **accuracy** is based only on **(TP + FP + FN)**.
