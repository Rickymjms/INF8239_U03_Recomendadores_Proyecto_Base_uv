"""LAB09, paso 7: comparar costo y utilidad (tabla de Pareto y Green AI).

scripts/lab09_pareto.py y ejecutar con:
    uv run python scripts/lab09_pareto.py --quick          # 3 configuraciones, ruta rápida
    uv run python scripts/lab09_pareto.py                  # rejilla factores x épocas

Opciones: --factors 10 20 40  --epochs 6 12  --seeds 42 123 999  --alpha 0.75

Utilidad = HitRate@10. Costo = segundos de entrenamiento y tamaño del modelo (bytes).
"""
from __future__ import annotations
 
import argparse
import itertools
import pickle
import time
 
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import root_mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity
 
from inf8239_u03.config import MOVIELENS_DIR, ROOT
from inf8239_u03.data import load_movielens
from inf8239_u03.metrics import catalog_coverage, hit_rate_at_k
from inf8239_u03.recommenders import MatrixFactorization, temporal_leave_one_out
 
parser = argparse.ArgumentParser()
parser.add_argument("--quick", action="store_true", help="usa 3 configuraciones: (10,5), (20,12), (40,20)")
parser.add_argument("--factors", type=int, nargs="+", default=[10, 20, 40])
parser.add_argument("--epochs", type=int, nargs="+", default=[6, 12])
parser.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 999])
parser.add_argument("--alpha", type=float, default=0.75)
args = parser.parse_args()
 
if args.quick:
    configs = [(10, 5), (20, 12), (40, 20)]
else:
    configs = list(itertools.product(args.factors, args.epochs))
 
ratings, movies = load_movielens(MOVIELENS_DIR)
train, test = temporal_leave_one_out(ratings)
seen_by_user = train.groupby("userId")["movieId"].apply(set).to_dict()
 
# TF-IDF de géneros (señal de contenido de la híbrida)
movie_table = movies.reset_index(drop=True).copy()
movie_table["genres_text"] = movie_table["genres"].str.replace("|", " ", regex=False)
genre_matrix = TfidfVectorizer().fit_transform(movie_table["genres_text"])
movie_row = {int(m): i for i, m in enumerate(movie_table["movieId"])}
 
 
def fast_top_n(model, user_id: int, seen: set, k: int) -> pd.DataFrame:
    """Equivalente vectorizado de model.top_n (mismos candidatos, mismo orden)."""
    items = np.asarray(model.items)
    scores = model.global_mean + model.item_factors @ model.user_factors[model.user_index[user_id]]
    keep = ~np.isin(items, list(seen))
    cand, sc = items[keep], scores[keep]
    order = sc.argsort()[::-1][:k]
    return pd.DataFrame({"movieId": cand[order], "collaborative_score": sc[order]})
 
 
def evaluate(model, alpha: float, use_fast: bool) -> dict:
    evaluable = test[test["userId"].isin(model.user_index) & test["movieId"].isin(model.item_index)]
    preds = [model.predict(r.userId, r.movieId) for r in evaluable.itertuples()]
    rmse = root_mean_squared_error(evaluable["rating"], preds)
    top_n = fast_top_n if use_fast else (lambda m, u, s, k: m.top_n(u, s, k))
    recs = {}
    for user_id in evaluable["userId"].unique():
        seen = seen_by_user.get(user_id, set())
        collab = top_n(model, user_id, seen, 100)
        span = max(collab["collaborative_score"].max() - collab["collaborative_score"].min(), 1e-9)
        collab["normalized"] = (collab["collaborative_score"] - collab["collaborative_score"].min()) / span
        hist = train.loc[train["userId"].eq(user_id) & train["movieId"].isin(movie_row), ["movieId", "rating"]]
        if len(hist) > 0:
            rows = [movie_row[int(i)] for i in hist["movieId"]]
            w = np.clip(hist["rating"].to_numpy() - 2.5, 0.1, None)
            profile = genre_matrix[rows].multiply(w[:, None]).sum(axis=0) / w.sum()
            cand = [movie_row[int(i)] for i in collab["movieId"]]
            cs = cosine_similarity(profile.A, genre_matrix[cand].toarray()).ravel()
            collab["content"] = (cs - cs.min()) / max(cs.max() - cs.min(), 1e-9)
            collab["hybrid"] = alpha * collab["normalized"] + (1 - alpha) * collab["content"]
        else:
            collab["hybrid"] = collab["normalized"]
        recs[int(user_id)] = collab.nlargest(10, "hybrid")["movieId"].astype(int).tolist()
    return {
        "n_eval": len(evaluable),
        "rmse": float(rmse),
        "hit_rate_at_10": hit_rate_at_k(recs, evaluable, 10),
        "catalog_coverage": catalog_coverage(recs, len(model.items)),
    }
 
 
def model_size_bytes(model) -> int:
    try:
        return len(pickle.dumps(model))
    except Exception:
        return int(sum(v.nbytes for v in vars(model).values() if isinstance(v, np.ndarray)))
 
 
