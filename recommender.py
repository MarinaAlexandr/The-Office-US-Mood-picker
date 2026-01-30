def recommend(episodes, selected_moods, low_cringe=False, max_results=8, require_all=True):
    selected = {m.strip().lower() for m in selected_moods if m is not None}

    if not selected:
        return []

    results = []
    for ep in episodes:
        ep_moods = {m.strip().lower() for m in ep.get("moods", []) if m is not None}

        # AND estricte
        if require_all and not selected.issubset(ep_moods):
            continue

        # Si NO AND (OR), com a mínim 1 coincidència
        if not require_all and len(selected & ep_moods) == 0:
            continue

        matches = sorted(list(selected & ep_moods))

        rating = ep.get("rating") or 0
        cringe = ep.get("cringe") or 0

        score = (len(matches) * 10) + float(rating) - (cringe * 3 if low_cringe else 0)

        results.append({
            **ep,
            "score": score,
            "matches": matches,
            "reason": ", ".join(matches) if matches else "General pick",
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_results]
