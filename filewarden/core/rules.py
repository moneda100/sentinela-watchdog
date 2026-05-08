"""
Módulo que define el modelo de datos para las reglas y centinelas.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

@dataclass
class Rule:
    """
    Define una regla de procesamiento de archivos.
    """
    extension: str
    destination: Path
    action: str
    rename_pattern: str = ""
    
    def __post_init__(self):
        exts = [e.strip().lower() for e in self.extension.split(',')]
        formatted_exts = []
        for e in exts:
            if e and not e.startswith('.'):
                formatted_exts.append(f".{e}")
            elif e:
                formatted_exts.append(e)
        self.extension = ", ".join(formatted_exts)
        
    def matches(self, suffix: str) -> bool:
        """
        Verifica si el sufijo dado coincide con alguna de las extensiones de la regla.
        """
        exts = [e.strip() for e in self.extension.split(',')]
        return suffix.lower() in exts

@dataclass
class Sentinel:
    """
    Representa una carpeta monitoreada (centinela) y sus reglas.
    """
    watch_path: Path
    rules: List[Rule] = field(default_factory=list)
    active: bool = False
    auto_organize: bool = False
