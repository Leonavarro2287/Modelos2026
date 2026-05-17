# Modelos de Decisión 2026 

Este repositorio contiene los recursos y modelos desarrollados hasta el momento en la materia, y se divide en dos herramientas:

Herramienta 1: Estadistica Descriptiva/Normalizacion/Ponderacion/Agregacion

Herramienta 2: DEA, Modelos CCR, BCC, Modelo Aditivo y calculadora de Eficiencia de Escala (CCR + BCC)


## 📋 Recomendaciones Previas

Las tablas de excel cargadas deben contener los datos limpios y ya transformados (en el caso de la linea de codigo de Agregacion, para suma ponderada y media geometrica ponderada se pueden transformar criterios de minimo a maximo automaticamente, usa la formula aij min/aij)

Los archivos a subir no deben tener celdas combinadas ni varias hojas (solo 1 hoja por archivo). Se recomienda trabajar con textos cortos.

Solo se debe ejecutar cada linea de codigo por separado y seguir las instrucciones que van apareciendo. Es bastante intuitivo. 

Para la normalizacion RIM, se toma por defecto para C y D el ultimo cuartil de los datos, pero se pueden ingresar valores manuales.

La media geometrica ponderada ya tiene incluida la normalizacion aij^peso.

Los metodos que se basan en comparaciones pareadas como AHP permiten la carga manual de datos para armar la matriz

Para seleccionar varios criterios, se debe mantener apretado Control y hacer click con el raton

## 🚀 Ejecución Interactiva

Podes ejecutar y probar el modelo haciendo click en los siguientes enlaces:

<a href="https://colab.research.google.com/drive/1Wt5XtLLFvexj37uL6ubZmLnwLAP4rQYn?authuser=2" 
   target="_blank" 
   rel="noopener noreferrer"
   style="display: inline-block; padding: 10px 20px; background-color: #34a853; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; font-family: sans-serif; margin-right: 10px;">
   Herramienta Estadistica Descriptiva/Normalizacion/Ponderacion/Agregacion
</a>

<a href="https://colab.research.google.com/drive/1fVdxArkOfyguIZvEM-27IUFyO_YWWyZQ?authuser=2" 
   target="_blank" 
   rel="noopener noreferrer"
   style="display: inline-block; padding: 10px 20px; background-color: #34a853; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; font-family: sans-serif;">
   Herramienta DEA
</a>


## 🛠️ Tecnologías y Librerías Utilizadas

El cuaderno está desarrollado en Python 3 y requiere los siguientes paquetes principales para su funcionamiento:

* **PuLP**: Para la formulación y resolución de los problemas de optimización lineal.
* **Pandas**: Para la manipulación, limpieza y estructuración de los datos de entrada (DataFrames).
* **Numpy**: Para el soporte de vectores y operaciones matemáticas eficientes.
* **Openpyxl**: Para la lectura y exportación de archivos de datos en formato Excel.



