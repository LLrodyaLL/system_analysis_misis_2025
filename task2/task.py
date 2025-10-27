import math
from typing import Tuple, List, Dict, Set

def main(s: str, e: str) -> Tuple[float, float]:
    edges = []
    for line in s.strip().split('\n'):
        if line:
            parent, child = line.split(',')
            edges.append((parent.strip(), child.strip()))

    nodes = set()
    for parent, child in edges:
        nodes.add(parent)
        nodes.add(child)
    nodes = sorted(nodes)
    n = len(nodes)

    node_to_idx = {node: idx for idx, node in enumerate(nodes)}

    graph = {node: [] for node in nodes}
    for parent, child in edges:
        graph[parent].append(child)

    # 1. Непосредственное управление (r1)
    r1 = set(edges)

    # 2. Непосредственное подчинение (r2) - обратные рёбра
    r2 = set((child, parent) for parent, child in edges)

    # 3. Опосредованное управление (r3) - транзитивное замыкание вниз
    def get_descendants(node):
        descendants = set()
        stack = [node]
        while stack:
            current = stack.pop()
            for child in graph.get(current, []):
                if child not in descendants:
                    descendants.add(child)
                    stack.append(child)
        return descendants

    r3 = set()
    for node in nodes:
        descendants = get_descendants(node)
        for desc in descendants:
            if (node, desc) not in r1:
                r3.add((node, desc))

    # 4. Опосредованное подчинение (r4) - обратные к r3
    r4 = set((child, parent) for parent, child in r3)

    # 5. Сотрудничество на одном уровне (r5)
    def get_siblings(node, root=e):
        if node == root:
            return set()

        parent = None
        for p, c in edges:
            if c == node:
                parent = p
                break

        if not parent:
            return set()

        siblings = set(graph.get(parent, [])) - {node}
        return siblings

    r5 = set()
    for node in nodes:
        siblings = get_siblings(node, root=e)
        for sibling in siblings:
            r5.add((node, sibling))
            r5.add((sibling, node))

    relations = [r1, r2, r3, r4, r5]

    l_matrix = [[0] * len(relations) for _ in range(n)]

    for rel_idx, relation in enumerate(relations):
        for i, node in enumerate(nodes):
            outgoing = sum(1 for start, end in relation if start == node)
            l_matrix[i][rel_idx] = outgoing

    total_entropy = 0.0

    for i in range(n):
        for rel_idx in range(len(relations)):
            lij = l_matrix[i][rel_idx]
            if lij > 0:
                P = lij / (n - 1)
                H_partial = -P * math.log2(P)
                total_entropy += H_partial

    c = 1 / (math.e * math.log(2))
    H_ref = c * n * len(relations)

    normalized_complexity = total_entropy / H_ref if H_ref > 0 else 0

    return (round(total_entropy, 1), round(normalized_complexity, 1))


if __name__ == "__main__":
    csv_string = "1,2\n1,3\n3,4\n3,5"
    root = "1"

    entropy, complexity = main(csv_string, root)
    print(f"Энтропия: {entropy}")
    print(f"Нормированная сложность: {complexity}")
    
# Пример входного файла:
# ---
# 1	2
# 1	3
# 3	4
# 3	5
# 1

# Пример результата работы:
# Энтропия: 6.5
# Нормированная сложность: 0.5
