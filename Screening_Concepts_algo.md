 Screening + Acceptable/Unacceptable Inference Algorithm
🎯 Objective
To test slight variations around a respondent’s ideal product (BYO) and automatically infer which attribute levels are acceptable and which are unacceptable, allowing the system to skip the explicit must-have/unacceptable step and proceed directly to the Choice Tournament.

🧭 Algorithm Steps
Step 1: Start from the BYO Profile
Each respondent builds an ideal product by selecting one level per attribute (BYO).

This profile becomes the reference or anchor point.

Step 2: Generate Screening Concepts
System generates 10–15 concepts by perturbing the BYO profile.

Each concept differs from the BYO in one or two attributes (controlled deviation).

These variants are designed to explore whether changing a specific level is tolerated.

Goal:
Ensure every level (except the BYO-chosen ones) appears at least once, so that it can be tested for acceptability.

Step 3: Present Screening Concepts and Collect Responses
Each concept is shown one by one.

Respondent is asked:

“Would you consider this product?” (Accept / Reject)

Each response gives insight into which levels are tolerated.

Step 4: Tally Accept/Reject Counts by Attribute-Level
For each concept shown:

Note which levels it contains.

If the concept is rejected, increase the reject count for each level it contains.

If the concept is accepted, increase the accept count for each level.

Step 5: Infer Acceptable and Unacceptable Levels
For each attribute-level pair:

If it has at least one acceptance, it is marked acceptable.

If it has only rejections, and appears in multiple rejected concepts, it is marked unacceptable.

Thresholds can be adjusted — e.g., mark as unacceptable only if it appears in ≥2 rejected concepts with no acceptance.

Step 6: Filter the Design Space for the Tournament
Now you have two sets:

Acceptable levels → use only these to generate candidate profiles.

Unacceptable levels → exclude these from all future tasks.

Profiles in the Choice Tournament will now:

Contain only acceptable levels.

Avoid combinations that previously caused rejection.

Example: Smartphone Purchase Preferences
Attributes and Levels
Attribute	Levels
Brand	Apple, Samsung, OnePlus
Price	$699, $899, $1099
Camera	Dual (12MP), Triple (48MP), Quad (108MP)
Storage	128 GB, 256 GB

🧱 Step 1: Respondent's BYO Profile
The respondent chooses:

Brand: Apple

Price: $899

Camera: Triple (48MP)

Storage: 256 GB

This becomes the anchor concept.

🧪 Step 2: Generate Screening Concepts
System generates 6 screening concepts by altering one or two attributes from BYO:

| Concept ID | Brand       | Price      | Camera   | Storage    | Response |
| ---------- | ----------- | ---------- | -------- | ---------- | -------- |
| C1         | **Samsung** | \$899      | Triple   | 256 GB     | Reject   |
| C2         | Apple       | **\$1099** | Triple   | 256 GB     | Accept   |
| C3         | Apple       | \$899      | **Quad** | 256 GB     | Accept   |
| C4         | Apple       | \$899      | Triple   | **128 GB** | Reject   |
| C5         | **OnePlus** | **\$699**  | **Dual** | 128 GB     | Reject   |
| C6         | Apple       | **\$699**  | Triple   | 256 GB     | Accept   |


📊 Step 3: Tally Responses per Level
| Attribute | Level   | Accepted | Rejected |
| --------- | ------- | -------- | -------- |
| Brand     | Apple   | 3        | 0        |
| Brand     | Samsung | 0        | 1        |
| Brand     | OnePlus | 0        | 1        |
| Price     | \$699   | 1        | 1        |
| Price     | \$899   | 0        | 0        |
| Price     | \$1099  | 1        | 0        |
| Camera    | Triple  | 3        | 0        |
| Camera    | Quad    | 1        | 0        |
| Camera    | Dual    | 0        | 1        |
| Storage   | 256 GB  | 3        | 0        |
| Storage   | 128 GB  | 0        | 2        |


✅ Step 4: Infer Acceptable and Unacceptable Levels
Acceptable Levels (appeared in accepted concepts at least once):
Brand: Apple

Price: $699, $1099

Camera: Triple, Quad

Storage: 256 GB

Unacceptable Levels (only appeared in rejected concepts ≥ 2 times or once with high confidence):
Brand: Samsung, OnePlus

Camera: Dual

Storage: 128 GB

🎯 Step 5: Use These for Choice Tournament
From now on:
Only generate profiles using acceptable levels

Exclude all unacceptable levels from the design

E.g., possible tournament profiles:

| Brand | Price  | Camera | Storage |
| ----- | ------ | ------ | ------- |
| Apple | \$699  | Triple | 256 GB  |
| Apple | \$1099 | Quad   | 256 GB  |


No more Samsung, OnePlus, Dual Cameras, or 128 GB storage in any tasks for this respondent.












