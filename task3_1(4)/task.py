import json
import numpy as np

def _normalize_ranking(data):
    if isinstance(data, dict):
        if "ranking" in data:
            data = data["ranking"]
        elif "clusters" in data:
            data = data["clusters"]
        else:
            raise ValueError("Invalid JSON structure: expected 'ranking' or 'clusters'")

    clusters = []
    for x in data:
        if isinstance(x, (list, tuple)):
            clusters.append([str(e) for e in x])
        else:
            clusters.append([str(x)])
    return clusters


def _all_labels(ranking):
    return sorted({e for cluster in ranking for e in cluster}, key=lambda x: int(x) if x.isdigit() else x)


def _relation_matrix(ranking, labels):
    n = len(labels)
    pos = {obj: idx for idx, cluster in enumerate(ranking) for obj in cluster}
    Y = np.zeros((n, n), dtype=int)
    for i, a in enumerate(labels):
        for j, b in enumerate(labels):
            if pos[a] <= pos[b]:  
                Y[i, j] = 1
    return Y


def _kernel_of_contradictions(YA, YB, labels):
    YA_t = YA.T
    YB_t = YB.T
    P = (YA * YB_t) | (YA_t * YB)
    contradictions = []
    n = len(labels)
    for i in range(n):
        for j in range(i + 1, n):
            if P[i, j] == 0 and P[j, i] == 0:
                contradictions.append([labels[i], labels[j]])
    return contradictions


def _warshall_closure(M):
    n = M.shape[0]
    closure = M.copy()
    for k in range(n):
        for i in range(n):
            for j in range(n):
                closure[i, j] = closure[i, j] or (closure[i, k] and closure[k, j])
    return closure


def _build_consistent_ranking(YA, YB, contradictions, labels):
    n = len(labels)
    C = YA & YB

    for i, j in ((labels.index(a), labels.index(b)) for a, b in contradictions):
        C[i, j] = C[j, i] = 1

    E = C & C.T

    E_star = _warshall_closure(E)

    visited = set()
    clusters = []
    for i in range(n):
        if i not in visited:
            cluster = [labels[j] for j in range(n) if E_star[i, j] and E_star[j, i]]
            for j in range(n):
                if E_star[i, j] and E_star[j, i]:
                    visited.add(j)
            clusters.append(sorted(cluster, key=lambda x: int(x) if x.isdigit() else x))

    cluster_order = []
    for cluster in clusters:
        cluster_order.append(cluster)

    return cluster_order


def main(json_ranking_a: str, json_ranking_b: str, variant: int = 1) -> str:
    """
    Варианты:
      variant=1 — ядро противоречий
      variant=2 — согласованная кластерная ранжировка
    """
    data_a = json.loads(json_ranking_a)
    data_b = json.loads(json_ranking_b)

    ranking_a = _normalize_ranking(data_a)
    ranking_b = _normalize_ranking(data_b)

    labels = _all_labels(ranking_a)

    YA = _relation_matrix(ranking_a, labels)
    YB = _relation_matrix(ranking_b, labels)

    if variant == 1:
        contradictions = _kernel_of_contradictions(YA, YB, labels)
        return json.dumps(contradictions, ensure_ascii=False)
    elif variant == 2:
        contradictions = _kernel_of_contradictions(YA, YB, labels)
        clusters = _build_consistent_ranking(YA, YB, contradictions, labels)
        return json.dumps(clusters, ensure_ascii=False)
    else:
        raise ValueError("variant must be 1 or 2")


if __name__ == "__main__":
    ranking_a = json.dumps([
        ["1"],
        ["2", "3"],
        ["4"],
        ["5", "6", "7"],
        ["8"],
        ["9"],
        ["10"]
    ])
    ranking_b = json.dumps([
        ["3"],
        ["1", "4"],
        ["2"],
        ["6"],
        ["5", "7", "8"],
        ["9", "10"]
    ])

    print("Вариант 1 — ядро противоречий:")
    print(main(ranking_a, ranking_b, variant=1))

    print("\nВариант 2 — согласованная кластерная ранжировка:")
    print(main(ranking_a, ranking_b, variant=2))
