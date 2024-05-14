
from urllib.parse import quote_plus
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.bdd.tables import Base, Region, Departement, Commune, PopulationParAnnee
from common.bdd.BDDUtilities import database_url



class BDD:
    
    
    def __init__(self):    
        self.database_url = database_url    
        self.engine = create_engine(self.database_url, echo=True)
        self.Session = sessionmaker(bind=self.engine)()
        self.region = Region
        self.departement = Departement
        self.commune = Commune
        self.populationParAnnee = PopulationParAnnee
            
        
    def __read_csv(self, file_path):
        return pd.read_csv(file_path, encoding='utf-8', low_memory=False)

    def __insert_data(self, df, table_name, total_rows=None):
        try:
            for i in range(0, len(df), 100):
                batch = df[i:i+100]  # Correction pour s'assurer que les bons lots sont traités
                batch.to_sql(table_name, con=self.engine, index=False, if_exists='append', method='multi', chunksize=50)
                self.Session.commit()
                print(f"{i + len(batch)} / {total_rows} lignes insérées dans {table_name}")
        except Exception as e:
            self.Session.rollback()
            print(f"Erreur lors de l'insertion des données : {e}")

    def __process_population_data(self, df, entity):
        # Liste des colonnes de population
        population_columns = [col for col in df.columns if 'Population en' in col]
        total_columns = len(population_columns)

        # Préparation des données pour chaque année
        for i, year_col in enumerate(population_columns):
            year = year_col.split(' ')[-1]
            print(f"Début du traitement de l'année {year} ({i+1}/{total_columns}).")
            year_data = df[[entity, year_col]].rename(columns={year_col: 'population', entity: 'code_commune'})
            year_data['annee'] = int(year)  # Ajouter une colonne année
            self.__insert_data(year_data, 'population_par_annee')
            print(f"Traitement de l'année {year} ({i+1}/{total_columns}) terminé.")

    def createBDD(self):
        # Création de la BDD
        user_input = input(f"Voules-vous créer la base de données ? (y/n): ")
        if user_input.lower() != 'y':
            print("Création de la base de donnée annulé.")
            return
        try:
            print("Création de la base de donnée.")
            Base.metadata.create_all(self.engine)
        except:
            print("Echec de la création de la base de données")
        
    def addDataInBDD(self):        
        user_input = input(f"Voules-vous ajouter les données à la base de données ? (y/n): ")
        if user_input.lower() != 'y':
            print("Ajout des données a la base de donnée annulé.")
            return
                
        communes_csv = 'docs/communes.csv'
        departements_csv = 'docs/departements.csv'
        regions_csv = 'docs/regions.csv'
        
        print("Chargement des données de regions, departements, communes.")
        regions_data = self.__read_csv(regions_csv)
        departements_data = self.__read_csv(departements_csv)
        communes_data = self.__read_csv(communes_csv)

        # Séparer les données de population
        population_columns = [col for col in communes_data.columns if 'Population en' in col]
        population_data = communes_data[population_columns + ['code']]
        print(communes_data)
        communes_data = communes_data.drop(columns=population_columns).rename(columns={'code_commune': 'code'})
        
        print("Insertion des données des regions, departements, communes.")
        self.__insert_data(regions_data, 'regions', len(regions_csv))
        self.__insert_data(departements_data, 'departements', len(departements_csv))
        self.__insert_data(communes_data, 'communes', len(communes_data))
        
        print("Traitement des données de population des communes.")
        self.__process_population_data(population_data, 'code')
        
    def closeSession(self):
        self.Session.close_all()
        
        