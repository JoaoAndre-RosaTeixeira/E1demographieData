import requests
from common.api.classObject import Region, Departement, Commune


class GeographicApi:
    GEO_API_URL = 'https://geo.api.gouv.fr'
    
    @staticmethod
    def get_all_communes():
        response = requests.get(f'{GeographicApi.GEO_API_URL}/communes')
        if response.status_code == 200:
            communes_data = response.json()
            return [Commune(nom=commune['nom'], code=commune['code'], codeDepartement=commune['codeDepartement'], codeRegion=commune['codeRegion'], codesPostaux=commune['codesPostaux']) for commune in communes_data]
        else:
            raise Exception("Failed to fetch data: ", response.status_code)

    @staticmethod
    def get_all_regions():
        response = requests.get(f'{GeographicApi.GEO_API_URL}/regions')
        regions_data = response.json()
        return [Region(nom=region['nom'], code=region['code']) for region in regions_data]

    @staticmethod
    def get_all_departements():
        response = requests.get(f'{GeographicApi.GEO_API_URL}/departements')
        departements_data = response.json()
        return [Departement(nom=dept['nom'], code=dept['code'], code_region=dept['codeRegion']) for dept in departements_data]

    @staticmethod
    def get_departements_by_region_code(region_code):
        url = f'{GeographicApi.GEO_API_URL}/regions/{region_code}/departements'
        response = requests.get(url)
        departements_data = response.json()
        return [Departement(nom=dept['nom'], code=dept['code']) for dept in departements_data]

    @staticmethod
    def get_communes_by_departement_code(departement_code):
        url = f'{GeographicApi.GEO_API_URL}/departements/{departement_code}/communes'
        response = requests.get(url)
        communes_data = response.json()
        return [Commune(nom=commune['nom'], code=commune['code']) for commune in communes_data]

    


