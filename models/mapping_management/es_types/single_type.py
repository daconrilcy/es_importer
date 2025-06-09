class EsType:
    def __init__(self, name: str, category: str = None, description: str = None):
        self.name = name
        self.category = category
        self.description = description

    def __repr__(self):
        return f"EsType(name={self.name}, category={self.category}, description={self.description})"
