import pyodbc
import json
import datetime

# Função para registrar mensagens em um arquivo de log
def registrar_log(log_file, mensagem):
    with open(log_file, 'a') as file:
        file.write(mensagem + '\n')

# Carregando parâmetros de conexão do arquivo JSON
with open('Parametros.json', 'r') as json_file:
    parametros = json.load(json_file)

# Parâmetros de conexão
hostname1 = parametros["hostname1"]
banco1 = parametros["banco1"]
user1 = parametros["user1"]
senha1 = parametros["senha1"]

hostname2 = parametros["hostname2"]
banco2 = parametros["banco2"]
user2 = parametros["user2"]
senha2 = parametros["senha2"]

# Strings de conexão
conn_str1 = f'DRIVER={{SQL Server}};SERVER={hostname1};DATABASE={banco1};UID={user1};PWD={senha1}'
conn_str2 = f'DRIVER={{SQL Server}};SERVER={hostname2};DATABASE={banco2};UID={user2};PWD={senha2}'

# Conectar aos bancos de dados
try:
    conn1 = pyodbc.connect(conn_str1)
    conn2 = pyodbc.connect(conn_str2)
    cursor1 = conn1.cursor()
    cursor2 = conn2.cursor()

    # Iniciar a sincronização
    registrar_log('log.txt', 'Conexão com sucesso')
    registrar_log('log.txt', 'Início da sincronização')

    # Selecionar registros do Database1 onde enviado = 'N'
    cursor1.execute('SELECT * FROM dados WHERE enviado = ?', 'N')
    registros = cursor1.fetchall()

    for registro in registros:
        id_registro = registro.id
        try:
            # Inserir no Database2 com enviado = 'S'
            cursor2.execute('INSERT INTO dados (texto1, numeric1, enviado, hostname, appname) VALUES (?, ?, ?, ?, ?)',
                            f'Enviado registro para o banco {banco2}', id_registro, 'S', HOST_NAME(), APP_NAME())
            conn2.commit()

            # Atualizar o enviado no Database1 para 'P'
            cursor1.execute('UPDATE dados SET enviado = ? WHERE id = ?', 'P', id_registro)
            conn1.commit()

            # Registrar sucesso no log
            registrar_log('log.txt', f'Enviado com sucesso para o banco {banco2}')
        except Exception as e:
            # Registrar erro no log
            registrar_log('log.txt', f'Erro de envio: {str(e)}')

    quantidade_copiados = null 
    # Calcular e registrar quantidade de registros copiados
    quantidade_copiados = len(registros)
    registrar_log('log.txt', f'Quantidade copiados: {quantidade_copiados}')

    # Fim da sincronização
    registrar_log('log.txt', 'Fim da sincronização')

except Exception as e:
    # Registrar erro de conexão no log
    registrar_log('log.txt', f'Erro de conexão: {str(e)}')

finally:
    if 'conn1' in locals():
        conn1.close()
    if 'conn2' in locals():
        conn2.close()

# Criar arquivo de log final com informações adicionais
data_hora = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_final_file = f'logFinal_{data_hora}.txt'

with open(log_final_file, 'w') as log_final:
    log_final.write(f'Quantidade copiados: {quantidade_copiados}\n')
    log_final.write(f'Quantidade de erros: {quantidade_copiados - len(registros)}\n')
    log_final.write(f'Data Hora Início: {data_hora}\n')
    log_final.write(f'Data Hora Fim: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
    log_final.write(f'Hostname1: {hostname1}\n')
    log_final.write(f'Hostname2: {hostname2}\n')
    log_final.write(f'Banco1: {banco1}\n')
    log_final.write(f'Banco2: {banco2}\n')

print("Processo concluído.")
