import duckdb
from datetime import date

con = duckdb.connect('academia.duckdb')

# Tabela de alunos
con.execute('''
CREATE TABLE IF NOT EXISTS alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    data_nascimento DATE,
    sexo TEXT,
    faixa TEXT,
    peso REAL,
    categoria_idade TEXT,
    categoria_peso TEXT,
    endereco TEXT,
    foto_path TEXT,
    encoding BLOB
);
''')

# Tabela de categorias de idade (padrão IBJJF)
categorias_idade = [
    ("Infantil", 4, 15),
    ("Juvenil", 16, 17),
    ("Adulto", 18, 29),
    ("Master 1", 30, 35),
    ("Master 2", 36, 40),
    ("Master 3", 41, 45),
    ("Master 4", 46, 50),
    ("Master 5", 51, 55),
    ("Master 6", 56, 60),
    ("Master 7", 61, 120)
]
con.execute('''
CREATE TABLE IF NOT EXISTS categorias_idade (
    nome TEXT PRIMARY KEY,
    idade_min INTEGER,
    idade_max INTEGER
);
''')
con.execute('DELETE FROM categorias_idade;')
con.executemany('INSERT INTO categorias_idade VALUES (?, ?, ?);', categorias_idade)

# Tabela de categorias de peso (masculino adulto IBJJF)
categorias_peso = [
    ("Galo", 0, 57.5, "Masculino"),
    ("Pluma", 57.6, 64.0, "Masculino"),
    ("Pena", 64.1, 70.0, "Masculino"),
    ("Leve", 70.1, 76.0, "Masculino"),
    ("Médio", 76.1, 82.3, "Masculino"),
    ("Meio-Pesado", 82.4, 88.3, "Masculino"),
    ("Pesado", 88.4, 94.3, "Masculino"),
    ("Super-Pesado", 94.4, 100.5, "Masculino"),
    ("Pesadíssimo", 100.6, 999.0, "Masculino"),
    ("Galo", 0, 48.5, "Feminino"),
    ("Pluma", 48.6, 53.5, "Feminino"),
    ("Pena", 53.6, 58.5, "Feminino"),
    ("Leve", 58.6, 64.0, "Feminino"),
    ("Médio", 64.1, 69.0, "Feminino"),
    ("Meio-Pesado", 69.1, 74.0, "Feminino"),
    ("Pesado", 74.1, 79.3, "Feminino"),
    ("Super-Pesado", 79.4, 999.0, "Feminino")
]
con.execute('''
CREATE TABLE IF NOT EXISTS categorias_peso (
    nome TEXT,
    peso_min REAL,
    peso_max REAL,
    sexo TEXT
);
''')
con.execute('DELETE FROM categorias_peso;')
con.executemany('INSERT INTO categorias_peso VALUES (?, ?, ?, ?);', categorias_peso)

con.close()
print("Banco de dados inicializado com sucesso!")
