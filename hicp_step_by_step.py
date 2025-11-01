# hicp_step_by_step.py
# Análisis paso a paso del HICP (Eurostat) para proyecto académico
# Autor: <tu nombre>
# Requisitos: pandas, numpy, matplotlib, openpyxl
# Estructura esperada:
#   tu_proyecto/
#     data/prc_hicp_aind.xlsx
#     outputs/

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings

# Suprimir advertencia repetida de openpyxl sobre "no default style"
warnings.filterwarnings(
    "ignore",
    message="Workbook contains no default style, apply openpyxl's default"
)

# --------------------------
# 0) Configuración de rutas
# --------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Directorios candidatos donde podría estar el archivo de datos
POSSIBLE_DATA_DIRS = [
    os.path.join(SCRIPT_DIR, "data"),
    os.path.join(SCRIPT_DIR, "Data"),
    os.path.join(SCRIPT_DIR, "data base"),
    os.path.join(os.path.dirname(SCRIPT_DIR), "data"),
    SCRIPT_DIR,
]

# Nombre esperado del fichero
FNAME_XLSX = "prc_hicp_aind.xlsx"

# Permitir ruta explícita vía variable de entorno (útil si la carpeta contiene espacios)
env_path = os.environ.get("HICP_XLSX_PATH")
RAW_XLSX = None
DATA_DIR = None

if env_path:
    env_path = os.path.normpath(env_path)
    if os.path.isfile(env_path):
        RAW_XLSX = env_path
        DATA_DIR = os.path.dirname(env_path)

# Buscar en las carpetas candidatas si no se pasó env var o no existe
if RAW_XLSX is None:
    for d in POSSIBLE_DATA_DIRS:
        d_norm = os.path.normpath(d)
        candidate = os.path.join(d_norm, FNAME_XLSX)
        if os.path.isfile(candidate):
            RAW_XLSX = candidate
            DATA_DIR = d_norm
            break

# Si no se encontró, usar por defecto una carpeta 'data' en el mismo directorio del script
if RAW_XLSX is None:
    DATA_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "data"))
    RAW_XLSX = os.path.join(DATA_DIR, FNAME_XLSX)

OUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
CLEAN_CSV = os.path.join(DATA_DIR, "hicp_clean.csv")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

# ------------------------------------
# BLOQUE 1 — Cargar Excel y ver hojas
# ------------------------------------
def load_excel_preview(path_xlsx: str):
    path_xlsx = os.path.normpath(path_xlsx)
    print(f"Intentando abrir el archivo: {path_xlsx}")
    if not os.path.exists(path_xlsx):
        buscados = "\n".join([os.path.normpath(p) for p in POSSIBLE_DATA_DIRS])
        raise FileNotFoundError(
            "No encuentro prc_hicp_aind.xlsx.\n"
            "Rutas buscadas (algunas candidatas):\n"
            f"{buscados}\n\n"
            "Opciones:\n"
            "- Coloca el archivo en una de las carpetas anteriores.\n"
            "- O exporta su ruta completa en la variable de entorno HICP_XLSX_PATH.\n"
            f"- Ruta esperada actualmente: {path_xlsx}"
        )

    xls = pd.ExcelFile(path_xlsx)
    print("Hojas en el archivo:", xls.sheet_names)
    # Elige la primera hoja que NO sea 'Summary'
    candidate_sheets = [s for s in xls.sheet_names if s.strip().lower() != "summary"]
    sheet_name = candidate_sheets[0] if candidate_sheets else xls.sheet_names[0]

    # Leer primero sin cabecera para detectar dónde comienzan los encabezados reales
    df_noheader = pd.read_excel(path_xlsx, sheet_name=sheet_name, header=None, engine="openpyxl")
    header_row = None
    max_score = -1
    import re

    # Buscar en las primeras filas (p. ej. 0..19) la que tenga más años o etiquetas 'time'/'geo'
    for i in range(min(20, len(df_noheader))):
        row = df_noheader.iloc[i].astype(str).fillna("").tolist()
        # contar celdas que son años de 4 dígitos
        year_count = sum(1 for v in row if re.match(r'^\s*\d{4}\s*$', v))
        lowered = [v.strip().lower() for v in row]
        label_score = 0
        if any("time" in v for v in lowered):
            label_score += 2
        if any("geo" in v or "country" in v or "geopolitical" in v for v in lowered):
            label_score += 2
        score = year_count + label_score
        if score > max_score:
            max_score = score
            header_row = i

    if header_row is None or max_score <= 0:
        # fallback: usar la primera fila como header y avisar
        header_row = 0
        print("No encontré fila de cabecera claramente; usaré la primera fila como cabecera.")
    else:
        print(f"Fila de cabecera detectada: {header_row} (score={max_score})")

    # Leer la hoja con la fila de cabecera encontrada
    df_raw = pd.read_excel(path_xlsx, sheet_name=sheet_name, header=header_row, engine="openpyxl")

    # Limpiar filas/columnas totalmente vacías que suelen venir en estas hojas
    df_raw = df_raw.dropna(axis=0, how="all")
    df_raw = df_raw.loc[:, df_raw.notna().any()]

    print("Dimensiones crudas:", df_raw.shape)
    print(df_raw.head(10))
    return df_raw

