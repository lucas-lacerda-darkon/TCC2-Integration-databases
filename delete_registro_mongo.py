import pymongo

# Parâmetros de conexão com o MongoDB
mongo_hostname = 'localhost'
mongo_port = 27017
mongo_database = 'database3'

# Conectar ao MongoDB
client = pymongo.MongoClient(mongo_hostname, mongo_port)
db = client[mongo_database]
dados = db['dados']

# Defina a condição para exclusão (por exemplo, onde "enviado" é "E")
condicao = {"enviado": "P"}

# Exclua os registros que atendem à condição
resultado = dados.delete_many(condicao)

# Exiba o número de registros excluídos
print(f"Número de registros excluídos: {resultado.deleted_count}")
