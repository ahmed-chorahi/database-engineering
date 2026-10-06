"""Part A: similarity from scratch with NumPy. No libraries hiding anything."""
import numpy as np

# Pretend these are 3-dimensional "embeddings" (real ones have 384-1536 dimensions)
cat    = np.array([0.9, 0.1, 0.0])
kitten = np.array([0.8, 0.2, 0.1])
car    = np.array([0.0, 0.2, 0.9])

def dot(a, b):        return float(np.sum(a * b))
def euclidean(a, b):  return float(np.sqrt(np.sum((a - b) ** 2)))
def cosine(a, b):     return dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print(f"{'pair':<14}{'dot':>8}{'euclid':>9}{'cosine':>9}")
for name, (a, b) in {"cat-kitten": (cat, kitten), "cat-car": (cat, car)}.items():
    print(f"{name:<14}{dot(a,b):>8.3f}{euclidean(a,b):>9.3f}{cosine(a,b):>9.3f}")

# Nearest-neighbour search by brute force: compare the query to EVERY vector
vectors = np.vstack([cat, kitten, car])
labels  = ["cat", "kitten", "car"]
query   = np.array([0.85, 0.15, 0.05])           # "something catty"

scores = [cosine(query, v) for v in vectors]
order  = np.argsort(scores)[::-1]                # highest similarity first
print("\nquery ->", [(labels[i], round(float(scores[i]), 3)) for i in order])
