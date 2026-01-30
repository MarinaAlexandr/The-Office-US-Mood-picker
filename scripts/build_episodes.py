import json
from pathlib import Path

import pandas as pd
import kagglehub
from kagglehub import KaggleDatasetAdapter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


OUT_JSON = Path("data/episodes_enriched.json")

# 1) Moods i "definicions" (serveixen per TF-IDF)
MOOD_DESCRIPTIONS = {
    "romantic": "romance relationship couple dating date kiss proposal wedding boyfriend girlfriend valentine",
    "christmas": "christmas xmas santa christmas party snow",
    "chaos": "chaos panic disaster accident fire fight crisis stress",
    "cringe": "awkward embarrassing inappropriate uncomfortable humiliation",
    "workplace": "office meeting boss manager hr sales branch employee",
    "comfort": "comfort cozy fun supportive friends party lighthearted",
    "wholesome": "wholesome kind caring supportive gratitude help together",
}

# 2) Keywords (alta precisió)
MOOD_KEYWORDS = {
    "christmas": ["christmas", "xmas", "santa", "snow"],
    "romantic": ["date", "love", "wedding", "valentine", "proposal", "kiss", "couple", "boyfriend", "girlfriend","seeks comfort", "breakup", "break up", "marriage", "crush"],
    "chaos": ["fire", "panic", "fight", "disaster", "stress", "accident", "injury", "police"],
    "cringe": ["awkward", "embarrass", "inappropriate", "humiliate", "uncomfortable"],
    "workplace": ["office", "meeting", "sales", "manager", "branch", "boss", "employee", "hr"],
    "comfort": ["party", "friend", "family", "support", "together", "fun", "celebrate"],
    "wholesome": ["kind", "care", "support", "together", "help", "thank"],
}


def infer_moods_keywords(text: str) -> list[str]:
    if not isinstance(text, str):
        return []
    t = text.lower()
    moods = []
    for mood, kws in MOOD_KEYWORDS.items():
        if any(kw in t for kw in kws):
            moods.append(mood)
    return sorted(set(moods))


def infer_moods_tfidf(texts: list[str], top_k: int = 2, min_sim: float = 0.12) -> list[list[tuple[str, float]]]:
    """
    Retorna per cada text una llista [(mood, score), ...] ordenada
    """
    moods = list(MOOD_DESCRIPTIONS.keys())
    mood_texts = [MOOD_DESCRIPTIONS[m] for m in moods]

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    X = vectorizer.fit_transform(texts + mood_texts)

    text_vecs = X[: len(texts)]
    mood_vecs = X[len(texts) :]

    sims = cosine_similarity(text_vecs, mood_vecs)

    out = []
    for i in range(sims.shape[0]):
        ranked = sorted(enumerate(sims[i]), key=lambda x: x[1], reverse=True)
        picked = []
        for j, s in ranked[:top_k]:
            if s >= min_sim:
                picked.append((moods[j], float(s)))
        out.append(picked)
    return out


def main():
    # Carrega dataset
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "nehaprabhavalkar/the-office-dataset",
        "the_office_series.csv"
    )

    # Normalitza i crea id + episode dins temporada
    df["Season"] = df["Season"].astype(int)
    df["id"] = df["Unnamed: 0"].astype(int)

    # (opcional però pro) ordena per data dins temporada si vols estabilitat
    df["DateParsed"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
    df = df.sort_values(["Season", "DateParsed", "id"]).reset_index(drop=True)

    df["EpisodeInSeason"] = df.groupby("Season").cumcount() + 1

    about_texts = df["About"].fillna("").astype(str).tolist()

    # Keywords
    kw_moods = [infer_moods_keywords(t) for t in about_texts]

    # TF-IDF (només com a suport)
    tfidf_ranked = infer_moods_tfidf(about_texts, top_k=2, min_sim=0.12)

    episodes = []
    for idx, r in df.iterrows():
        title = r.get("EpisodeTitle") or "Untitled"
        about = r.get("About") or ""
        season = int(r.get("Season") or 0)
        ep_in_season = int(r.get("EpisodeInSeason") or 0)
        ep_id = int(r.get("id") or 0)

        rating = r.get("Ratings") or 0
        votes = r.get("Votes") or 0
        duration = r.get("Duration") or None
        date = r.get("Date") or None

        # 1) Keywords tenen prioritat absoluta
        moods = list(kw_moods[idx])
        sources = {m: "keyword" for m in moods}

        # 2) TF-IDF només si NO hi ha cap keyword
        if not moods:
            for m, score in tfidf_ranked[idx]:
                moods.append(m)
                sources[m] = f"tfidf:{score:.3f}"
                break  # només 1 mood semàntic
        
        # 3) Fallback final
        if not moods:
            moods = ["workplace"]
            sources["workplace"] = "default"

        episodes.append({
            "id": ep_id,  # 0..187
            "season": season,
            "episode": ep_in_season,  # 1..N dins temporada
            "title": title,
            "about": about,
            "rating": float(rating) if rating else 0,
            "votes": int(votes) if votes else 0,
            "duration": int(duration) if duration else None,
            "date": str(date) if date else None,
            "moods": sorted(set(moods)),
            "mood_sources": sources,  # per transparència
        })

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(episodes, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ Wrote {len(episodes)} episodes to {OUT_JSON}")


if __name__ == "__main__":
    main()
