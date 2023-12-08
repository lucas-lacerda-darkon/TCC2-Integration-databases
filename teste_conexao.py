import pyodbc


# Parâmetros de conexão (substitua pelos seus próprios valores)
server = 'DESKTOP-6ERDHEL\SQLEXPRESS'
database = 'Database1'
username = 'user'
password = 'user1234'

# Tente estabelecer a conexão
try:
    conn_str = f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    connection = pyodbc.connect(conn_str)

    print("Conexão bem-sucedida com o SQL Server 2 ")

    # Você pode executar consultas ou outras operações aqui, se necessário

    connection.close()

except pyodbc.Error as e:
    print("Erro de conexão com o SQL Server:")
    print(e)
