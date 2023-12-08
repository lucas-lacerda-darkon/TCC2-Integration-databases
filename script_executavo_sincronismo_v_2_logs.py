import pyodbc
import configparser
import datetime
import psutil
from tqdm import tqdm
import signal

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

    with tqdm(total=len(registros), unit="registro", desc="Sincronizando") as pbar:
        for registro in registros:
            if processo_interrompido:
                break  # Interrompa a sincronização se o processo foi interrompido

            id_registro = registro.id

            try:
                cursor2.execute("INSERT INTO dados (texto1, numeric1, enviado, data_hora) VALUES (?, ?, ?, GETDATE())",
                                registro.texto1, registro.numeric1, 'P')
                conn2.commit()
                cursor1.execute("UPDATE dados SET enviado = 'P' WHERE id = ?", id_registro)
                conn1.commit()
                informacoes_recursos = obter_informacoes_recursos()
                registrar_log(log_file, f"ID: {id_registro}, Enviado para o banco2 | Recursos: {informacoes_recursos}")
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
    log_final.write(f'Data Hora Fim: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
    log_final.write(f'Hostname1: {hostname1}\n')
    log_final.write(f'Hostname2: {hostname2}\n')
    log_final.write(f'Banco1: {banco1}\n')
    log_final.write(f'Banco2: {banco2}\n')

print("Processo concluído.")
