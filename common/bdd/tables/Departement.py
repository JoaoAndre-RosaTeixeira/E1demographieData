from common.bdd.tables.Base  import *
from common.bdd.tables.Commune import Commune
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, String


class Departement(Base):
        __tablename__ = 'departements'
        code = Column(String(10), primary_key=True)
        nom = Column(String(255), nullable=False)
        code_region = Column(String(10), ForeignKey('regions.code'))
        communes = relationship("Commune", order_by=Commune.code, back_populates="departement")
        region = relationship("Region", back_populates="departements")