from typing import List, Union, Any

from models.web_viewer.dom_objects.base.dom_attributes import DomAttribute
from models.web_viewer.dom_objects.base.predefined_attributes import PREDEFINED_ATTRIBUTES


class DomObject:
    """
    Objet destiné à être utilisé dans un template Flask/Jinja2 pour renseigner le DOM HTML.
    Permet de gérer des classes CSS de base (communes), des classes CSS additionnelles (spécifiques),
    ainsi qu'une collection d'attributs HTML personnalisés (data-*).
    """

    def __init__(self,
                 n_cols: int = 12,
                 n_rows: int = 7,
                 original_indice_col: int = 0,
                 original_indice_row: int = 0,
                 base_classes: Union[str, List[str]] = None,
                 extra_classes: Union[str, List[str]] = None,
                 attributes: List[DomAttribute] = None,
                 value: Any = None,
                 parent_class: str = None
                 ):
        """
        :param base_classes: Classes CSS de base (communes à plusieurs objets)
        :param extra_classes: Classes CSS additionnelles (spécifiques à cet objet)
        :param attributes: Liste d'objets DomAttribute
        """
        self.n_cols = n_cols
        self.n_rows = n_rows
        self.original_indice_col = original_indice_col
        self.original_indice_row = original_indice_row
        self.base_classes = self._to_list(base_classes)
        self.extra_classes = self._to_list(extra_classes)
        self._attributes = attributes or []
        self.value = value
        self.parent_class = parent_class

    @property
    def n_cols(self):
        """
        Nombre total de colonnes
        :return:
        """
        return self._n_cols

    @n_cols.setter
    def n_cols(self, total_col: int):
        if total_col is None:
            total_col = 0
        self._n_cols = total_col

    @property
    def n_rows(self) -> int:
        """
        nombre total de rows
        :return:
        """
        return self._n_rows

    @n_rows.setter
    def n_rows(self, total_rows: int):
        if total_rows is None:
            total_rows = 0
        self._n_rows = total_rows

    @property
    def original_indice_col(self):
        """
        Indice Original de colonne
        :return:
        """
        return self._original_indice_col

    @original_indice_col.setter
    def original_indice_col(self, original_indice_col: int):
        if original_indice_col is None:
            original_indice_col = 0
        self._original_indice_col = original_indice_col

    @property
    def original_indice_row(self):
        """
        indice original de la ligne
        :return:
        """
        return self._original_indice_row

    @original_indice_row.setter
    def original_indice_row(self, original_indice_row: int):
        if original_indice_row is None:
            original_indice_row = 0
        self._original_indice_row = original_indice_row

    @property
    def value(self) -> Any:
        """
        Renvoie la value de la cellule
        :return:
        """
        return self._value

    @value.setter
    def value(self, value: Any):

        self._value = value

    @staticmethod
    def _to_list(val):
        if val is None:
            return []
        if isinstance(val, str):
            return val.split()
        return list(val)

    @staticmethod
    def set_default_attributes():
        """
        Définit les attributes pre enregistrés
        :return:
        """
        for attr in PREDEFINED_ATTRIBUTES:
            data_name = f"data-{attr.replace('_', '-')}"
            prop = property(_make_getter(data_name), _make_setter(data_name))
            setattr(DomObject, attr, prop)

    @property
    def css_classes(self) -> str:
        """Renvoie la liste complète des classes CSS (base + additionnelles) sous forme de string."""
        return ' '.join(self.base_classes + self.extra_classes)

    @property
    def attributes(self) -> List[DomAttribute]:
        """Renvoie la liste des attributs DomAttribute."""
        return self._attributes

    @property
    def parent_class(self) -> str:
        """Renvoie la classe parente de l'objet."""
        return self._parent_class

    @parent_class.setter
    def parent_class(self, parent_class: str):
        self._parent_class = parent_class

    def add_class(self, css_class: str, base: bool = False):
        """Ajoute une classe CSS à la liste de base ou additionnelle."""
        if base:
            if css_class not in self.base_classes:
                self.base_classes.append(css_class)
        else:
            if css_class not in self.extra_classes:
                self.extra_classes.append(css_class)

    def remove_class(self, css_class: str):
        """Supprime une classe CSS de la liste de base ou additionnelle."""
        if css_class in self.base_classes:
            self.base_classes.remove(css_class)
        if css_class in self.extra_classes:
            self.extra_classes.remove(css_class)

    def add_attribute(self, name: str, value: str):
        """Ajoute ou remplace un attribut data-* à l'objet."""
        for attr in self._attributes:
            if attr.name == name:
                attr.value = value
                return
        self._attributes.append(DomAttribute(name, value))

    def remove_attribute(self, name: str):
        """Supprime un attribut data-* par son nom."""
        self._attributes = [attr for attr in self._attributes if attr.name != name]

    def __iter__(self):
        """Permet l'itération sur les attributs (utile pour le template Jinja2)."""
        return iter(self._attributes)

    def _get_attribute(self, name):
        for dom_attr in self._attributes:
            if dom_attr.name == name:
                return dom_attr.value
        return None

    def _set_attribute(self, name, value):
        for attr in self._attributes:
            if attr.name == name:
                attr.value = value
                return
        self._attributes.append(DomAttribute(name, value))

    def __repr__(self):
        return f'<DomObject classes="{self.css_classes}" attributes={[repr(a) for a in self._attributes]}>'


# Génération dynamique des propriétés pour chaque attribut préformaté (hors de la classe)


def _make_getter(data_name):
    def getter(self):
        """
        Crée les getters pour la classe hors de la classe
        :param self:
        :return:
        """
        return self._get_attribute(data_name)

    return getter


def _make_setter(data_name):
    def setter(self, value):
        """
        Crée les setters pour les attributs de la classe hors de la classe
        :param self:
        :param value:
        :return:
        """
        self._set_attribute(data_name, value)

    return setter


# Appel automatique pour garantir la présence des propriétés dynamiques
DomObject.set_default_attributes()
