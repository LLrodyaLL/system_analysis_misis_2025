import json
from typing import List, Dict, Any

def _normalize_ranking(data: Any) -> List[List[str]]:
    if isinstance(data, dict):
        if "ranking" in data:
            data = data["ranking"]
        elif "clusters" in data:
            data = data["clusters"]
        else:
            raise ValueError("Unsupported dict format for ranking")

    if not isinstance(data, list):
        raise ValueError("Ranking must be list or dict with key 'ranking'/'clusters'")

    clusters: List[List[str]] = []

    for elem in data:
        if isinstance(elem, (list, tuple)):
            if not elem:
                continue
            clusters.append([str(x) for x in elem])
        else:
            clusters.append([str(elem)])

    if not clusters:
        raise ValueError("Empty ranking")

    return clusters


def _build_positions(ranking: List[List[str]]) -> Dict[str, int]:
    pos: Dict[str, int] = {}
    for idx, cluster in enumerate(ranking):
        for label in cluster:
            if label in pos:
                raise ValueError(f"Duplicate object label in ranking: {label}")
            pos[label] = idx
    return pos


def _sorted_labels(labels) -> List[str]:
    def key_fn(x: str):
        try:
            return (0, int(x))
        except (ValueError, TypeError):
            return (1, str(x))

    return sorted(labels, key=key_fn)


def main(json_ranking_a: str, json_ranking_b: str) -> str:
    data_a = json.loads(json_ranking_a)
    data_b = json.loads(json_ranking_b)

    ranking_a = _normalize_ranking(data_a)
    ranking_b = _normalize_ranking(data_b)

    # Строим множество объектов
    labels_a = {label for cluster in ranking_a for label in cluster}
    labels_b = {label for cluster in ranking_b for label in cluster}

    if labels_a != labels_b:
        raise ValueError(
            f"Rankings must be defined on the same set of objects. "
            f"Got A={labels_a}, B={labels_b}"
        )

    labels = _sorted_labels(labels_a)

    # Позиции объектов (номер кластера слева направо)
    pos_a = _build_positions(ranking_a)
    pos_b = _build_positions(ranking_b)

    contradictions: List[List[str]] = []

    # Просматриваем все неупорядоченные пары объектов {i, j}
    n = len(labels)
    for i_idx in range(n):
        for j_idx in range(i_idx + 1, n):
            i = labels[i_idx]
            j = labels[j_idx]

            # Сравнение в ранжировке A
            # -1: i левее j (хуже)
            #  0: i и j в одном кластере (неразличимы)
            #  1: i правее j (лучше)
            a_cmp = (pos_a[i] > pos_a[j]) - (pos_a[i] < pos_a[j])

            # Сравнение в ранжировке B
            b_cmp = (pos_b[i] > pos_b[j]) - (pos_b[i] < pos_b[j])

            # Противоречие только если строгие порядки противоположны:
            # в одной ранжировке i лучше j, а в другой — j лучше i.
            if a_cmp * b_cmp == -1:
                contradictions.append([i, j])

    # Возвращаем JSON-строку
    return json.dumps(contradictions, ensure_ascii=False)


if __name__ == "__main__":
    # Пример:
    # A = [x1, {x2, x3}, x4, {x5, x6, x7}, x8, x9, x10]
    # B = [x3, {x1, x4}, x2, x6, {x5, x7, x8}, {x9, x10}]
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

    print(main(ranking_a, ranking_b))
    # Ожидаемый результат ядра противоречий:
    # [["1","3"],["2","4"]]
