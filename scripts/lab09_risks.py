"""LAB09, paso 8: cuantificar riesgos del recomendador híbrido.

scripts/lab09_risks.py y ejecutar con:
    uv run python scripts/lab09_risks.py                      # configuración elegida: 10 factores, 12 épocas
    uv run python scripts/lab09_risks.py --factors 40 --epochs 12

Mide: popularidad dominante, burbuja de filtro, sesgo de selección y desempeño por nivel de actividad
(el dataset no tiene demografía; la actividad es solo un indicador de heterogeneidad, no de grupos poblacionales).
Salida: reports/risks_metrics.json
"""
from __future__ import annotations

import argparse
import json
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from inf8239_u03.config import MOVIELENS_DIR, ROOT
from inf8239_u03.data import load_movielens
from inf8239_u03.metrics import catalog_coverage, hit_rate_at_k
from inf8239_u03.recommenders import MatrixFactorization, temporal_leave_one_out

parser = argparse.ArgumentParser()
parser.add_argument("--factors", type=int, default=10)
parser.add_argument("--epochs", type=int, default=12)
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--alphas", type=float, nargs="+", default=[0.25, 0.75])
args = parser.parse_args()

ratings, movies = load_movielens(MOVIELENS_DIR)
train, test = temporal_leave_one_out(ratings)
model = MatrixFactorization(factors=args.factors, seed=args.seed).fit(train, epochs=args.epochs)
evaluable = test[test["userId"].isin(model.user_index) & test["movieId"].isin(model.item_index)]
seen_by_user = train.groupby("userId")["movieId"].apply(set).to_dict()

movie_table = movies.reset_index(drop=True).copy()
movie_table["genres_text"] = movie_table["genres"].str.replace("|", " ", regex=False)
genre_matrix = TfidfVectorizer().fit_transform(movie_table["genres_text"])
movie_row = {int(m): i for i, m in enumerate(movie_table["movieId"])}
genre_sets = {
    int(r.movieId): {g for g in r.genres.split("|") if g != "(no genres listed)"} for r in movies.itertuples()
}

# Popularidad en entrenamiento
counts = train.groupby("movieId").size().reindex(model.items).fillna(0)
pop_pct = counts.rank(pct=True)                      # percentil de popularidad (1.0 = más popular)
head_items = set(counts.nlargest(int(0.2 * len(counts))).index)   # 20 % de ítems más valorados


def fast_top_n(user_id: int, seen: set, k: int) -> pd.DataFrame:
    items = np.asarray(model.items)
    scores = model.global_mean + model.item_factors @ model.user_factors[model.user_index[user_id]]
    keep = ~np.isin(items, list(seen))
    cand, sc = items[keep], scores[keep]
    order = sc.argsort()[::-1][:k]
    return pd.DataFrame({"movieId": cand[order], "collaborative_score": sc[order]})


def recommend(alpha: float) -> dict[int, list[int]]:
    recs = {}
    for user_id in evaluable["userId"].unique():
        collab = fast_top_n(user_id, seen_by_user[user_id], 100)
        span = max(collab["collaborative_score"].max() - collab["collaborative_score"].min(), 1e-9)
        collab["normalized"] = (collab["collaborative_score"] - collab["collaborative_score"].min()) / span
        hist = train.loc[train["userId"].eq(user_id) & train["movieId"].isin(movie_row), ["movieId", "rating"]]
        rows = [movie_row[int(i)] for i in hist["movieId"]]
        w = np.clip(hist["rating"].to_numpy() - 2.5, 0.1, None)
        profile = genre_matrix[rows].multiply(w[:, None]).sum(axis=0) / w.sum()
        cand = [movie_row[int(i)] for i in collab["movieId"]]
        cs = cosine_similarity(profile.A, genre_matrix[cand].toarray()).ravel()
        collab["content"] = (cs - cs.min()) / max(cs.max() - cs.min(), 1e-9)
        collab["hybrid"] = alpha * collab["normalized"] + (1 - alpha) * collab["content"]
        recs[int(user_id)] = collab.nlargest(10, "hybrid")["movieId"].astype(int).tolist()
    return recs


