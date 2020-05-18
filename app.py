import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import scipy.optimize as so
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

########### Define your variables

def obj(proteines=75,lipides=90,glucides=225,kcal=2000,fer=9,calcium=800,fibres=45):
    """
    Fixe les objectifs a atteindre dans un tableau numpy.
    Les grammages des apports sont comptes selon la maniere habituelle de le faire : 
        Proteines, lipides, glucides et fibres en grammes 
        Fer et calcium en miligrammes 
        Kcal est deja une mesure en soit.
        
    Retourne objectif : le tableau numpy des objectifs nutritionnels"""
    objectif=np.array([proteines,lipides,glucides,kcal,fer,calcium,fibres])
    return objectif

def obj_new(kwargs):
    """Permets la mise a jour des objectifs en temps reel dans une liste.
    
    Retourne array2 : la liste des objectifs nutritionnels"""
    listeobjectif = [kwargs["proteines"], kwargs["lipides"], kwargs["glucides"], kwargs["kcal"], kwargs["fer"], kwargs["calcium"], kwargs["fibres"]]
    
    return listeobjectif


def restriction(regime='Omnivore'):
    """Adapte les aliments disponibles en fonction des regimes suivis.
        Omnivore correspond a un regime sans restriction particuliere
        Vegetarien correspond a un regime sans viande ni poisson
        Vegan correspond a un regime sans produit d'origine animale
        Sans lactose correspond a un regime sans lait.
        
        Retourne dataregime : le jeu de donnees adapte au regime selectionne"""
  
    
    data2=data.copy()
    if regime == "Vegetarien":
        data3=vegetarien(data2)

    elif regime == "Vegan":
        data3=vegan(data2)
        
    elif regime == "Sans Lactose":
        data3=lactose(data2)
        
    else:
        data3=data.copy()
        
    dataregime=data3.set_index("Produit (100g)").copy()
    return dataregime

def vegetarien(data):
    """Adapte la liste d'aliments pour les vegetariens.
    
    Retourne datavege : la liste des aliments sans viande ni poisson"""
    i=0
    while i<len(data):
        
        A = data["Produit (100g)"].str.contains(pat = 'Viande')
        B = data["Produit (100g)"].str.contains(pat = 'Poisson')
        if A[i] == True or B[i] == True:
            data.drop([i],0,inplace=True)
        i+=1

    datavege=data.copy()
    return datavege


def vegan(data):
    """Adapte la liste d'aliments pour les vegan.
    
    Retourne datavegan : la liste des aliments non issus d'animaux"""
    i=0
    while i<len(data):
            
        A = data["Produit (100g)"].str.contains(pat = 'Lait')
        B = data["Produit (100g)"].str.contains(pat = 'Viande')
        C = data["Produit (100g)"].str.contains(pat = 'Poisson')
        if A[i] == True or B[i] == True or C[i] == True:
            data.drop([i],0,inplace=True)
        i+=1

    datavegan=data.copy()
    return datavegan

def lactose(data): 
    """Adapte la liste d'aliments pour les personnes intolerantes au lactose.
    
    Retourne datasanslactose : la liste des aliments ne contenants pas de lait"""
    i=0
    while i<len(data):
        A = data["Produit (100g)"].str.contains(pat = 'Lait')
        if A[i] == True:
            data.drop([i],0,inplace=True)
        i+=1

    datasanslactose=data.copy()
    return datasanslactose

def minmaxfun(objmax,objmin):
    """Definit un intervalle au dessus et en dessous de l'objectif, les apports du repas ne doivent pas sortir de cet intervalle.
    objmax doit etre compris entre 1 et 2 et objmin entre 0 et 1. 
    
    Retourne objminmax : un tableau numpy des objectifs minimaux et maximaux"""
    objminmax = np.array([objmin,objmax])

    return objminmax


