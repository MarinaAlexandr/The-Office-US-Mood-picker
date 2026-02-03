# 🎬 The Office (US) - Mood Picker

A lightweight recommendation app that helps you find the right *The Office (US)* episode based on user-selected moods and viewing preferences.

Sometimes picking an episode takes longer than watching one.  
This app is designed to make that choice quick, intuitive, and enjoyable.

---

## 🛠️ Tech stack

* `Python`
* `Streamlit`
* Rule-based recommendation system

### Data preparation (offline)
* `pandas` — data cleaning and preprocessing
* `scikit-learn` — TF-IDF and cosine similarity for mood inference
* `kagglehub` — dataset ingestion

---

## 🌟 Features

* **Select one or more mood**: Choose between the different options such as chaos, romantic, cringe or comfort.
* **Adjust preferences**:
    - Avoid high-cringe episodes.
    - Require all moods to match (an AND logic).
    - Choose how many recommendations to display.
- **"Choose for me” random episode picker**: If you can’t decide, let the app randomly select an episode for you.
  
---

## 🧠 How it works? 

The app relies on a transparent recommendation approach. Episode data is enriched offline using keyword-based rules and TF-IDF similarity, while recommendations are generated at runtime through a lightweight, rule-based scoring logic.

### Data enrichment

Before the app runs, episode data is collected and enriched through an offline preprocessing pipeline:
- Episode metadata is loaded from a public dataset using **kagglehub** (https://www.kaggle.com/datasets/nehaprabhavalkar/the-office-dataset)
- The data is cleaned and normalized using **pandas**
- Each episode is automatically tagged with one or more **moods** using a hybrid approach:
  - **Keyword matching** on episode descriptions.
  - **TF-IDF vectorization and cosine similarity** (scikit-learn) to infer moods when no keywords are found.
- For transparency, the source of each inferred mood (keyword, TF-IDF, or fallback) is stored alongside the episode.

The result of this step is a static JSON file containing enriched episode data, which is used by the app at runtime.

### Recommendation logic

When a user interacts with the app:
- One or more moods are selected.
- Optional preferences are applied (low-cringe filtering, AND/OR logic, number of results).
- Episodes are filtered based on mood overlap.
- Each candidate episode is scored using a **rule-based formula** that takes into account:
  - Number of matching moods.
  - Episode rating.
  - Optional penalty for high-cringe episodes.

The results are then ranked by score and the top episodes are displayed.

### Random selection

A **“Choose for me”** option allows users to receive a random episode matching their current filters.

Overall, the system is designed to remain lightweight, transparent, and easy to extend, while still providing meaningful and personalized recommendations.

---

## 💡 What did I learn?

- **Designing explainable recommendation systems**: How to balance simple, rule-based logic with enriched data, prioritizing transparency and user trust over complex models.

- **Separating offline data processing from runtime logic**: The importance of keeping data enrichment and feature extraction offline, while maintaining a lightweight and deterministic application at runtime.

- **Building and deploying user-facing data apps**: Hands-on experience designing an interactive UI, managing application state, and deploying a Streamlit app as a complete, end-to-end product.

---

## 📈 How can it be improved?

Some features that can be improved:

- **User profiles and favorites persistence**: Introduce lightweight user profiles to store favorites and preferences across sessions in a multi-user environment.

- **Richer episode metadata and visuals**: Add episode thumbnails, short quotes, or key scenes to improve visual engagement and browsing experience.

- **Mood weighting and intensity**: Allow users to indicate how strongly they want a specific mood, enabling more nuanced scoring and recommendations.

- **Extended recommendation logic**: Combine mood-based rules with episode similarity (e.g. TF-IDF–based episode-to-episode similarity) to suggest follow-up episodes once a recommendation is selected.

---






