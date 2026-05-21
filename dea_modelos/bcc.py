import numpy as np
from pulp import *
import ipywidgets as widgets
from IPython.display import display, clear_output
from .utils import cargar_archivo, mostrar_tabla


def resolver_bcc(df, col_dmu, inputs, outputs, orientacion):
    n = len(df)
    dmu_names = df[col_dmu].values
    X = df[inputs].values.T
    Y = df[outputs].values.T
    m, s = len(inputs), len(outputs)
    resultados = {
        'eficiencia': {},
        'factor_expansion': {},
        'referentes': {},
        'metas_inputs': {},
        'metas_outputs': {}
    }
    EPS = 1e-6

    for k in range(n):
        if orientacion == "Input":
            prob = LpProblem(f"BCC_Input_{k}", LpMinimize)
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
            theta_opt = value(theta)
            eficiencia = theta_opt
            factor_exp = 1.0 / theta_opt if theta_opt > 0 else 0
            lambdas_opt = [value(l) for l in lambdas]
            holg_in = [value(s) for s in s_menos]
            holg_out = [value(s) for s in s_plus]
            metas_input = {inputs[i]: theta_opt * X[i,k] - holg_in[i] for i in range(m)}
            metas_output = {outputs[r]: Y[r,k] + holg_out[r] for r in range(s)}
        else:
            prob = LpProblem(f"BCC_Output_{k}", LpMaximize)
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
            factor_exp = phi_opt
            lambdas_opt = [value(l) for l in lambdas]
            holg_in = [value(s) for s in s_menos]
            holg_out = [value(s) for s in s_plus]
            metas_input = {inputs[i]: X[i,k] - holg_in[i] for i in range(m)}
            metas_output = {outputs[r]: phi_opt * Y[r,k] + holg_out[r] for r in range(s)}

        resultados['eficiencia'][dmu_names[k]] = eficiencia
        resultados['factor_expansion'][dmu_names[k]] = factor_exp
        resultados['referentes'][dmu_names[k]] = {
            dmu_names[j]: lambdas_opt[j] for j in range(n) if lambdas_opt[j] > 1e-6
        }
        resultados['metas_inputs'][dmu_names[k]] = metas_input
        resultados['metas_outputs'][dmu_names[k]] = metas_output
    return resultados


def run_bcc():
    """Ejecutar la herramienta BCC interactiva en Google Colab."""
    df_proc, variables, dmus = cargar_archivo()

    inputs_sel = widgets.SelectMultiple(options=list(variables), description='Inputs:')
    outputs_sel = widgets.SelectMultiple(options=list(variables), description='Outputs:')
    orientacion_sel = widgets.RadioButtons(options=['Input', 'Output'], description='Orientación:', value='Input')
    display(inputs_sel, outputs_sel, orientacion_sel)

    btn = widgets.Button(description="Resolver BCC")
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
                resultados = resolver_bcc(df_proc, 'DMU', inputs, outputs, orientacion)
                print(f"\nMODELO BCC (VRS) - Orientación {orientacion}\n")
                mostrar_tabla(resultados, inputs, outputs, dmus, orientacion)
            except Exception as e:
                print(f"Error: {e}")

    btn.on_click(on_click)
    display(btn, out)
