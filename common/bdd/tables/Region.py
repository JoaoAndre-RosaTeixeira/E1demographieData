from common.bdd.tables.Base  import *
from common.bdd.tables.Departement import Departement, Commune
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String


class Region(Base):
        __tablename__ = 'regions'
        code = Column(String(10), primary_key=True)
        nom = Column(String(255), nullable=False)
        departements = relationship("Departement", order_by=Departement.code, back_populates="region")
        departements = relationship("Commune", order_by=Commune.code, back_populates="region")
        
    