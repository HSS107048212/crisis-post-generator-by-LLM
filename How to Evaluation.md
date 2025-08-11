# Evaluating Entity Matching with Fuzzy Similarity

```text

data = { 
    "901958356973301760": {
        "text": "#Houston #HoustonFlood the intersection of I-45 &amp; N. Main Street https://t.co/jBPxoS4ub7",
        "T1": {"text": "I-45", "class": "highway"},
        "T2": {"text": "N. Main Street", "class": "highway"},
        "NER_T1": {"text": "Houston", "class": "LOC"},
        "NER_T2": {"text": "I - 45", "class": "LOC"},
        "NER_T3": {"text": "N", "class": "LOC"},
        "NER_T4": {"text": "Main Street", "class": "LOC"}
    },
    "901431863536996352": {
        "text": "#HarveyStorm over Austin, TX at 8:00 AM CDT via Weather Underground https://t.co/rbb1kU3FjM",
        "T1": {"text": "Austin", "class": "boundary"},
        "NER_T1": {"text": "Austin", "class": "LOC"},
        "NER_T2": {"text": "TX", "class": "LOC"}
    }
}

* T1, T2, T... are gold answers.
* NER_T1, NER_T2, NER_T... are Predicted answers.

```

## Objective

**Evaluating Entity Matching with Fuzzy Similarity**

- **Goal:** Compare predicted entities from a model with ground truth entities using fuzzy matching.
- **Data Source:** Example tweets with annotated ground gold answers (`T1`, `T2`, …) and model predictions (`NER_T1`, `NER_T2`, …).

---

## Step 1: Build Comparable Sets

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

## Step 2: Normalize and Compute Similarity

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

## Step 3: Greedy Matching

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

## Example01: Post `901958356973301760`

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

## Example02: Post `901431863536996352`

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

## Totals Across All Posts

- **True Positives (TP):** 2 (Post 1) + 1 (Post 2) = **3**
- **False Positives (FP):** 2 (Post 1) + 1 (Post 2) = **3**
- **False Negatives (FN):** 0 + 0 = **0**

---

## Metrics Calculation

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
