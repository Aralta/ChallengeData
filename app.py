import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient
import pandas as pd
import pprint



# Connexion à MongoDB
client = MongoClient("mongodb://vps1.amoros.io:32777")
db = client["database"]
collection = db["freq_taxon"]

#test de validité de la base 
print(collection.count_documents({}))
print(collection.count_documents({"taxon_id":9606,"AA1":"A","AA2":"A"}))
pprint.pprint(collection.find({"taxon_id":9606,"AA1":"A","AA2":"A"}))

##########################################################################################
#                                                                                        #
#                         options pour les deroulants                                    #
#                                                                                        #
##########################################################################################

# Chemin du fichier TSV
tsv_file_path = "data/taxo_filtered.tsv"

# Charger le fichier TSV en utilisant pandas
df_taxo = pd.read_csv(tsv_file_path, sep='\t')

taxo_option = [{
    'label': f" {row['taxon_Id']} - {row['scientific_name']}", 'value': row['taxon_Id']
} for index, row in df_taxo.iterrows()]

# Liste des acides aminés
AA = ["A", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "V", "W", "Y"]

##########################################################################################



# Création de l'application Dash
app = dash.Dash(__name__)

# Tableau de bord
app.layout = html.Div([
    html.H1("Analyse des distributions d'acides aminés"),

    # Sélection de l'ID du graphique
    dcc.Dropdown(
        id='id-plot-dropdown',
        options=taxo_option,
        value=str(collection.find_one()['_id']),
        style={'width': '50%'}
    ),

    # Sélection des acides aminés AA1 et AA2
    dcc.Dropdown(
        id='aa1-dropdown',
        options=[
            {'label': aa, 'value': aa} for aa in AA
        ],
        value='A',
        style={'width': '30%'}
    ),
    
    dcc.Dropdown(
        id='aa2-dropdown',
        options=[
            {'label': aa, 'value': aa} for aa in AA
        ],
        value='C',
        style={'width': '30%'}
    ),

    # Graphique Plotly
    dcc.Graph(id='distribution-plot'),
    dcc.Graph(id='comparaison-plot'),
    dcc.Graph(id='repartition-plot')
])

##########################################################################################
#                                                                                        #
#                         graphique distribution de AA                                   #
#                                                                                        #
##########################################################################################


# Callback pour mettre à jour le graphique en fonction de la sélection
@app.callback(
    Output('distribution-plot', 'figure'),
    [Input('id-plot-dropdown', 'value'),
     Input('aa1-dropdown', 'value'),
     Input('aa2-dropdown', 'value')]
)

def update_plot(selected_id, selected_aa1, selected_aa2):

    if not selected_id:
        return go.Figure()
    
    else:
        # Récupérer les données de MongoDB en fonction de l'ID sélectionné
        cursor = collection.find({"taxon_id": selected_id, "AA1": selected_aa1, "AA2": selected_aa2})
    
        # Convertir le curseur en liste de dictionnaires
        data_list = list(cursor)
    
        # Créer un dictionnaire avec les valeurs de 1 à 100 et leurs fréquences
        oc = {str(d): 0 for d in range(1, 101)}
        for entry in data_list:
            for d in range(1, 101):
                oc[str(d)] += entry.get(str(d), 0)
    
        # Créer un DataFrame à partir des données récupérées
        df2 = pd.DataFrame(list(oc.items()), columns=['index', 'valeurs'])
    
        # Utiliser Plotly graph_objects pour créer le graphique
        fig = go.Figure()
    
        # Ajouter une trace pour les valeurs de 1 à 100
        fig.add_trace(go.Scatter(x=df2['index'], y=df2['valeurs'], mode='lines+markers',
                             name=f'Distribution des acides aminés {selected_aa1}-{selected_aa2}'))

        fig.update_layout(title=f'Distribution des acides aminés {selected_aa1}-{selected_aa2}',
                        xaxis=dict(title='Position'),
                        yaxis=dict(title='Frequency'))

        return fig





##########################################################################################
#                                                                                        #
#                          graphique comparaison de AA                                   #
#                                                                                        #
##########################################################################################

# Callback pour mettre à jour le graphique en fonction de la sélection
@app.callback(
    Output('comparaison-plot', 'figure'),
    [Input('id-plot-dropdown', 'value'),
     Input('aa1-dropdown', 'value'),
     Input('aa2-dropdown', 'value')]
)

def update_plot2(selected_id, selected_aa1, selected_aa2):

    if not selected_id:
        return go.Figure()
    
    else:
        # Utiliser Plotly graph_objects pour créer le graphique
        fig = go.Figure()

        for i in range (2):
            if i==0:
                AA1 = selected_aa1
                AA2 = selected_aa2 
                
            else: 
                AA1 = selected_aa2
                AA2 = selected_aa1
   

            # Récupérer les données de MongoDB en fonction de l'ID sélectionné
            cursor = collection.find({"taxon_id": selected_id, "AA1": AA1, "AA2": AA2})

            # Convertir le curseur en liste de dictionnaires
            data_list = list(cursor)

        
            # Créer un dictionnaire avec les valeurs de 1 à 100 et leurs fréquences
            oc = {str(d): 0 for d in range(1, 101)}
            for entry in data_list:
                for d in range(1, 101):
                    oc[str(d)] += entry.get(str(d), 0)


            # Créer un DataFrame à partir des données récupérées
            df = pd.DataFrame(list(oc.items()), columns=['index', 'valeurs'])
    
    
            # Ajouter une trace pour les valeurs de 1 à 100
            fig.add_trace(go.Scatter(x=df['index'], y=df['valeurs'], mode='lines+markers',
                                name=f'Distribution des acides aminés {AA1}-{AA2}'))


        fig.update_layout(title=f'Comparaison des acides aminés {selected_aa1}-{selected_aa2} et {selected_aa2}-{selected_aa1}',
                        xaxis=dict(title='Position'),
                        yaxis=dict(title='Frequency'))

        return fig



##########################################################################################
#                                                                                        #
#                          piechar repartition des AA                                    #
#                                                                                        #
##########################################################################################
    

@app.callback(
    Output('repartition-plot', 'figure'),
    [Input('id-plot-dropdown', 'value')
]
)

def update_plot3(selected_id):
    res = {}
    if not selected_id:
        return go.Figure()
    
    else:
        for i in AA:
            cursor = collection.find({"taxon_id": selected_id, "AA1": i, "AA2": "A"})

            data_list = list(cursor)
            print(data_list[0]['count'])
            res[i]= data_list[0]['count']

        print(res)

        fig = px.pie(values=list(res.values()), names=list(res.keys()), title=f'Répartition des AA pour l\'id {selected_id} ')

        return fig


##########################################################################################





# Exécuter l'application Dash
if __name__ == '__main__':
    app.run_server(debug=True)