def optimisation(objectif,data,objmax=1,objmin=1):
    """ Permet de minimiser le prix total selon les elements du jeu de donnees data sous la contrainte d'objectif.
    Si min et max ne sont pas specifies objectif doit etre inferieur au resultat sinon il doit etre compris entre min et max.
    """
    objectif=np.array(objectif)
    A=np.array(data).T

    objminmax=minmaxfun(objmax,objmin)
    if  objminmax[1] <= 1 and objminmax[0] >= 1 :
        result=so.linprog(A[-1], A_ub=-A[:-1], b_ub=-objectif,method='simplex') 
    else :
        result=so.linprog(A[-1], A_ub=np.concatenate((-A[:-1],A[:-1]),axis=0), b_ub=np.concatenate((-objminmax[0]*objectif, objminmax[1]*objectif), axis=0), method='simplex')
       
    
    return result

def minmaxfun_d(obj):
    """Definit un intervalle au dessus et en dessous de l'objectif, les apports du repas ne doivent pas sortir de cet intervalle.
    L'intervalle est défini automatiquement en fonction de la valeur choisie/saisie par l'utilisateur.
    
    Retourne objminmax : un tableau numpy des objectifs minimaux et maximaux"""
    
    if obj == 'Ne pas dépasser de 10% ses objectifs' :
        objminmax = np.array([1,1.1])
    elif obj == 'Atteindre ses objectifs à + ou - 10%' :
        objminmax = np.array([0.9,1.1])
    else :    
        objminmax = np.array([1,1])

    return objminmax



def optimisation_d(objectif,data,obj):
    """ Version automatique, permet de minimiser le prix total selon les elements du jeu de donnees data sous la contrainte d'objectif.
    La contrainte d'objectif est déterminée automatiquement par la fonction minmaxfun_d.
    """
    objectif=np.array(objectif)
    A=np.array(data).T
           

    objminmax=minmaxfun_d(obj)
    
    if  objminmax[1] <= 1 and objminmax[0] >= 1 :
        result=so.linprog(A[-1], A_ub=-A[:-1], b_ub=-objectif,method='simplex') 
    else :
        result=so.linprog(A[-1], A_ub=np.concatenate((-A[:-1],A[:-1]),axis=0), b_ub=np.concatenate((-objminmax[0]*objectif, objminmax[1]*objectif), axis=0), method='simplex')
       
    
    return result




def apports(result,data):
    """ Tableau recapitulatif des aliments conseilles, de leur quantite, leur prix et des apports obtenus pour la quantite consommee.
    La derniere ligne fait le total et correspond aux poids, apports au prix du repas dans son ensemble. 
    result est le resultat de la fonction optimisation
    
    Retourne le tableau recapitulatif : repas et les apports nutritionnels de ce repas : total"""
    A=result.x
    u,=A.nonzero()
    rest=data.iloc[u,:]
    qte=pd.DataFrame({'Quantites en g' : 100*A[A.nonzero()]}).set_index(data.iloc[u,:].index)
    bilan=pd.DataFrame((np.array(rest).T*A[A.nonzero()]).T).set_index(qte.index)
    repas=pd.concat([qte,bilan],axis=1)
    total=repas.sum()
    repas=repas.append([total])
    namescol=['Quantite (en g)']+list(data.columns)
    namescol[-1]='Prix (en euros)'
    repas.columns=namescol
    namesrow=list(qte.index)
    namesrow.append('Apports du repas')
    repas.index=namesrow
    repas = np.around(repas, decimals=2)

    return repas,total



def rename_aliment(old_name):
    """Permets d'obtenir le nom des aliments sans leur categorie. """
    new_name=old_name.replace("Lait ", "")
    new_name=new_name.replace("Viande ", "")
    new_name=new_name.replace("Poisson ", "")
    new_name=new_name.replace("Le\xe9gume ", "")
    new_name=new_name.replace("Base ", "")
    return new_name


