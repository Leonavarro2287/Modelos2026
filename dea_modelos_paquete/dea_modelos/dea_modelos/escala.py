import numpy as np
from pulp import *
import ipywidgets as widgets
from IPython.display import display, clear_output
from .utils import cargar_archivo, mostrar_tabla_escala


def _resolver_ccr_escala(df, col_dmu, inputs, outputs, orientacion):
    n = len(df)
    dmu_names = df[col_dmu].values
    X = df[inputs].values.T
    Y = df[outputs].values.T
    m, s = len(inputs), len(outputs)
    resultados = {'eficiencia': {}, 'referentes': {}}
    EPS = 1e-6

    for k in range(n):
        if orientacion == "Input":
            prob = LpProblem(f"CCR_ES_Input_{k}", LpMinimize)
            theta = LpVariable("theta", lowBound=0, upBound=1)
            lambdas = [LpVariable(f"l_{j}", lowBound=0) for j in range(n)]
            s_menos = [LpVariable(f"s_in_{i}", lowBound=0) for i in range(m)]
            s_plus = [LpVariable(f"s_out_{r}", lowBound=0) for r in range(s)]
            prob += theta + EPS * (lpSum(s_menos) + lpSum(s_plus))
            for i in range(m):
                prob += lpSum(lambdas[j]*X[i,j] for j in range(n)) + s_menos[i] == theta * X[i,k]
            for r in range(s):
                prob += lpSum(lambdas[j]*Y[r,j] for j in range(n)) - s_plus[r] == Y[r,k]
            prob.solve(PULP_CBC_CMD(msg=0))
            eficiencia = value(theta)
            lambdas_opt = [value(l) for l in lambdas]
        else:
            prob = LpProblem(f"CCR_ES_Output_{k}", LpMaximize)
            phi = LpVariable("phi", lowBound=1)
            lambdas = [LpVariable(f"l_{j}", lowBound=0) for j in range(n)]
            s_menos = [LpVariable(f"s_in_{i}", lowBound=0) for i in range(m)]
            s_plus = [LpVariable(f"s_out_{r}", lowBound=0) for r in range(s)]
            prob += phi - EPS * (lpSum(s_menos) + lpSum(s_plus))
            for i in range(m):
                prob += lpSum(lambdas[j]*X[i,j] for j in range(n)) + s_menos[i] == X[i,k]
            for r in range(s):
                prob += lpSum(lambdas[j]*Y[r,j] for j in range(n)) - s_plus[r] == phi * Y[r,k]
            prob.solve(PULP_CBC_CMD(msg=0))
            phi_opt = value(phi)
            eficiencia = 1.0 / phi_opt if phi_opt > 0 else 0
            lambdas_opt = [value(l) for l in lambdas]

        resultados['eficiencia'][dmu_names[k]] = eficiencia
        resultados['referentes'][dmu_names[k]] = {
            dmu_names[j]: lambdas_opt[j] for j in range(n) if lambdas_opt[j] > 1e-6
        }
    return resultados


def _resolver_bcc_escala(df, col_dmu, inputs, outputs, orientacion):
    n = len(df)
    dmu_names = df[col_dmu].values
    X = df[inputs].values.T
    Y = df[outputs].values.T
    m, s = len(inputs), len(outputs)
    resultados = {'eficiencia': {}, 'referentes': {}}
    EPS = 1e-6

    for k in range(n):
        if orientacion == "Input":
            prob = LpProblem(f"BCC_ES_Input_{k}", LpMinimize)
            theta = LpVariable("theta", lowBound=0, upBound=1)
            lambdas = [LpVariable(f"l_{j}", lowBound=0) for j in range(n)]
            s_menos = [LpVariable(f"s_in_{i}", lowBound=0) for i in range(m)]
            s_plus = [LpVariable(f"s_out_{r}", lowBound=0) for r in range(s)]
            prob += theta + EPS * (lpSum(s_menos) + lpSum(s_plus))
            for i in range(m):
                prob += lpSum(lambdas[j]*X[i,j] for j in range(n)) + s_menos[i] == theta * X[i,k]
            for r in range(s):
                prob += lpSum(lambdas[j]*Y[r,j] for j in range(n)) - s_plus[r] == Y[r,k]
            prob += lpSum(lambdas) == 1
            prob.solve(PULP_CBC_CMD(msg=0))
            eficiencia = value(theta)
            lambdas_opt = [value(l) for l in lambdas]
        else:
            prob = LpProblem(f"BCC_ES_Output_{k}", LpMaximize)
            phi = LpVariable("phi", lowBound=1)
            lambdas = [LpVariable(f"l_{j}", lowBound=0) for j in range(n)]
            s_menos = [LpVariable(f"s_in_{i}", lowBound=0) for i in range(m)]
            s_plus = [LpVariable(f"s_out_{r}", lowBound=0) for r in range(s)]
            prob += phi - EPS * (lpSum(s_menos) + lpSum(s_plus))
            for i in range(m):
                prob += lpSum(lambdas[j]*X[i,j] for j in range(n)) + s_menos[i] == X[i,k]
            for r in range(s):
                prob += lpSum(lambdas[j]*Y[r,j] for j in range(n)) - s_plus[r] == phi * Y[r,k]
            prob += lpSum(lambdas) == 1
            prob.solve(PULP_CBC_CMD(msg=0))
            phi_opt = value(phi)
            eficiencia = 1.0 / phi_opt if phi_opt > 0 else 0
            lambdas_opt = [value(l) for l in lambdas]

        resultados['eficiencia'][dmu_names[k]] = eficiencia
        resultados['referentes'][dmu_names[k]] = {
            dmu_names[j]: lambdas_opt[j] for j in range(n) if lambdas_opt[j] > 1e-6
        }
    return resultados


def run_escala():
    """Ejecutar la herramienta Eficiencia de Escala interactiva en Google Colab."""
    df_proc, variables, dmus = cargar_archivo()

    inputs_sel = widgets.SelectMultiple(options=list(variables), description='Inputs:')
    outputs_sel = widgets.SelectMultiple(options=list(variables), description='Outputs:')
    orientacion_sel = widgets.RadioButtons(options=['Input', 'Output'], description='Orientación:', value='Input')
    display(inputs_sel, outputs_sel, orientacion_sel)

    btn = widgets.Button(description="Calcular Eficiencia de Escala")
    out = widgets.Output()

    def on_click(b):
        with out:
            clear_output()
            try:
                inputs = list(inputs_sel.value)
                outputs = list(outputs_sel.value)
                orientacion = orientacion_sel.value
                if not inputs or not outputs:
                    print("Selecciona inputs y outputs")
                    return
                res_ccr = _resolver_ccr_escala(df_proc, 'DMU', inputs, outputs, orientacion)
                res_bcc = _resolver_bcc_escala(df_proc, 'DMU', inputs, outputs, orientacion)
                print(f"\nEFICIENCIA DE ESCALA - Orientación {orientacion}\n")
                mostrar_tabla_escala(
                    dmus,
                    res_ccr['eficiencia'], res_ccr['referentes'],
                    res_bcc['eficiencia'], res_bcc['referentes']
                )
            except Exception as e:
                print(f"Error: {e}")

    btn.on_click(on_click)
    display(btn, out)
