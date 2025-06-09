from typing import List, Union, Optional, Any
from models.web_viewer.dom_objects.base import DomObject

from models.web_viewer.web_config import CSS_GLOBAL

class DomFlexObject(DomObject):
    """
    Classe mère pour des objets DOM affichés dans une grille HTML gérée par du flex CSS.
    Permet d'adapter dynamiquement les classes CSS en fonction du nombre de colonnes et lignes.
    - Ajoute automatiquement les classes de base 'csv-col' et 'colx-md-N'.
    - Ajoute la classe 'reduced' si le nombre de colonnes dépasse le maximum autorisé.
    Les noms de classes CSS de base sont modifiables via le fichier de config web_config.py.
    """

    def __init__(self,
                 n_cols: int,
                 n_rows: Optional[int] = None,
                 max_cols: int = 8,
                 max_rows: Optional[int] = None,
                 base_classes: Union[str, List[str]] = None,
                 extra_classes: Union[str, List[str]] = None,
                 attributes: Optional[List] = None,
                 value: Any = None
                 ):
        """
        :param n_cols: Nombre de colonnes des données à afficher
        :param n_rows: Nombre de lignes (optionnel)
        :param max_cols: Nombre maximum de colonnes autorisé pour l'affichage
        :param max_rows: Nombre maximum de lignes (optionnel)
        :param base_classes: Classes CSS de base supplémentaires
        :param extra_classes: Classes CSS additionnelles
        :param attributes: Liste d'attributs DomAttribute
        """
        self.n_cols = n_cols
        self.n_rows = n_rows
        self.max_cols = max_cols
        self.max_rows = max_rows
        self.reduced = False

        # Détermination des classes CSS de base
        base = [f"{CSS_GLOBAL['COL_CSS_PREFIX']}{n_cols}"]
        if base_classes:
            if isinstance(base_classes, str):
                base += base_classes.split()
            else:
                base += list(base_classes)

        # Ajout automatique de la classe reduced si besoin
        if n_cols > max_cols:
            self.reduced = True
            base.append(CSS_GLOBAL["REDUCED_CSS_CLASS"])

        super().__init__(base_classes=base, extra_classes=extra_classes, attributes=attributes, value=value)