# --- Verificar que la evaluación rápida coincide con model.top_n ---------------
probe = MatrixFactorization(factors=configs[0][0], seed=args.seeds[0]).fit(train, epochs=1)
probe_users = list(probe.user_index)[:5]
use_fast = all(
    probe.top_n(u, seen_by_user.get(u, set()), 100)["movieId"].tolist()
    == fast_top_n(probe, u, seen_by_user.get(u, set()), 100)["movieId"].tolist()
    for u in probe_users
)
print("Evaluación vectorizada equivalente a model.top_n:", use_fast)
 
# --- Ejecutar configuraciones x semillas ---------------------------------------
runs = []
for (factors, epochs), seed in itertools.product(configs, args.seeds):
    start = time.perf_counter()
    model = MatrixFactorization(factors=factors, seed=seed).fit(train, epochs=epochs)  # semilla efectiva
    train_seconds = time.perf_counter() - start
    metrics = evaluate(model, args.alpha, use_fast)
    runs.append({"factors": factors, "epochs": epochs, "seed": seed, "alpha": args.alpha,
                 "train_seconds": train_seconds, "model_bytes": model_size_bytes(model), **metrics})
    print(f"f={factors:>3} e={epochs:>3} seed={seed:>4} | hit@10={metrics['hit_rate_at_10']:.4f} "
          f"rmse={metrics['rmse']:.4f} cov={metrics['catalog_coverage']:.4f} t={train_seconds:.1f}s")
 
runs_df = pd.DataFrame(runs)
(ROOT / "reports").mkdir(exist_ok=True)
runs_df.to_csv(ROOT / "reports/pareto_runs.csv", index=False)
 
# --- Resumen por configuración -------------------------------------------------
summary = runs_df.groupby(["factors", "epochs"]).agg(
    hit_mean=("hit_rate_at_10", "mean"), hit_std=("hit_rate_at_10", "std"),
    rmse_mean=("rmse", "mean"), cov_mean=("catalog_coverage", "mean"),
    sec_mean=("train_seconds", "mean"), sec_min=("train_seconds", "min"), size_mean=("model_bytes", "mean"), n_eval=("n_eval", "first"),
).reset_index()
 
 
def is_dominated(i: int, time_col: str) -> bool:
    a = summary.loc[i]
    for j in summary.index:
        if j == i:
            continue
        b = summary.loc[j]
        no_worse = b.hit_mean >= a.hit_mean and b[time_col] <= a[time_col] and b.size_mean <= a.size_mean
        strictly = b.hit_mean > a.hit_mean or b[time_col] < a[time_col] or b.size_mean < a.size_mean
        if no_worse and strictly:
            return True
    return False
 
 
# Estricta (tiempo medio) y de sensibilidad (tiempo mínimo, menos afectado por ruido de la máquina)
summary["dominada"] = [is_dominated(i, "sec_mean") for i in summary.index]
summary["dominada_t_min"] = [is_dominated(i, "sec_min") for i in summary.index]
summary = summary.sort_values("sec_mean").reset_index(drop=True)
 
# Error estándar binomial de HitRate (incertidumbre por tener pocos usuarios evaluables)
summary["hit_se"] = np.sqrt(summary["hit_mean"] * (1 - summary["hit_mean"]) / summary["n_eval"])
base = summary.iloc[0]
summary["delta_hit_vs_barata"] = summary["hit_mean"] - base["hit_mean"]
summary["delta_seg_vs_barata"] = summary["sec_mean"] - base["sec_mean"]
summary["delta_kb_vs_barata"] = (summary["size_mean"] - base["size_mean"]) / 1024
se_diff = np.sqrt(summary["hit_se"] ** 2 + base["hit_se"] ** 2)
summary["mejora_vs_ruido"] = np.where(summary["delta_hit_vs_barata"] > 2 * se_diff, "supera 2 EE", "dentro del ruido")
summary.loc[0, "mejora_vs_ruido"] = "referencia"
 
# Candidata Green AI (heurística): del frente (tiempo mínimo), la de menor tamaño y tiempo cuyo HitRate no es peor que el mejor menos 1 EE
front = summary[~summary["dominada_t_min"]]
best = front.loc[front["hit_mean"].idxmax()]
candidate = front[front["hit_mean"] >= best["hit_mean"] - best["hit_se"]].sort_values(["size_mean", "sec_mean"]).iloc[0]
summary["candidata_green_ai"] = (summary["factors"].eq(candidate["factors"]) & summary["epochs"].eq(candidate["epochs"]))
 
summary.to_csv(ROOT / "reports/pareto_table.csv", index=False)
 
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", None)
print("\n=== Tabla costo-utilidad (media de semillas; dominada=True se descarta) ===")
print(summary.round(4).to_string(index=False))
print(f"\nCandidata Green AI (heurística, justifíquela con la tabla): "
      f"factors={int(candidate['factors'])}, epochs={int(candidate['epochs'])}")
print("Guardado: reports/pareto_runs.csv y reports/pareto_table.csv")