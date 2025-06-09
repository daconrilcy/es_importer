class DomAttribute:
    """
    Représente un attribut HTML de type data-*, ex : data-user-id="123".
    """

    def __init__(self, name: str, value: str):
        if not name.startswith("data-"):
            name = "data-" + name.lstrip('-')
        self.name = name
        self.value = value

    def __repr__(self):
        return f'{self.name}="{self.value}"'