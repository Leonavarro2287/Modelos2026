import pandas as pd
import io
from IPython.display import display, HTML


def preparar_datos(df_original):
    vars_fila = df_original.iloc[:, 0].values
    dmus = df_original.columns[1:].values
    data = {v: [] for v in vars_fila}
    for dmu in dmus:
        for v in vars_fila:
            val = df_original[df_original.iloc[:, 0] == v][dmu].values[0]
            data[v].append(val)
    df_proc = pd.DataFrame(data, index=dmus)
    df_proc.index.name = 'DMU'
    df_proc.reset_index(inplace=True)
    return df_proc, vars_fila, dmus


def mostrar_tabla(resultados, inputs, outputs, dmus, orientacion):
    if orientacion == "Input":
        rows = ['θ*', 'λ*'] + [f"{inp}*" for inp in inputs]
    else:
        rows = ['φ*', 'θ*', 'λ*'] + [f"{out}*" for out in outputs]

    data = {row: [] for row in rows}

    for dmu in dmus:
        eff = resultados['eficiencia'][dmu]
        factor = resultados['factor_expansion'][dmu]

        if orientacion == "Output":
            data['φ*'].append(f"{factor:.4f}".replace('.', ','))

        data['θ*'].append(f"{eff:.4f}".replace('.', ','))

        if eff < 0.9999:
            refs = resultados['referentes'][dmu]
            if refs:
                items = sorted(refs.items(), key=lambda x: x[1], reverse=True)
                texto_html = "<br>".join([f"{r} ({w:.2f})".replace('.', ',') for r, w in items])
                data['λ*'].append(texto_html)
            else:
                data['λ*'].append("")
        else:
            data['λ*'].append("")

        if orientacion == "Input":
            if eff < 0.9999:
                metas = resultados['metas_inputs'][dmu]
                for inp in inputs:
                    data[f"{inp}*"].append(f"{metas[inp]:.2f}".replace('.', ','))
            else:
                for inp in inputs:
                    data[f"{inp}*"].append("")
        else:
            if eff < 0.9999:
                metas = resultados['metas_outputs'][dmu]
                for out in outputs:
                    data[f"{out}*"].append(f"{metas[out]:.2f}".replace('.', ','))
            else:
                for out in outputs:
                    data[f"{out}*"].append("")

    df_resultado = pd.DataFrame(data, index=dmus).T
    html = df_resultado.to_html(escape=False, na_rep='')
    html = html.replace('<td>', '<td style="text-align:center; vertical-align:middle;">')
    display(HTML(html))


def mostrar_tabla_aditivo(resultados, inputs, outputs, dmus):
    rows = ['θ*', 'λ*'] + [f"{inp}*" for inp in inputs] + [f"{out}*" for out in outputs]
    data = {row: [] for row in rows}

    for dmu in dmus:
        inef = resultados['ineficiencia'][dmu]
        data['θ*'].append(f"{inef:.4f}".replace('.', ','))

        if inef > 1e-6:
            refs = resultados['referentes'][dmu]
            if refs:
                items = sorted(refs.items(), key=lambda x: x[1], reverse=True)
                texto_html = "<br>".join([f"{r} ({w:.2f})".replace('.', ',') for r, w in items])
                data['λ*'].append(texto_html)
            else:
                data['λ*'].append("")
            metas_in = resultados['metas_inputs'][dmu]
            for inp in inputs:
                data[f"{inp}*"].append(f"{metas_in[inp]:.2f}".replace('.', ','))
            metas_out = resultados['metas_outputs'][dmu]
            for out in outputs:
                data[f"{out}*"].append(f"{metas_out[out]:.2f}".replace('.', ','))
        else:
            data['λ*'].append("")
            for inp in inputs:
                data[f"{inp}*"].append("")
            for out in outputs:
                data[f"{out}*"].append("")

    df_resultado = pd.DataFrame(data, index=dmus).T
    html = df_resultado.to_html(escape=False, na_rep='')
    html = html.replace('<td>', '<td style="text-align:center; vertical-align:middle;">')
    display(HTML(html))


def mostrar_tabla_escala(dmus, eff_ccr, refs_ccr, eff_bcc, refs_bcc):
    filas = {
        'CCR (θ*)': [],
        'λ* CCR': [],
        'BCC (θ*)': [],
        'λ* BCC': [],
        'ES (Escala)': []
    }
    for dmu in dmus:
        ccr = eff_ccr[dmu]
        bcc = eff_bcc[dmu]
        es = min(ccr / bcc, 1.0) if bcc and bcc > 0 else 0.0

        filas['CCR (θ*)'].append(f"{ccr:.4f}".replace('.', ','))
        filas['BCC (θ*)'].append(f"{bcc:.4f}".replace('.', ','))
        filas['ES (Escala)'].append(f"{es:.4f}".replace('.', ','))

        refs_c = refs_ccr[dmu]
        if refs_c and ccr < 0.9999:
            items = sorted(refs_c.items(), key=lambda x: x[1], reverse=True)
            filas['λ* CCR'].append("<br>".join([f"{r} ({w:.2f})".replace('.', ',') for r, w in items]))
        else:
            filas['λ* CCR'].append("")

        refs_b = refs_bcc[dmu]
        if refs_b and bcc < 0.9999:
            items = sorted(refs_b.items(), key=lambda x: x[1], reverse=True)
            filas['λ* BCC'].append("<br>".join([f"{r} ({w:.2f})".replace('.', ',') for r, w in items]))
        else:
            filas['λ* BCC'].append("")

    df_resultado = pd.DataFrame(filas, index=dmus).T
    html = df_resultado.to_html(escape=False, na_rep='')
    html = html.replace('<td>', '<td style="text-align:center; vertical-align:middle;">')
    display(HTML(html))


def cargar_archivo():
    """Carga un archivo Excel desde Colab y retorna df_orig, df_proc, variables, dmus."""
    from google.colab import files
    print("📂 Sube archivo Excel (variables en filas, DMUs en columnas)")
    uploaded = files.upload()
    filename = list(uploaded.keys())[0]
    df_orig = pd.read_excel(io.BytesIO(uploaded[filename]))
    df_proc, variables, dmus = preparar_datos(df_orig)
    print("Vista previa:")
    display(df_orig)
    return df_proc, variables, dmus
