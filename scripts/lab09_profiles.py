"""LAB09, paso 6: evaluar tres perfiles (historial amplio, pequeño y usuario nuevo).

"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from inf8239_u03.config import MOVIELENS_DIR, ROOT
from inf8239_u03.data import load_movielens
from inf8239_u03.recommenders import MatrixFactorization, temporal_leave_one_out

parser = argparse.ArgumentParser()
parser.add_argument("--factors", type=int, default=20)
parser.add_argument("--epochs", type=int, default=12)
args = parser.parse_args()

ratings, movies = load_movielens(MOVIELENS_DIR)
train, test = temporal_leave_one_out(ratings)
model = MatrixFactorization(factors=args.factors).fit(train, epochs=args.epochs)

movie_table = movies.reset_index(drop=True).copy()
movie_table["genres_text"] = movie_table["genres"].str.replace("|", " ", regex=False)
genre_matrix = TfidfVectorizer().fit_transform(movie_table["genres_text"])
movie_row = {int(m): i for i, m in enumerate(movie_table["movieId"])}
titles = movies.set_index("movieId")["title"].to_dict()

counts = train.groupby("userId").size()
counts = counts[counts.index.isin(model.user_index)].sort_values()


def hybrid_top10(user_id: int, alpha: float) -> list[int]:
    seen = set(train.loc[train["userId"].eq(user_id), "movieId"])
    collab = model.top_n(user_id, seen, 100)
    rng = max(collab["collaborative_score"].max() - collab["collaborative_score"].min(), 1e-9)
    collab["normalized"] = (collab["collaborative_score"] - collab["collaborative_score"].min()) / rng
    hist = train.loc[train["userId"].eq(user_id) & train["movieId"].isin(movie_row), ["movieId", "rating"]]
    rows = [movie_row[int(i)] for i in hist["movieId"]]
    w = np.clip(hist["rating"].to_numpy() - 2.5, 0.1, None)
    profile = genre_matrix[rows].multiply(w[:, None]).sum(axis=0) / w.sum()
    cand = [movie_row[int(i)] for i in collab["movieId"]]
    cs = cosine_similarity(profile.A, genre_matrix[cand].toarray()).ravel()
    collab["content"] = (cs - cs.min()) / max(cs.max() - cs.min(), 1e-9)
    collab["hybrid"] = alpha * collab["normalized"] + (1 - alpha) * collab["content"]
    return collab.nlargest(10, "hybrid")["movieId"].astype(int).tolist()


profiles = {
    "amplio": int(counts.index[-1]),   # mayor historial en entrenamiento
    "pequeño": int(counts.index[0]),   # menor historial en entrenamiento
}
rows_out = []

for name, uid in profiles.items():
    seen = set(train.loc[train["userId"].eq(uid), "movieId"])
    low, high = hybrid_top10(uid, 0.25), hybrid_top10(uid, 0.75)
    overlap = len(set(low) & set(high))
    print(f"\n=== Perfil {name} | userId={uid} | valoraciones en train={len(seen)} ===")
    print("¿Excluye ítems vistos (alpha 0.25 y 0.75)?:", not (seen & set(low)) and not (seen & set(high)))
    print(f"Coincidencia Top-10 entre alpha=0.25 y alpha=0.75: {overlap}/10")
    for a, recs in (("0.25", low), ("0.75", high)):
        print(f"\nTop-10 alpha={a}")
        for rank, m in enumerate(recs, 1):
            print(f"  {rank:>2}. {titles.get(m, m)}")
            rows_out.append({"perfil": name, "userId": uid, "alpha": a, "rank": rank,
                             "movieId": m, "title": titles.get(m, ""), "personalizada": True})

# Usuario nuevo: userId inexistente en entrenamiento -> fallback de popularidad (igual a lab09_hybrid.py)
new_id = int(ratings["userId"].max()) + 1
assert new_id not in model.user_index
pop = train.groupby("movieId")["rating"].agg(["mean", "count"]).sort_values(["count", "mean"], ascending=False)
fallback = pop.index[:10].tolist()
print(f"\n=== Perfil nuevo | userId={new_id} (no está en el entrenamiento) ===")
print("Lista NO personalizada (fallback por popularidad: cantidad y media):")
for rank, m in enumerate(fallback, 1):
    print(f"  {rank:>2}. {titles.get(m, m)}")
    rows_out.append({"perfil": "nuevo", "userId": new_id, "alpha": "n/a", "rank": rank,
                     "movieId": int(m), "title": titles.get(m, ""), "personalizada": False})

(ROOT / "reports").mkdir(exist_ok=True)
pd.DataFrame(rows_out).to_csv(ROOT / "reports/profiles_check.csv", index=False)
print("\nGuardado: reports/profiles_check.csv")
