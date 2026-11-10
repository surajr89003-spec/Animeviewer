import pickle
import numpy as np

K = 50
with open("anime_similarity.pkl", "rb") as f:
    sim = pickle.load(f)

n = len(sim)
idx = np.zeros((n, K), dtype=np.int32)
val = np.zeros((n, K), dtype=np.float32)
for i in range(n):
    row = np.asarray(sim[i])
    top = np.argpartition(-row, K)[:K]
    idx[i] = top
    val[i] = row[top]

np.savez_compressed("anime_similarity_topk.npz", idx=idx, val=val)
print("done", n)