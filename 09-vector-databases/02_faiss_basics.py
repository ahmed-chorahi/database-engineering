"""Part B: FAISS basics. Random vectors first, so we see the mechanics."""
import numpy as np, faiss

d = 64                                    # dimension of each vector
rng = np.random.default_rng(42)
data = rng.random((10_000, d)).astype("float32")   # FAISS wants float32!
query = data[:1] + 0.01                            # a slightly changed copy of vector 0

# --- L2 (Euclidean) distance: smaller = closer
index = faiss.IndexFlatL2(d)
index.add(data)
print("vectors in index:", index.ntotal)

D, I = index.search(query, 3)             # top-3
print("L2  ids:", I[0], "distances:", D[0].round(3))

# --- Inner product: bigger = closer. Normalise vectors -> inner product == cosine similarity
norm_data = data.copy();  faiss.normalize_L2(norm_data)
norm_q    = query.copy(); faiss.normalize_L2(norm_q)
ip = faiss.IndexFlatIP(d)
ip.add(norm_data)
D, I = ip.search(norm_q, 3)
print("IP  ids:", I[0], "scores:   ", D[0].round(3))

# --- Save / load
faiss.write_index(index, "demo.index")
loaded = faiss.read_index("demo.index")
print("reloaded:", loaded.ntotal, "vectors")

# --- Approximate search (IVF): cluster first, only search nearby clusters. Faster on big data.
nlist = 100
quant = faiss.IndexFlatL2(d)
ivf = faiss.IndexIVFFlat(quant, d, nlist)
ivf.train(data)                           # learn the clusters
ivf.add(data)
ivf.nprobe = 5                            # how many clusters to check (speed vs accuracy)
D, I = ivf.search(query, 3)
print("IVF ids:", I[0], "(approximate)")
