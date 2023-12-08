import pyodbc
import configparser
import datetime
from tqdm import tqdm
import signal
import pymongo
import psutil
import pytz  # 3rd party: $ pip install pytz


# Variável de controle para verificar se o processo deve ser interrompido
processo_interrompido = False

# Listas para armazenar os valores de uso da CPU e RAM
cpu_percent_list = []
ram_percent_list = []

# Função para lidar com o sinal de interrupção (Ctrl+C)
def lidar_com_sinal_interrupcao(sig, frame):
    global processo_interrompido
    processo_interrompido = True
    print("\nSinal de interrupção recebido. Encerrando o processo...")

# Registre a função para lidar com o sinal de interrupção (Ctrl+C)
signal.signal(signal.SIGINT, lidar_com_sinal_interrupcao)

# Função para registrar mensagens em um arquivo de log
def registrar_log(log_file, mensagem):
    with open(log_file, 'a') as file:
        file.write(mensagem + '\n')

# Função para obter informações de uso da CPU e RAM
def obter_informacoes_recursos():
    cpu_percent = psutil.cpu_percent()
    ram_percent = psutil.virtual_memory().percent
    return f"CPU: {cpu_percent}% | RAM: {ram_percent}%"

# Ler as configurações de conexão do arquivo INI
config = configparser.ConfigParser()
config.read('Parametros.ini')  # Substitua pelo caminho completo do arquivo INI

# Parâmetros de conexão para "banco1" (SQL Server)
hostname1 = config['Database1']['hostname']
banco1 = config['Database1']['banco']
user1 = config['Database1']['user']
senha1 = config['Database1']['senha']

# Parâmetros de conexão para "banco2" (MongoDB)
mongo_hostname = config['Database2']['hostname']
mongo_port = int(config['Database2']['port'])
mongo_database = config['Database2']['database']

# Definir nome do arquivo de log
data_hora = datetime.datetime.now(pytz.timezone("America/Sao_Paulo")).strftime('%Y-%m-%d_%H-%M-%S')
log_file = f'log_{data_hora}.txt'

# Iniciar a sincronização
try:
    # Conectar ao "banco1" (SQL Server)
    conn1 = pyodbc.connect(f"DRIVER=SQL Server;SERVER={hostname1};DATABASE={banco1};UID={user1};PWD={senha1}")
    cursor1 = conn1.cursor()

    # Conectar ao "banco2" (MongoDB)
    client = pymongo.MongoClient(mongo_hostname, mongo_port)
    db2 = client[mongo_database]
    dados2 = db2['dados']

    registrar_log(log_file, 'Conexão com sucesso')
    registrar_log(log_file, 'Início da sincronização')

    # Consultar registros em "banco1" (SQL Server) com enviado = 'S'
    cursor1.execute("SELECT * FROM dados WHERE enviado = 'S'")
    registros = cursor1.fetchall()

    quantidade_copiados = 0
    quantidade_erros = 0

    with tqdm(total=len(registros), unit="registro", desc="Sincronizando") as pbar:
        for registro in registros:
            if processo_interrompido:
                break  # Interrompa a sincronização se o processo foi interrompido

            id_registro = registro.id

            try:
            # Converter objetos Decimal para float
                numeric1 = float(registro.numeric1)
    
                # Inserir registro em "banco2" (MongoDB)
                registro_mongo = {
                    "texto1": registro.texto1,
                    "numeric1": numeric1,  # Converter para float
                    "enviado": "P",
                    "data_hora": datetime.datetime.now(pytz.timezone("America/Sao_Paulo")).strftime('%Y-%m-%d_%H-%M-%S')
                }
                dados2.insert_one(registro_mongo)
    
                # Atualizar registro em "banco1" (SQL Server)
                cursor1.execute("UPDATE dados SET enviado = 'P' WHERE id = ?", id_registro)
                conn1.commit()
    
                informacoes_recursos = obter_informacoes_recursos()
                registrar_log(log_file, f"ID: {id_registro}, Enviado para o banco2 (MongoDB) | Recursos: {informacoes_recursos}")
                quantidade_copiados += 1
    
                # Registre os valores de uso da CPU e RAM
                cpu_percent_list.append(psutil.cpu_percent())
                ram_percent_list.append(psutil.virtual_memory().percent)
            except Exception as e:
                registrar_log(log_file, f"Erro de envio: {str(e)}")
                quantidade_erros += 1

        pbar.update(1)

    registrar_log(log_file, 'Fim da sincronização')

except Exception as e:
    registrar_log(log_file, f'Erro de conexão: {str(e)}')
    quantidade_copiados = None
    quantidade_erros = None

# Calcular a média do uso da CPU e RAM
media_cpu = sum(cpu_percent_list) / len(cpu_percent_list)
media_ram = sum(ram_percent_list) / len(ram_percent_list)

# Criar arquivo de log final
log_final_file = f'logFinal_{data_hora}.txt'
with open(log_final_file, 'w') as log_final:
    log_final.write(f'Quantidade copiados: {quantidade_copiados}\n')
    log_final.write(f'Quantidade de erros: {quantidade_erros}\n')
    log_final.write(f'Média CPU: {media_cpu:.2f}%\n')
    log_final.write(f'Média RAM: {media_ram:.2f}%\n')
    log_final.write(f'Data Hora Início: {data_hora}\n')
    log_final.write(f'Data Hora Fim: {datetime.datetime.now(pytz.timezone("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S")}\n')
    log_final.write(f'Hostname1: {hostname1}\n')
    log_final.write(f'Hostname2: {mongo_hostname}\n')
    log_final.write(f'Banco1: {banco1}\n')
    log_final.write(f'Banco2: {mongo_database}\n')

print("Processo concluído.")
