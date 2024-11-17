import sqlite3
import random

# Listas para popular a tabela
first_name_list = [
    "Antônio", "Carlos", "Francisco", "João", "José", "Luís", "Luiz", "Pedro", "Mateus", "Miguel",
    "Alberto", "Roberto", "Ana", "Alice", "Maria", "Fátima", "Francisca", "Cora", "Mariana"
]
last_name_list = [
    "Almeida", "Souza", "Bernardes", "Neves", "Oliveira", "Silva", "Souza", "Lira", "Costa", "Moura",
    "Rodrigues", "Gomes", "Gonçalves", "Martins"
]
localization_list = [
    "Sorriso - MT", "São Miguel Arcanjo - SP", "Marialva - PR", "Jatobá - PI", "Ivinhema - MS",
    "Maués - AM", "Atibaia - SP", "Igarapé-Mirim - PA", "Piedade - SP", "Ituporanga - SC",
    "São Joaquim - SC", "Reserva - PR", "São Desidério - BA", "Uberaba - MG"
]
pesticide_list = [
    "2,4-D", "Metomil", "Clorpirifós", "Diazinona", "Acefato", "Atrazina", "Diuron", "Glifosato",
    "Melationa", "Mancozebe"
]


# Criar e popular a tabela farmers
def setup_database():
    with sqlite3.connect('pesticides.db') as conn:
        cursor = conn.cursor()

        # Criar a tabela farmers, agora incluindo fingerprint_path
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY,
            firstname TEXT,
            lastname TEXT,
            localization TEXT,
            pesticide TEXT,
            category TEXT,
            fingerprint_path TEXT  -- Nova coluna para armazenar o caminho da digital
        )""")

        # Popular a tabela
        populate(cursor)

        # Exibir os dados inseridos
        cursor.execute("SELECT * FROM farmers")
        print(cursor.fetchall())


def populate(cursor):
    farmers_data = []

    for i in range(121):
        firstname = random.choice(first_name_list)
        lastname = random.choice(last_name_list)
        localization = random.choice(localization_list)

        if i < 20:
            pesticide = pesticide_list[random.randint(0, 1)]
            category = "1"
        elif 20 < i < 61:
            pesticide = pesticide_list[random.randint(2, 3)]
            category = "2"
        else:
            pesticide = pesticide_list[random.randint(4, 9)]
            category = "3"

        farmers_data.append((i + 1, firstname, lastname, localization, pesticide, category))

    # Usar executemany para inserir todos os dados de uma vez
    cursor.executemany("INSERT INTO farmers VALUES (?, ?, ?, ?, ?, ?)", farmers_data)


# Executar a configuração do banco de dados
if __name__ == "__main__":
    setup_database()