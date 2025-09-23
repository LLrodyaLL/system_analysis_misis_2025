import csv
from io import StringIO

def main():
    filename = input("Введите название CSV файла: ")
    
    try:
        with open(filename, 'r') as file:
            csv_content = file.read()
        
        csv_reader = csv.reader(StringIO(csv_content))
        edges = []
        for row in csv_reader:
            if len(row) >= 2:  
                edges.append((int(row[0]), int(row[1])))
        
        max_vertex = 0
        for u, v in edges:
            max_vertex = max(max_vertex, u, v)
        
        matrix_size = max_vertex
        adjacency_matrix = [[0] * matrix_size for _ in range(matrix_size)]
        
        for u, v in edges:
            adjacency_matrix[u-1][v-1] = 1
        
        return adjacency_matrix
    
    except FileNotFoundError:
        print(f"Файл '{filename}' не найден!")
        return []
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []

if __name__ == "__main__":
    result = main()
    if result:
        print("Матрица смежности:")
        for row in result:
            print(row)


# Пример входного файла:
# ---
# 1	2
# 1	3
# 3	4
# 3	5

# Пример результата работы:
# Матрица смежности:
# [0, 1, 1, 0, 0]
# [0, 0, 0, 0, 0]
# [0, 0, 0, 1, 1]
# [0, 0, 0, 0, 0]
# [0, 0, 0, 0, 0]
