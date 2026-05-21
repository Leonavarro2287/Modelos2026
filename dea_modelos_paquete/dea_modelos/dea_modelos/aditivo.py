import numpy as np
from pulp import *
import ipywidgets as widgets
from IPython.display import display, clear_output
from .utils import cargar_archivo, mostrar_tabla_aditivo


def resolver_aditivo_vrs(df, col_dmu, inputs, outputs):
    n = len(df)
    dmu_names = df[col_dmu].values
    X = df[inputs].values.T
    Y = df[outputs].values.T
    m, s = len(inputs), len(outputs)
    resultados = {
        'ineficiencia': {},
        'referentes': {},
        'metas_inputs': {},
        'metas_outputs': {}
    }

    for k in range(n):
        prob = LpProblem(f"Aditivo_VRS_{k}", LpMaximize)
        lambdas = [LpVariable(f"l_{j}", lowBound=0) for j in range(n)]
        s_menos = [LpVariable(f"s_in_{i}", lowBound=0) for i in range(m)]
        s_plus = [LpVariable(f"s_out_{r}", lowBound=0) for r in range(s)]
        prob += lpSum(s_menos) + lpSum(s_plus)
        for i in range(m):
            prob += lpSum(lambdas[j]*X[i,j] for j in range(n)) + s_menos[i] == X[i,k]
        for r in range(s):
            prob += lpSum(lambdas[j]*Y[r,j] for j in range(n)) - s_plus[r] == Y[r,k]
        prob += lpSum(lambdas) == 1
        prob.solve(PULP_CBC_CMD(msg=0))

        lambdas_opt = [value(l) for l in lambdas]
        holg_in = [value(s) for s in s_menos]
        holg_out = [value(s) for s in s_plus]
        suma_holg = sum(holg_in) + sum(holg_out)

        resultados['ineficiencia'][dmu_names[k]] = suma_holg
        resultados['referentes'][dmu_names[k]] = {
            dmu_names[j]: lambdas_opt[j] for j in range(n) if lambdas_opt[j] > 1e-6
        }
        resultados['metas_inputs'][dmu_names[k]] = {inputs[i]: X[i,k] - holg_in[i] for i in range(m)}
        resultados['metas_outputs'][dmu_names[k]] = {outputs[r]: Y[r,k] + holg_out[r] for r in range(s)}
    return resultados


def run_aditivo():
    """Ejecutar la herramienta Modelo Aditivo interactiva en Google Colab."""
    df_proc, variables, dmus = cargar_archivo()

    inputs_sel = widgets.SelectMultiple(options=list(variables), description='Inputs:')
    outputs_sel = widgets.SelectMultiple(options=list(variables), description='Outputs:')
    display(inputs_sel, outputs_sel)

    btn = widgets.Button(description="Resolver Aditivo (VRS)")
    out = widgets.Output()

    def on_click(b):
        with out:
            clear_output()
            try:
                inputs = list(inputs_sel.value)
                outputs = list(outputs_sel.value)
                if not inputs or not outputs:
                    print("Selecciona inputs y outputs")
                    return
                resultados = resolver_aditivo_vrs(df_proc, 'DMU', inputs, outputs)
                print("\nMODELO ADITIVO (ADD-VRS) - Rendimientos Variables a Escala\n")
                mostrar_tabla_aditivo(resultados, inputs, outputs, dmus)
            except Exception as e:
                print(f"Error: {e}")

    btn.on_click(on_click)
    display(btn, out)
