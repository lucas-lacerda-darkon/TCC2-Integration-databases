import pyodbc
import configparser
import datetime

# Função para registrar mensagens em um arquivo de log
def registrar_log(log_file, mensagem):
    with open(log_file, 'a') as file:
        file.write(mensagem + '\n')

# Ler as configurações de conexão do arquivo INI
config = configparser.ConfigParser()
config.read('Parametros.ini')  # Substitua pelo caminho completo do arquivo INI

# Parâmetros de conexão para "banco1"
hostname1 = config['Database1']['hostname']
banco1 = config['Database1']['banco']
user1 = config['Database1']['user']
senha1 = config['Database1']['senha']

# Parâmetros de conexão para "banco2"
hostname2 = config['Database2']['hostname']
banco2 = config['Database2']['banco']
user2 = config['Database2']['user']
senha2 = config['Database2']['senha']

# Definir nome do arquivo de log
data_hora = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_file = f'log_{data_hora}.txt'

# Iniciar a sincronização
try:
    # Conectar ao "banco1"
    conn1 = pyodbc.connect(f"DRIVER=SQL Server;SERVER={hostname1};DATABASE={banco1};UID={user1};PWD={senha1}")
    cursor1 = conn1.cursor()

    # Conectar ao "banco2"
    conn2 = pyodbc.connect(f"DRIVER=SQL Server;SERVER={hostname2};DATABASE={banco2};UID={user2};PWD={senha2}")
    cursor2 = conn2.cursor()

    registrar_log(log_file, 'Conexão com sucesso')
    registrar_log(log_file, 'Início da sincronização')

    # Consultar registros em "banco1" com enviado = 'S' e copiá-los para "banco2" com enviado = 'P'
    cursor1.execute("SELECT * FROM dados WHERE enviado = 'S'")
    registros = cursor1.fetchall()

    quantidade_copiados = 0
    quantidade_erros = 0

    for registro in registros:
        id_registro = registro.id

        try:
            cursor2.execute("INSERT INTO dados (texto1, numeric1, enviado, data_hora) VALUES (?, ?, ?, GETDATE())",
                            registro.texto1, registro.numeric1, 'S')
            conn2.commit()
            cursor1.execute("UPDATE dados SET enviado = 'P' WHERE id = ?", id_registro)
            conn1.commit()
            registrar_log(log_file, f"ID: {id_registro}, Enviado para o banco2 - Data Hora Fim: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
            quantidade_copiados += 1
        except Exception as e:
            registrar_log(log_file, f"Erro de envio: {str(e)}")
            quantidade_erros += 1

    registrar_log(log_file, 'Fim da sincronização')

except Exception as e:
    registrar_log(log_file, f'Erro de conexão: {str(e)}')
    quantidade_copiados = None
    quantidade_erros = None

# Criar arquivo de log final
log_final_file = f'logFinal_{data_hora}.txt'
with open(log_final_file, 'w') as log_final:
    log_final.write(f'Quantidade copiados: {quantidade_copiados}\n')
    log_final.write(f'Quantidade de erros: {quantidade_erros}\n')
    log_final.write(f'Data Hora Início: {data_hora}\n')
    log_final.write(f'Data Hora Fim: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
    log_final.write(f'Hostname1: {hostname1}\n')
    log_final.write(f'Hostname2: {hostname2}\n')
    log_final.write(f'Banco1: {banco1}\n')
    log_final.write(f'Banco2: {banco2}\n')

print("Processo concluído.")
