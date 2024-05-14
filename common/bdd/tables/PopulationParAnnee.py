from common.bdd.tables.Base  import *
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, String, Integer

class PopulationParAnnee(Base):
        __tablename__ = 'population_par_annee'
        code_commune = Column(String(10), ForeignKey('communes.code'), primary_key=True)
        annee = Column(Integer, primary_key=True)
        population = Column(Integer)
        commune = relationship("Commune", back_populates="populations")