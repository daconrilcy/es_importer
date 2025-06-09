from setuptools import setup, find_packages

setup(
    name="csv_importer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Le Conda",
    description="Un outil d'import CSV vers Elasticsearch",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
