import json
import random
from pathlib import Path
import streamlit as st
from recommender import recommend

st.set_page_config(page_title="The Office Mood Picker", layout="centered")

st.markdown(
    """
    <style>
    /* Tots els botons secondary */
    button[kind="secondary"] {
        background-color:rgb(233, 226, 210) !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
        box-shadow: none !important;
    }
    button[kind="secondary"]:hover {
        background-color:rgb(224, 132, 29) !important;
        color: #111827 !important;
        border: 1px solid #cbd5e1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Títol i descripció ---

st.title("The Office (US) - Mood Picker")
st.write("Select a vibe✨  and get episode recommendations.")

# --- 1) Cargar dataset ---
@st.cache_data
def load_episodes():
    p = Path("data/episodes_enriched.json")
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


episodes = load_episodes()

if episodes is None:
    st.error("No trobo data/episodes_enriched.json. Primer executa: python scripts/build_episodes.py")
    st.stop()

ALL_MOODS = sorted({m for ep in episodes for m in ep.get("moods", [])})

# Mood emoji

MOOD_EMOJI = {
    "chaos": "🌪️",
    "christmas": "🎄",
    "comfort": "🤗",
    "cringe": "😬",
    "romantic": "💕",
    "wholesome": "🤍",
    "workplace": "🏢",
}
def mood_label(m: str) -> str:
    return f"{MOOD_EMOJI.get(m, '✨')} {m}"

# compta quants episodis tenen cada mood
selected_moods = st.multiselect(
    "Moods:",
    ALL_MOODS,
    default=["comfort"] if "comfort" in ALL_MOODS else (ALL_MOODS[:1] if ALL_MOODS else []),
    format_func=mood_label
)

low_cringe = st.checkbox("Prefer low-cringe episodes", value=False)
max_results = st.slider("Number of recs", 3, 15, 8)

require_all = st.checkbox(
    "Require ALL selected moods",
    value=True
)

# --- 3) Recomanar / Random pick ---

# Estado para random pick

if "random_pick" not in st.session_state:
    st.session_state["random_pick"] = None

def filter_candidates(episodes, selected_moods, require_all):
    selected = {m.strip().lower() for m in selected_moods if m is not None}

    # Si no hay moods seleccionados, cualquier episodio es candidato
    if not selected:
        return episodes

    candidates = []
    for ep in episodes:
        ep_moods = {m.strip().lower() for m in ep.get("moods", []) if m is not None}

        if require_all:
            if selected.issubset(ep_moods):
                candidates.append(ep)
        else:
            if len(selected & ep_moods) > 0:
                candidates.append(ep)

    return candidates


#Botones

col1, col2 = st.columns([1, 1])

with col1:
    do_recommend = st.button("Recommend")

with col2:
    do_random = st.button("🎲 Choose for me", key="random_btn", type="secondary")


# --- Random pick ---
if do_random:
    candidates = filter_candidates(episodes, selected_moods, require_all)

    if not candidates:
        st.session_state["random_pick"] = None
        st.warning("No episodes match your filters. Try removing a mood or disable AND.")
    else:
        pick = random.choice(candidates)

        # Normaliza para calcular matches bien
        selected_norm = {m.strip().lower() for m in selected_moods if m is not None}
        pick_norm = {m.strip().lower() for m in pick.get("moods", []) if m is not None}
        pick_matches = sorted(list(selected_norm & pick_norm))

        pick = {
            **pick,
            "matches": pick_matches,
            "reason": ", ".join(pick_matches) if pick_matches else "Random pick"
        }

        st.session_state["random_pick"] = pick

# Mostrar random pick si existe
if st.session_state["random_pick"] is not None:
    ep = st.session_state["random_pick"]
    sources = ep.get("mood_sources", {})
    match_list = ep.get("matches", [])

    if match_list:
        why = " · ".join([f"{m} ({sources.get(m, 'unknown')})" for m in match_list])
    else:
        why = ep.get("reason", "Random pick")

    with st.container(border=True):
        st.markdown(f"### 🎲 S{ep['season']:02d}E{ep['episode']:02d} — {ep['title']}")
        emoji_line = " ".join(MOOD_EMOJI.get(m, "✨") for m in match_list)

        cols = st.columns([2, 1])
        with cols[0]:
            st.caption(f"{emoji_line}  \nWhy: {why}")
        with cols[1]:
            st.caption(f"⭐ Rating: {ep.get('rating', 0)}")

        about = ep.get("about") or ep.get("description") or ""
        if about.strip():
            with st.expander("Show synopsis"):
                st.write(about)

    st.divider()

# --- Recommend normal ---
if do_recommend:
    results = recommend(
        episodes,
        selected_moods,
        low_cringe=low_cringe,
        max_results=max_results,
        require_all=require_all
    )

    st.subheader("Recommendations:")

    if not results:
        if require_all and len(selected_moods) > 1:
            st.warning(
                "There are no episodes that match ALL selected moods. "
                "Try removing one mood or disable 'Require ALL selected moods'."
            )
        else:
            st.warning("No matches were found. Try other moods.")
    else:
        for ep in results:
            sources = ep.get("mood_sources", {})
            match_list = ep.get("matches", [])
            if match_list:
                why = " · ".join([f"{m} ({sources.get(m, 'unknown')})" for m in match_list])
            else:
                why = ep.get("reason", "General pick")

            with st.container(border=True):
                st.markdown(f"### S{ep['season']:02d}E{ep['episode']:02d} — {ep['title']}")

                emoji_line = " ".join(MOOD_EMOJI.get(m, "✨") for m in match_list)

                cols = st.columns([2, 1])
                with cols[0]:
                    st.caption(f"{emoji_line}  \nWhy: {why}")
                with cols[1]:
                    st.caption(f"⭐ Rating: {ep.get('rating', 0)}")

                about = ep.get("about") or ep.get("description") or ""
                if about.strip():
                    with st.expander("Show synopsis"):
                        st.write(about)
