## 🎯 **Goal of Choice Tournament with D-Optimal Design**

To present **highly informative product choices** (sets of 2–3 profiles) that help us learn how the respondent makes trade-offs **within their acceptable preference space** — while maximizing the **statistical quality** of the data collected.

We do this using a **D-optimal design**, which selects the most **statistically efficient** set of profiles to estimate utilities (preferences) with **low uncertainty**.

---

## ✅ Prerequisites

From screening, we already know:

* Which attribute levels are **acceptable**.
* Which ones are **unacceptable** (excluded from further tasks).

---

## 🧱 Example Acceptable Attribute Space (from screening)

| Attribute | Acceptable Levels |
| --------- | ----------------- |
| Brand     | Apple             |
| Price     | \$699, \$1099     |
| Camera    | Triple, Quad      |
| Storage   | 256 GB            |

Now we only build profiles using these combinations.

---

## 🪜 Step-by-Step Algorithm

---

### **Step 1: Enumerate All Acceptable Profiles**

* Generate all possible product profiles **using only the acceptable levels**.
* In our example:

Total combinations = 1 (brand) × 2 (prices) × 2 (camera) × 1 (storage) = **4 profiles**.

These are:

| Profile ID | Brand | Price  | Camera | Storage |
| ---------- | ----- | ------ | ------ | ------- |
| P1         | Apple | \$699  | Triple | 256 GB  |
| P2         | Apple | \$699  | Quad   | 256 GB  |
| P3         | Apple | \$1099 | Triple | 256 GB  |
| P4         | Apple | \$1099 | Quad   | 256 GB  |

---

### **Step 2: Create a Design Matrix**

* Each profile is converted into **coded numerical variables** using **effects coding** or **dummy coding**.
* This allows us to mathematically represent how each attribute-level affects utility.

Example:

| Profile | Price\_\$1099 | Camera\_Quad |
| ------- | ------------- | ------------ |
| P1      | 0             | 0            |
| P2      | 0             | 1            |
| P3      | 1             | 0            |
| P4      | 1             | 1            |

---

### **Step 3: Use D-Optimal Design to Select Choice Sets**

* Use an algorithm (like **Fedorov’s exchange** or **coordinate exchange**) to:

  * Choose **choice sets** (e.g., sets of 2 or 3 profiles each).
  * Ensure:

    * **Each level appears evenly across sets** (level balance)
    * **Attributes vary independently** (orthogonality)
    * **Maximum information per choice** (minimize parameter uncertainty)

📌 In simple terms:
We’re trying to **ask the fewest but smartest questions** to **learn the most** about the respondent’s preferences.

---

### **Step 4: Construct Final Choice Sets**

* Once the D-optimal profiles are selected, group them into **choice sets** of 2 or 3.
* Example (2-alternative sets):

| Choice Set | Option A                     | Option B                      |
| ---------- | ---------------------------- | ----------------------------- |
| Set 1      | Apple, \$699, Triple, 256 GB | Apple, \$1099, Triple, 256 GB |
| Set 2      | Apple, \$699, Quad, 256 GB   | Apple, \$1099, Quad, 256 GB   |

---

### **Step 5: Randomize Presentation**

* Randomize:

  * Order of choice sets
  * Position of profiles (left/right/top/bottom)

This reduces bias due to position effects.

---

### **Step 6: Record Responses**

* Respondent selects their preferred option in each set.


---

## ✅ Summary of Key Properties

| Design Feature          | Why It Matters                           |
| ----------------------- | ---------------------------------------- |
| D-optimality            | Maximizes precision of utility estimates |
| Acceptable-level filter | Respects respondent-specific constraints |
| Minimal sets needed     | Efficient and shorter surveys            |
| Balanced and orthogonal | Prevents estimation bias                 |

---


