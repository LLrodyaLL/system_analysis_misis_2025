from typing import List, Tuple


def main(s: str, e: str) -> Tuple[
    List[List[bool]],
    List[List[bool]],
    List[List[bool]],
    List[List[bool]],
    List[List[bool]]
]:
    # 1. Парсим csv-строку
    edges = [tuple(map(int, line.split(','))) for line in s.strip().split('\n')]
    nodes = sorted({x for edge in edges for x in edge})
    n = len(nodes)
    idx = {node: i for i, node in enumerate(nodes)}

    # 2. Матрица r1 (непосредственное управление)
    r1 = [[False] * n for _ in range(n)]
    for u, v in edges:
        r1[idx[u]][idx[v]] = True

    # 3. Матрица r2 (непосредственное подчинение)
    r2 = [[r1[j][i] for j in range(n)] for i in range(n)]

    # 4. Матрица транзитивного замыкания (для r3, r4)
    # Используем алгоритм Флойда-Уоршелла
    closure = [[r1[i][j] for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                closure[i][j] = closure[i][j] or (closure[i][k] and closure[k][j])

    # 5. Матрица r3 (опосредованное управление)
    r3 = [[closure[i][j] and not r1[i][j] and i != j for j in range(n)] for i in range(n)]

    # 6. Матрица r4 (опосредованное подчинение)
    r4 = [[r3[j][i] for j in range(n)] for i in range(n)]

    # 7. Матрица r5 (соподчинение — один родитель)
    parent = {node: None for node in nodes}
    for u, v in edges:
        parent[v] = u
    r5 = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and parent[nodes[i]] is not None and parent[nodes[i]] == parent[nodes[j]]:
                r5[i][j] = True

    return (r1, r2, r3, r4, r5)


if __name__ == "__main__":
    s = "1,2\n1,3\n3,4\n3,5\n5,6\n6,7"
    e = "1"
    res = main(s, e)
    for i, r in enumerate(res, start=1):
        print(f"r{i}:")
        for row in r:
            print(row)
        print()


# Пример входного файла:
# ---
# 1	2
# 1	3
# 3	4
# 3	5

# Пример результата работы:
# ---
# r1:
# [False, True, True, False, False, False, False]
# [False, False, False, False, False, False, False]
# [False, False, False, True, True, False, False]
# [False, False, False, False, False, False, False]
# [False, False, False, False, False, True, False]
# [False, False, False, False, False, False, True]
# [False, False, False, False, False, False, False]
#
# r2:
# [False, False, False, False, False, False, False]
# [True, False, False, False, False, False, False]
# [True, False, False, False, False, False, False]
# [False, False, True, False, False, False, False]
# [False, False, True, False, False, False, False]
# [False, False, False, False, True, False, False]
# [False, False, False, False, False, True, False]
#
# r3:
# [False, False, False, True, True, True, True]
# [False, False, False, False, False, False, False]
# [False, False, False, False, False, True, True]
# [False, False, False, False, False, False, False]
# [False, False, False, False, False, False, True]
# [False, False, False, False, False, False, False]
# [False, False, False, False, False, False, False]
#
# r4:
# [False, False, False, False, False, False, False]
# [False, False, False, False, False, False, False]
# [False, False, False, False, False, False, False]
# [True, False, False, False, False, False, False]
# [True, False, False, False, False, False, False]
# [True, False, True, False, False, False, False]
# [True, False, True, False, True, False, False]
#
# r5:
# [False, False, False, False, False, False, False]
# [False, False, True, False, False, False, False]
# [False, True, False, False, False, False, False]
# [False, False, False, False, True, False, False]
# [False, False, False, True, False, False, False]
# [False, False, False, False, False, False, False]
# [False, False, False, False, False, False, False]