# ------------------------------------------------------
# BLOQUE 2 — Detectar años y transformar a formato largo
# ------------------------------------------------------
def wide_to_long(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    # Detectar columnas de años (4 dígitos)
    year_cols = []
    for c in df.columns:
        try:
            num = int(str(c)[:4])
            if 1900 <= num <= 2100:
                year_cols.append(c)
        except:
            pass
    if not year_cols:
        raise ValueError("No detecté columnas de años (ej. 2016, 2017, ...). Revisa la hoja elegida.")

    # Columnas identificadoras (no-año)
    id_vars = [c for c in df.columns if c not in year_cols]

    # Transformar a largo
    df_long = df.melt(id_vars=id_vars, value_vars=year_cols,
                      var_name="time", value_name="value")

    # Determinar la columna 'geo' (país)
    normalized = [c.strip().lower() for c in id_vars]
    cand_geo = []
    for i, name in enumerate(normalized):
        if name in ["geo", "geopolitical entity", "country", "geo\\time", "geotime"]:
            cand_geo.append(id_vars[i])
    geo_col = cand_geo[0] if cand_geo else id_vars[0]

    df_long = df_long.rename(columns={geo_col: "geo"})
    df_long["time"] = pd.to_numeric(df_long["time"], errors="coerce")
    df_long["value"] = pd.to_numeric(df_long["value"], errors="coerce")

    print("Dimensiones long:", df_long.shape)
    print(df_long.head(10))
    return df_long

# ------------------------------------------------------
# BLOQUE 3 — Limpieza mínima + regla del 49%
# ------------------------------------------------------
def clean_data(df_long: pd.DataFrame) -> pd.DataFrame:
    df = df_long.dropna(how="all").copy()
    vac_ratio = df.isna().mean(axis=1)
    df = df.loc[vac_ratio <= 0.49].copy()
    need_cols = [c for c in ["geo", "time", "value"] if c in df.columns]
    df = df.dropna(subset=need_cols)
    # Tipos
    df["time"] = df["time"].astype(int)
    return df

# ------------------------------------------------------
# BLOQUE 4 — Guardar limpio para Power BI
# ------------------------------------------------------
def save_clean(df_clean: pd.DataFrame, path_csv: str):
    cols_pref = ["geo", "time", "value", "coicop", "unit"]
    cols_to_keep = [c for c in cols_pref if c in df_clean.columns]
    if not cols_to_keep:
        cols_to_keep = ["geo", "time", "value"]
    df_clean[cols_to_keep].to_csv(path_csv, index=False, encoding="utf-8")
    print(f"[OK] Guardado limpio en: {path_csv}")

# ------------------------------------------------------
# BLOQUE 5 — Descriptivas y correlación por país
# ------------------------------------------------------
def stats_and_correlation(df_clean: pd.DataFrame):
    # Estadísticas
    desc = df_clean["value"].describe().to_frame("value")
    desc_path = os.path.join(OUT_DIR, "estadisticas_descriptivas.xlsx")
    with pd.ExcelWriter(desc_path, engine="openpyxl") as w:
        desc.to_excel(w, sheet_name="descriptivas")
    print("[OK] Descriptivas ->", desc_path)

    # Correlación (pivot: años x países)
    pivot_country = df_clean.pivot_table(index="time", columns="geo", values="value", aggfunc="mean")
    corr = pivot_country.corr()
    corr_path = os.path.join(OUT_DIR, "correlacion.csv")
    corr.to_csv(corr_path, encoding="utf-8")
    print("[OK] Correlación ->", corr_path)
    return corr

# ------------------------------------------------------
# BLOQUE 6 — Gráficos (4 requeridos)
# ------------------------------------------------------
def build_charts(df_clean: pd.DataFrame, corr: pd.DataFrame):
    plt.rcParams["figure.figsize"] = (10, 6)

    # 1) Barras por país (último año)
    latest_year = int(df_clean["time"].max())
    by_country = df_clean[df_clean["time"] == latest_year].groupby("geo")["value"].mean().sort_values(ascending=False)
    ax = by_country.plot(kind="bar")
    ax.set_title(f"Inflación promedio por país - {latest_year}")
    ax.set_ylabel("%")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "g1_inflacion_por_pais_ultimo_anio.png"), dpi=200)
    plt.close()

    # 2) Evolución temporal para top 5 países del último año
    top5 = by_country.head(5).index.tolist()
    evo_top5 = df_clean[df_clean["geo"].isin(top5)].groupby(["time", "geo"])["value"].mean().reset_index()
    for g in top5:
        sub = evo_top5[evo_top5["geo"] == g]
        plt.plot(sub["time"], sub["value"], label=g)
    plt.title(f"Evolución HICP (promedio) - Top 5 países {latest_year}")
    plt.xlabel("Año"); plt.ylabel("%"); plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "g2_evolucion_top5.png"), dpi=200)
    plt.close()

    # 3) Mapa de calor de correlación
    plt.figure(figsize=(10, 8))
    plt.imshow(corr, aspect='auto', interpolation='nearest')
    plt.title("Correlación entre países (HICP)")
    plt.colorbar(label="Correlación")
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.index)), corr.index)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "g3_matriz_correlacion.png"), dpi=200)
    plt.close()

    # 4) Variación interanual por país (último vs anterior)
    prev_year = latest_year - 1
    cur = df_clean[df_clean["time"] == latest_year].groupby("geo")["value"].mean()
    prev = df_clean[df_clean["time"] == prev_year].groupby("geo")["value"].mean()
    delta = (cur - prev).dropna().sort_values(ascending=False)
    ax = delta.plot(kind="bar")
    ax.set_title(f"Variación interanual {latest_year} vs {prev_year} (promedio %)")
    ax.set_ylabel("Δ puntos porcentuales")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "g4_variacion_interanual.png"), dpi=200)
    plt.close()

    print("[OK] Gráficos en /outputs (g1...g4)")

# ------------------------------------------------------
# MAIN — Ejecutar todo en secuencia
# ------------------------------------------------------
if __name__ == "__main__":
    df_raw = load_excel_preview(RAW_XLSX)
    df_long = wide_to_long(df_raw)
    df_clean = clean_data(df_long)
    save_clean(df_clean, CLEAN_CSV)
    corr = stats_and_correlation(df_clean)
    build_charts(df_clean, corr)
    print("\nListo. Abre 'data/hicp_clean.csv' en Power BI para crear KPIs y visuales.")
