from setuptools import setup, find_packages

setup(
    name="modelos_decision",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0",
        "openpyxl>=3.0.0",
    ],
    author="Tu Nombre",
    description="Paquete para análisis de normalización y ponderación",
)
