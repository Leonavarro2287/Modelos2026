# =============================================================================
# PAQUETE MODELOS DE DECISIÓN - VERSIÓN SIMPLE
# =============================================================================

!pip install git+https://github.com/heguevel/Modelos2026.git

from Modelos2026.normalizador import ModelosNormalizacion
import pandas as pd
import numpy as np
from google.colab import files
from openpyxl.utils import get_column_letter

def analizar():
    # Subir archivo
    uploaded = files.upload()
    df = pd.read_excel(list(uploaded.keys())[0])
    
    # Mostrar columnas
    print("\nColumnas:", list(df.columns))
    
    # Preguntar
    id_col = input("\nColumna identificadora (ej: País, Proyecto): ")
    if id_col not in df.columns:
        id_col = df.columns[0]
    
    criterios = input("Columnas criterio (separadas por coma): ").split(',')
    criterios = [c.strip() for c in criterios if c.strip() in df.columns and c.strip() != id_col]
    
    # Transformar
    df2 = df[[id_col] + criterios].copy()
    for col in criterios:
        if input(f"{col} es MIN? (s/n): ").lower() == 's':
            df2[col] = 1 / df2[col]
        if df2[col].min() < 0:
            df2[col] = df2[col] + abs(df2[col].min()) + 1
    
    # Normalizar
    motor = ModelosNormalizacion()
    refs = {c: [df2[c].min(), df2[c].max(), df2[c].quantile(0.75), df2[c].max()] for c in criterios}
    norm = motor.ejecutar_todo(df=df2[criterios], minimo=[], metas_rim=refs, n_intervalos_oecd=4)
    
    # Elegir normalización para cada ponderación
    print("\nMétodos:", list(norm.keys()))
    eleccion = {}
    for m in ['Uniforme', 'DS', 'Entropia', 'CRITIC']:
        eleccion[m] = list(norm.keys())[int(input(f"{m} - Número: "))-1]
    
    # Calcular
    alt = df2[id_col].tolist()
    n = len(criterios)
    resultados = {}
    
    # Uniforme
    mat = norm[eleccion['Uniforme']][criterios].copy()
    w = [1/n]*n
    p = mat.dot(w).values
    resultados['Uniforme'] = {'pesos': w, 'puntajes': p, 'ranking': pd.Series(p).rank(ascending=False).astype(int)}
    
    # DS
    mat = norm[eleccion['DS']][criterios].copy()
    sigma = mat.std()
    w = (sigma / sigma.sum()).values
    p = mat.dot(w).values
    resultados['DS'] = {'pesos': w, 'puntajes': p, 'ranking': pd.Series(p).rank(ascending=False).astype(int)}
    
    # Entropía
    mat = norm[eleccion['Entropia']][criterios].copy()
    m = len(mat)
    k = 1/np.log(m)
    ent = {c: 1 - (-k * (mat[c] * np.log(mat[c]+1e-12)).sum()) for c in criterios}
    w = np.array([ent[c]/sum(ent.values()) for c in criterios])
    p = mat.dot(w).values
    resultados['Entropia'] = {'pesos': w, 'puntajes': p, 'ranking': pd.Series(p).rank(ascending=False).astype(int)}
    
    # CRITIC
    mat = norm[eleccion['CRITIC']][criterios].copy()
    corr = mat.corr()
    sigma = mat.std()
    C = {c: sigma[c] * (1 - corr[c]).sum() for c in criterios}
    w = np.array([C[c]/sum(C.values()) for c in criterios])
    p = mat.dot(w).values
    resultados['CRITIC'] = {'pesos': w, 'puntajes': p, 'ranking': pd.Series(p).rank(ascending=False).astype(int)}
    
    # Estadísticas
    stats = []
    for c in criterios:
        d = df2[c]
        stats.append({'Criterio': c, 'Media': round(d.mean(),4), 'Mediana': round(d.median(),4),
                     'Min': round(d.min(),4), 'Max': round(d.max(),4), 'DS': round(d.std(),4)})
    df_stats = pd.DataFrame(stats)
    
    # Rankings
    df_rank = pd.DataFrame({id_col: alt})
    for m, r in resultados.items():
        df_rank[f'Rank_{m}'] = r['ranking']
    
    # Excel
    out = "Informe.xlsx"
    with pd.ExcelWriter(out, engine='openpyxl') as w:
        df.to_excel(w, sheet_name='1_Original', index=False)
        df2.to_excel(w, sheet_name='2_Transformado', index=False)
        df_stats.to_excel(w, sheet_name='3_Estadisticas', index=False)
        
        # Normalizaciones juntas
        norm_list = []
        for nom, mat in norm.items():
            m = mat.copy()
            m.insert(0, id_col, alt)
            norm_list.append(pd.DataFrame([[f"NORM: {nom}"]], columns=[id_col]))
            norm_list.append(m.round(4))
            norm_list.append(pd.DataFrame([[]]))
        pd.concat(norm_list, ignore_index=True).to_excel(w, sheet_name='4_Normalizaciones', index=False, header=False)
        
        # Ponderaciones juntas
        pond_list = []
        for nom, r in resultados.items():
            pond_list.append(pd.DataFrame([[f"POND: {nom}"]], columns=['A']))
            pond_list.append(pd.DataFrame([["Pesos"]], columns=['A']))
            pond_list.append(pd.DataFrame({'Criterio': criterios, 'Peso': np.round(r['pesos'],4)}))
            pond_list.append(pd.DataFrame([["Puntajes"]], columns=['A']))
            pond_list.append(pd.DataFrame({id_col: alt, 'Puntaje': np.round(r['puntajes'],4), 'Ranking': r['ranking']}))
            pond_list.append(pd.DataFrame([[]]))
        pd.concat(pond_list, ignore_index=True).to_excel(w, sheet_name='5_Ponderaciones', index=False, header=False)
        
        df_rank.to_excel(w, sheet_name='6_Rankings', index=False)
    
    # Ajustar columnas
    from openpyxl import load_workbook
    wb = load_workbook(out)
    for ws in wb:
        for col in ws.columns:
            max_len = 0
            for cell in col:
                if cell.value:
                    max_len = max(max_len, min(len(str(cell.value)), 40))
            ws.column_dimensions[get_column_letter(col[0].column)].width = max_len + 2
    wb.save(out)
    
    files.download(out)
    print("\n✅ Listo!")

# =============================================================================
# EJECUTAR
# =============================================================================
analizar()
