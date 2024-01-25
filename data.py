import pandas as pd
from pymongo import MongoClient
import os

client = MongoClient("mongodb://vps1.amoros.io:32777")
db = client["database"]

AA = ["A", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "V", "W", "Y"]



# collection MongoDB
collection = db["freq_taxon"]
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