def repas(result,data):
    """Recapitule les aliments conseilles selon les apports specifies, leur prix et le nombre de calories consommees dans une phrase. 
    result est le resultat de la fonction optimisation
    
    Retourne phrase : une chaine de carateres qui recapitule les aliments conseilles"""
    A=result.x
    u,=A.nonzero()
    qt=A[u]
    phrase='Pour minimiser ses depenses et atteindre ses objectifs d\'apports journaliers, Marie doit consommer'
    for s in range(len(u)-1):
        if s>0 : phrase+=','
        gr=qt[s]*100
        old_name=data.iloc[u].index[s]
        name = rename_aliment(old_name)
        phrase+=' {:0.2f}g de {}'.format(gr,name)
    s=len(u)-1    
    gr=qt[s]*100
    old_name=data.iloc[u].index[s]
    name = rename_aliment(old_name)
    phrase+=' et {:0.2f}g de {}. '.format(gr,name)
    repas=apports(result,data)
    repas=repas[0]
    phrase+='Cela lui coutera {:0.2f} euros au total et comprend {:0.2f} calories.'.format(result.fun,repas['Energie (kcal)'][-1])
    print(phrase)
 
    
def recapbarplot(total,objectif,objmin=1,objmax=1):
    """Trace un graphique comparant le total des apports du repas aux objectifs d\'apports journaliers initiaux.
    
    total est une liste correspondant aux apports totaux du repas conseille/choisi, objectif est la liste des objectifs d'apport, objmin est le rapport minimum de ces objectifs a atteindre, objmax est le rapport maximum de ces objectifs a atteindre 
    
    Retourne un barplot recapitulatif des proportions d'apport par rapport a l'objectif """
    totalapport = [total[0], total[1], total[2], total[3], total[4], total[5], total[6]]
    pourcentage = [x/y for x, y in zip(totalapport,objectif)]
    pourcentage = [i*100 for i in pourcentage]
    objminmax=minmaxfun(objmax,objmin)
    plt.bar(range(7), pourcentage, width = 0.5, color = 'darkseagreen')
    bars = ('Proteines', 'Lipides', 'Glucides','Calories', 'Fer', 'Calcium','Fibres')
    if objminmax[0]<1:
        plt.axhline(y=objminmax[0]*100,linewidth=0.7,color='tomato',linestyle='--')
    if objminmax[1]>1:
        plt.axhline(y=objminmax[1]*100,linewidth=0.7,color='tomato',linestyle='--')

    plt.axhline(y=100,linewidth=1,color='red')
    y_pos = np.arange(len(bars))
    plt.xticks(y_pos, bars)
    plt.ylabel('Pourcentages des objectifs', fontsize='12')
    plt.show()
    
    
def preparation_df(prots,lip,glu,kcal,fer,calc,fib,obj,regime):
    """Prend en input les valeurs des curseurs, ainsi que les objectifs et le régime alimentaire, puis utilise 
    les fonctions restriction et optimisation_d pour construire le repas optimal, utilise ensuite la fonction apports 
    pour construire un tableau récapitulatif ainsi que les totaux. 
    La fonction renvoie un tuple comprenant un dataframe avec le repas optimal et la liste du total des apports du repas """
    objectifs=[prots,lip,glu,kcal,fer,calc,fib]
    regime_df=restriction(regime)
    resultats=optimisation_d(objectifs,regime_df,obj)
    tbapp=apports(resultats,regime_df)
    
    
    return tbapp


beers=['Chesapeake Stout', 'Snake Dog IPA', 'Imperial Porter', 'Double Dog IPA']
ibu_values=[35, 60, 85, 75]
abv_values=[5.4, 7.1, 9.2, 4.3]
color1='lightblue'
color2='darkgreen'
mytitle='Beer Comparison'
tabtitle='beer!'
myheading='Flying Dog Beers'
label1='IBU'
label2='ABV'
githublink='https://github.com/austinlasseter/flying-dog-beers'
sourceurl='https://www.flyingdog.com/beers/'

########### Set up the chart
bitterness = go.Bar(
    x=beers,
    y=ibu_values,
    name=label1,
    marker={'color':color1}
)
alcohol = go.Bar(
    x=beers,
    y=abv_values,
    name=label2,
    marker={'color':color2}
)

beer_data = [bitterness, alcohol]
beer_layout = go.Layout(
    barmode='group',
    title = mytitle
)

beer_fig = go.Figure(data=beer_data, layout=beer_layout)


########### Initiate the app
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)
server = app.server
app.title=tabtitle

