import os
from urllib.parse import urljoin
import pandas as pd
import requests
from common.api.GeographicApi import GeographicApi

class GeographicData:
    
    def __init__(self):        
        self.fetcher = GeographicApi()
        self.base_url = "https://www.insee.fr"
        # Mettre ici l'URL complète de téléchargement du fichier trouvé sur le site de l'INSEE
        self.file_url = "/fr/statistiques/fichier/3698339/base-pop-historiques-1876-2021.xlsx"
        self.download_url = urljoin(self.base_url, self.file_url)
        # Chemin vers le fichier Excel et le fichier CSV de sortie
        self.excel_path = "docs/base-pop-historiques-1876-2021.xlsx"
        self.output_csv_path = "docs/base-pop-historiques-1876-2021.csv"


    def __download_file(self, url, download_path):
        # Vérifie si le fichier existe déjà
        if os.path.exists(download_path):
            user_input = input(f"Le fichier {download_path} existe déjà. Voulez-vous le remplacer ? (y/n): ")
            if user_input.lower() != 'y':
                print("Téléchargement annulé.")
                return
        
        # Téléchargement du fichier
        response = requests.get(url)
        with open(download_path, 'wb') as f:
            f.write(response.content)
        print(f"Fichier téléchargé et sauvegardé sous : {download_path}")

    
    def __clean_and_convert_excel_to_csv(self, excel_path, output_csv_path):
        if os.path.exists(output_csv_path):
            user_input = input(f"Le fichier {output_csv_path} existe déjà. Voulez-vous le remplacer ? (y/n): ")
            if user_input.lower() != 'y':
                print("Conversion annulée.")
                return
        
        # Charger le fichier Excel, en sautant les 4 premières lignes et en prenant la 5ème comme en-tête
        df = pd.read_excel(excel_path, header=4)
        # Supprimer la ligne suivante après les en-têtes, qui est maintenant la première ligne du DataFrame
        df = df.drop(0, axis=0).reset_index(drop=True)
        # Sauvegarder le résultat en CSV
        df.to_csv(output_csv_path, index=False)
        print(f"Le fichier a été nettoyé et converti en CSV sous : {output_csv_path}")
        


    def __save_data_to_csv(self, data, filename_path):
        if os.path.exists(filename_path):
            user_input = input(f"Le fichier {filename_path} existe déjà. Voulez-vous le remplacer ? (y/n): ")
            if user_input.lower() != 'y':
                print("Téléchargement annulé.")
                return
        df = pd.DataFrame(data)         
        df.to_csv(filename_path, index=False)
        print(f"Données du CSV sauvegardées dans {filename_path}.")
        
    def __apply_data_types(self, df):
        # Identifier les colonnes nécessitant une conversion en entier
        population_cols = [col for col in df.columns if 'Population en' in col]
        
        # Traitement pour la colonne 'Région' également
        # Traiter chaque colonne
        for col in population_cols:
            # Convertir en numérique, en ignorant les erreurs pour transformer les non-numériques en NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')

            # Remplacer NaN par une valeur temporaire, convertir en Int64, puis remettre NaN
            df[col] = df[col].fillna(0).astype(int)  # Utiliser un entier temporaire qui ne perturbe pas vos données
            df[col] = df[col].astype(str) 
            
        return df



    def __handle_paris_fusion(self, csv_data):
        # Filtrer les données pour Paris
        paris_data = csv_data[csv_data['Code géographique'].str.startswith('751')]
        
        # Somme des populations pour chaque colonne
        population_columns = [col for col in paris_data.columns if 'Population en' in col]
        summed_populations = paris_data[population_columns].sum()

        # Créer une nouvelle ligne pour Paris avec la somme des populations
        paris_summary = pd.Series({'Code géographique': '75056', 'Libellé géographique': 'Paris', 'Région': '11', 'Département': '75'}, name="Paris")
        for col in population_columns:
            paris_summary[col] = summed_populations[col]

        # Supprimer les anciennes lignes de Paris
        csv_data = csv_data[~csv_data['Code géographique'].str.startswith('751')]
        # Ajouter la nouvelle ligne en utilisant concat
        new_row_df = pd.DataFrame([paris_summary])  # Convertir la Series en DataFrame
        csv_data = pd.concat([csv_data, new_row_df], ignore_index=True)

        return csv_data



    def __compare_and_merge_commune_data(self, api_communes, output_csv_path):
        csv_data = pd.read_csv(output_csv_path, low_memory=False)
        api_data = pd.DataFrame([{'code': commune.code, 'code_region': commune.codeRegion, 'code_departement': commune.codeDepartement, 'nom': commune.nom, 'codes_postaux': ','.join(commune.codesPostaux)} for commune in api_communes])

        # Appliquer les fusions de Paris
        csv_data = self.__handle_paris_fusion(csv_data)

        # Fusionner les données de l'API avec les données CSV modifiées
        merged_data = pd.merge(api_data, csv_data, left_on='code', right_on='Code géographique', how='outer')
        merged_data = merged_data.drop(['Libellé géographique', 'Code géographique', 'Région', 'Département'], axis=1)

        # Appliquer des types de données, si nécessaire
        merged_data = self.__apply_data_types(merged_data)
            
        # Colonnes à vérifier pour les valeurs NaN ou vides
        columns_to_check = ['code', 'code_region', 'code_departement', 'nom', 'codes_postaux']

        # Supprimer les lignes contenant des NaN dans les colonnes spécifiées
        merged_data = merged_data.dropna(subset=columns_to_check, how='any')

        # Nettoyer les champs pour supprimer les espaces et les lignes vides
        for column in columns_to_check:
            merged_data[column] = merged_data[column].astype(str).str.strip()  # Convertir en string et supprimer les espaces
        merged_data = merged_data[~merged_data[columns_to_check].replace('', pd.NA).isna().any(axis=1)]
        
        # Sauvegarder le résultat fusionné dans un nouveau CSV
        self.__save_data_to_csv(merged_data, 'docs/communes.csv')


    def getDownloadCheckAndMergeData(self):
        
        self.__download_file(self.download_url, "docs/base-pop-historiques-1876-2021.xlsx")
        
        self.__clean_and_convert_excel_to_csv(self.excel_path, self.output_csv_path)

        # Comparer et fusionner les données
        api_communes = self.fetcher.get_all_communes()
        api_regions = self.fetcher.get_all_regions()
        api_departements = self.fetcher.get_all_departements()

        # Convertissez les données en CSV
        self.__save_data_to_csv(api_regions, 'docs/regions.csv')
        self.__save_data_to_csv(api_departements, 'docs/departements.csv')
        self.__compare_and_merge_commune_data(api_communes, self.output_csv_path)