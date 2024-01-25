import pandas as pd
from pymongo import MongoClient
import os

client = MongoClient("mongodb://vps1.amoros.io:32777")
db = client["database2"]

AA = ["A", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "V", "W", "Y"]



# Collection pour les données du fichier TSV
tsv_collection_name = "taxo"
tsv_collection = db[tsv_collection_name]

# Chemin du fichier TSV
tsv_file_path = "data/taxo_filtered.tsv"

# Charger le fichier TSV en utilisant pandas
df = pd.read_csv(tsv_file_path, sep='\t')

# Convertir le DataFrame en dictionnaires (une ligne par document)
data_dict = df.to_dict(orient='records')

# Insérer les données dans la nouvelle collection MongoDB
tsv_collection.insert_many(data_dict)

print("Importation des données TSV dans MongoDB terminée.")





# Nom de la collection MongoDB
collection_name = "freq_taxon"
collection = db[collection_name]
x=0
for i in range(len(AA)):
    for j in range(len(AA)):
        x=x+1
        # Construire le chemin du fichier CSV 
        file = f"data/freq_taxon/{AA[i]}-{AA[j]}.csv"
        df = pd.read_csv(file)


        df.insert(0,"AA1",AA[i])
        df.insert(1,"AA2",AA[j])

        donnees_mongodb = df.to_dict(orient='records')
        collection.insert_many(donnees_mongodb)
        print(x)