########### Set up the layout
app.layout = html.Div([ 
    
    
    html.Div([

        html.Div([
            html.P("Objectif :", style={'color':'rgb(246, 185, 53)'}),
            dcc.Dropdown(
                id='obj',
                options=[
                    {'label': 'Minimiser les dépenses uniquement', 'value': 'depenses'},
                    {'label': 'Ne pas dépasser de 10% ses objectifs', 'value': 'Ne pas dépasser de 10% ses objectifs'},
                    {'label': 'Atteindre ses objectifs à + ou - 10%', 'value': 'Atteindre ses objectifs à + ou - 10%'}],
                value='depenses'
            )
        ],style={'width': '65%','display': 'inline-block'}), # style{} affecte des commandes CSS à l'objet 
        

        
        
        html.Div([
            html.P("Régime :", style={'color':'rgb(246, 185, 53)'}),
            
            dcc.Dropdown(
                id='regime',
                options=[
                    {'label': 'Omnivore', 'value': 'Omnivore'},
                    {'label': 'Végétarien', 'value': 'Vegetarien'},
                    {'label': 'Vegan', 'value': 'Vegan'},
                    {'label': 'Sans lactose', 'value': 'Sans Lactose'}],
                value='Omnivore'
                )
        ], style={'width': '34%','float': 'right','display': 'inline-block'}),
        
        ],style={'width': '30%','backgroundColor': 'rgb(22, 26, 40)','display': 'flex'}),
        
    
        
        
  html.Div([            
        
        html.Div([
            html.P(id = "p_prots"),
            dcc.Slider(
                id='prots',
                min=40,
                max=250,
                step=5,
                value=75,
                marks={40:"40",75:"75",250:"250"}
                ),
            
            html.P(id="p_lip"),
            dcc.Slider(
                id='lip',
                min=30,
                max=130,
                step=5,
                value=90,
                marks={30:"30",90:"90",130:"130"}
                ),

            html.P(id="p_glu"),
            dcc.Slider(
                id='glu',
                min=50,
                max=300,
                step=5,
                value=225,
                marks={50:"50",225:"225",300:"300"}
                ),
        
            html.P(id="p_kcal"),
            dcc.Slider(
                id='kcal',
                min=1500,
                max=3000,
                step=10,
                value=2000,
                marks={1500:"1500",2000:"2000",3000:"3000"}
                ),
            html.P(id="p_fer"),
            dcc.Slider(
                id='fer',
                min=1,
                max=15,
                step=1,
                value=9,
                marks={1:"1",15:"15",9:"9"}
                ),  
            html.P(id="p_calc"),
            dcc.Slider(
                id='calc',
                min=500,
                max=1300,
                step=50,
                value=800,
                marks={500:"500",800:"800",1300:"1300"}
                ),
            html.P(id="p_fib"),
            dcc.Slider(
                id='fib',
                min=15,
                max=80,
                step=5,
                value=45,
                marks={45:"45",15:"15",80:"80"}
                )], style={'width': '30%',
        'backgroundColor': 'rgb(22, 26, 40)', 'display': 'inline-block', 'vertical-align': 'bottom','color':'rgb(246, 185, 53)'}),
    
        html.Div([
            html.H1("Régime Alimentaire", style={'color':'rgb(246, 185, 53)','position': 'absolute','top':'0px','right':'300px'}),
            html.Div([
                dcc.Graph(id="bpt_fig")],style={'position': 'absolute','top': '60px','right':'0px', 'width':'65%'}),
            html.Div([
                dcc.Graph(id="tbl_fig")],style={'maxHeight': '200px','overflow':'auto','position': 'absolute','top': '520px', 'right':'0px', 'width':'65%'})]
                
                ,style={'float': 'right','width': '60%','margin': '0px'}),

             
          ])


    
            
        ], style={
  'verticalAlign':'middle',
  'backgroundColor': 'rgb(35, 38, 53)',
  'position':'fixed',
  'width':'100%',
  'height':'100%',
  'top':'0px',
  'left':'0px',  
  'z-index':'1000'  
}
        
    )

if __name__ == '__main__':
    app.run_server()
