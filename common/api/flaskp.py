from urllib.parse import quote_plus
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship

# Configuration de l'application Flask
# Configuration de connexion à PostgreSQL
app = Flask(__name__)
password = "^Te+7Qib&Q\"%@X>>"
encoded_password = quote_plus(password)
database_url = f'postgresql+psycopg2://postgres:{encoded_password}@34.155.209.64:5432/dev-ia-e1'
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de SQLAlchemy avec Flask
db = SQLAlchemy(app)

# Définition des modèles
class Commune(db.Model):
    __tablename__ = 'communes'
    code = Column(String(10), primary_key=True)
    nom = Column(String(255), nullable=False)
    codes_postaux = Column(String)
    code_departement = Column(String(10), ForeignKey('departements.code'))
    code_region = Column(String(10), ForeignKey('regions.code'))
    populations = relationship('PopulationParAnnee', order_by='PopulationParAnnee.annee')

class Departement(db.Model):
    __tablename__ = 'departements'
    code = Column(String(10), primary_key=True)
    nom = Column(String(255), nullable=False)
    code_region = Column(String(10), ForeignKey('regions.code'))
    communes = relationship('Commune', backref='departement')

class Region(db.Model):
    __tablename__ = 'regions'
    code = Column(String(10), primary_key=True)
    nom = Column(String(255), nullable=False)
    departements = relationship('Departement', backref='region')

class PopulationParAnnee(db.Model):
    __tablename__ = 'population_par_annee'
    code_commune = Column(String(10), ForeignKey('communes.code'), primary_key=True)
    annee = Column(Integer, primary_key=True)
    population = Column(Integer)

# Configuration des entités avec leurs attributs correspondants
entity_config = {
    'commune': {'model': Commune, 'code_attr': 'codes_postaux', 'population_relationship': 'populations'},
    'departement': {'model': Departement, 'code_attr': 'code', 'population_relationship': 'communes'},
    'region': {'model': Region, 'code_attr': 'code', 'population_relationship': 'departements'}
}

@app.route('/<entity_type>', defaults={'code': None, 'year': None})
@app.route('/<entity_type>/year/<int:year>', defaults={'code': None})
@app.route('/<entity_type>/code/<code>', defaults={'year': None})
@app.route('/<entity_type>/code/<code>/year/<int:year>')
def get_data(entity_type, code, year):
    config = entity_config.get(entity_type)
    if not config:
        return jsonify(message="Invalid entity type"), 400

    model = config['model']
    query = db.session.query(model)

    if code:
        query = query.filter(getattr(model, config['code_attr']) == code)

    entities = query.all()
    if not entities:
        return jsonify(message="No entities found"), 404

    results = []
    for entity in entities:
        entity_data = {
            'nom': entity.nom,
            'code': getattr(entity, config['code_attr']),
            'populations': []
        }

        if entity_type == 'commune':
            populations = entity.populations if year is None else [pop for pop in entity.populations if pop.annee == year]
        else:
            populations = []
            if entity_type == 'departement':
                for commune in entity.communes:
                    populations.extend(commune.populations)
            elif entity_type == 'region':
                for departement in entity.departements:
                    for commune in departement.communes:
                        populations.extend(commune.populations)
                        
        population_summary = {}
        for pop in populations:
            if year and pop.annee != year:
                continue
            if pop.annee in population_summary:
                population_summary[pop.annee] += pop.population
            else:
                population_summary[pop.annee] = pop.population

        entity_data['populations'] = [{'annee': k, 'population': v} for k, v in sorted(population_summary.items())]
        
        results.append(entity_data)

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