def gini(values: np.ndarray) -> float:
    v = np.sort(values.astype(float))
    n = len(v)
    return float((2 * np.arange(1, n + 1) - n - 1).dot(v) / (n * v.sum())) if v.sum() > 0 else 0.0


def ild(item_ids: list[int]) -> float:
    rows = [movie_row[i] for i in item_ids if i in movie_row]
    if len(rows) < 2:
        return float("nan")
    sim = cosine_similarity(genre_matrix[rows])
    n = len(rows)
    return float(1 - (sim.sum() - n) / (n * (n - 1)))


rng = np.random.default_rng(args.seed)
hist_pct = np.mean([pop_pct.reindex(list(seen_by_user[u])).mean() for u in evaluable["userId"].unique()])
activity = train.groupby("userId").size()
tercile = pd.qcut(activity.rank(method="first"), 3, labels=["baja", "media", "alta"])

report: dict = {"config": vars(args), "n_usuarios_evaluables": int(len(evaluable)), "n_items_catalogo": len(model.items)}
for alpha in args.alphas:
    recs = recommend(alpha)
    slots = Counter(item for values in recs.values() for item in values)
    total = sum(slots.values())
    exposure = np.array([slots.get(i, 0) for i in model.items])
    n_genres_rec, n_genres_hist, ild_rec, ild_hist = [], [], [], []
    for user_id, items in recs.items():
        n_genres_rec.append(len(set().union(*(genre_sets.get(i, set()) for i in items))))
        hist_items = list(seen_by_user[user_id])
        n_genres_hist.append(len(set().union(*(genre_sets.get(i, set()) for i in hist_items))))
        ild_rec.append(ild(items))
        sample = rng.choice(hist_items, size=min(10, len(hist_items)), replace=False).tolist()
        ild_hist.append(ild(sample))
    hit_by_activity = {}
    for level in ["baja", "media", "alta"]:
        users = set(tercile[tercile == level].index)
        sub = evaluable[evaluable["userId"].isin(users)]
        hit_by_activity[level] = {"usuarios": int(len(sub)), "hit_rate_at_10": hit_rate_at_k(recs, sub, 10)}
    report[f"alpha_{alpha}"] = {
        "hit_rate_at_10": hit_rate_at_k(recs, evaluable, 10),
        "cobertura_catalogo": catalog_coverage(recs, len(model.items)),
        "items_distintos_recomendados": len(slots),
        "cuota_10_items_mas_recomendados": sum(c for _, c in slots.most_common(10)) / total,
        "gini_exposicion": gini(exposure),
        "cuota_recs_en_cabeza_20pct": sum(c for i, c in slots.items() if i in head_items) / total,
        "percentil_popularidad_recomendados": float(sum(pop_pct[i] * c for i, c in slots.items()) / total),
        "percentil_popularidad_historial": float(hist_pct),
        "generos_distintos_top10_media": float(np.mean(n_genres_rec)),
        "generos_distintos_historial_media": float(np.mean(n_genres_hist)),
        "diversidad_intralista_top10": float(np.nanmean(ild_rec)),
        "diversidad_intralista_historial_10": float(np.nanmean(ild_hist)),
        "hit_rate_por_actividad": hit_by_activity,
        "top5_items_mas_recomendados": [(int(i), c) for i, c in slots.most_common(5)],
    }

# Sesgo de selección (independiente de alpha)
density = len(train) / (train["userId"].nunique() * train["movieId"].nunique())
is_head = train["movieId"].isin(head_items)
report["sesgo_seleccion"] = {
    "densidad_matriz": float(density),
    "cuota_valoraciones_en_cabeza_20pct": float(is_head.mean()),
    "media_rating_cabeza": float(train.loc[is_head, "rating"].mean()),
    "media_rating_cola": float(train.loc[~is_head, "rating"].mean()),
    "items_con_menos_de_5_valoraciones": float((counts < 5).mean()),
}
report["demografia"] = "no disponible en MovieLens Latest Small; no se evalúan grupos poblacionales"

(ROOT / "reports").mkdir(exist_ok=True)
(ROOT / "reports/risks_metrics.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
