from setuptools import setup, find_packages

setup(
    name="dea_modelos",
    version="1.0.0",
    description="Modelos DEA: CCR, BCC, Aditivo y Eficiencia de Escala",
    packages=find_packages(),
    install_requires=[
        "pulp",
        "openpyxl",
        "pandas",
        "numpy",
        "ipywidgets",
    ],
)
