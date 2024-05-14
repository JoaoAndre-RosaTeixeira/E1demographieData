from common.bdd.tables.Base  import Base
from common.bdd.tables.PopulationParAnnee import PopulationParAnnee
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, String, Text

class Commune(Base):
        __tablename__ = 'communes'
        code = Column(String(10), primary_key=True)
        nom = Column(String(255), nullable=False)
        code_departement = Column(String(10), ForeignKey('departements.code'))
        code_region = Column(String(10), ForeignKey('regions.code'))
        codes_postaux = Column(Text)
        departement = relationship("Departement", back_populates="communes")
        region = relationship("Region")
        populations = relationship("PopulationParAnnee", order_by=PopulationParAnnee.annee, back_populates="commune")
