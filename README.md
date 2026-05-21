# dea_modelos

Paquete Python con modelos DEA (Data Envelopment Analysis) para usar en Google Colab.

## Instalación

```python
!pip install git+https://github.com/Leonavarro2287/Modelos2026.git -q
```

## Modelos disponibles

| Herramienta | Descripción |
|---|---|
| `run_ccr()` | Modelo CCR (CRS) — Orientación Input u Output |
| `run_bcc()` | Modelo BCC (VRS) — Orientación Input u Output |
| `run_aditivo()` | Modelo Aditivo (ADD-VRS) |
| `run_escala()` | Eficiencia de Escala (CCR + BCC) |

## Uso en Colab

Cada herramienta se usa en una celda separada:

```python
# Celda 1 — CCR
from dea_modelos import run_ccr
run_ccr()
```

```python
# Celda 2 — BCC
from dea_modelos import run_bcc
run_bcc()
```

```python
# Celda 3 — Modelo Aditivo
from dea_modelos import run_aditivo
run_aditivo()
```

```python
# Celda 4 — Eficiencia de Escala
from dea_modelos import run_escala
run_escala()
```

## Formato del archivo Excel

- Variables en **filas** (primera columna = nombre de la variable)
- DMUs en **columnas** (primera fila = nombre de cada DMU)
- Sin celdas combinadas, sin hojas múltiples
