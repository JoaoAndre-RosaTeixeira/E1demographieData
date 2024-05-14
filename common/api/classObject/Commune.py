
from dataclasses import dataclass

@dataclass
class Commune:
    nom: str
    code: str
    codeDepartement: str
    codeRegion: str
    codesPostaux: list