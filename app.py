from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_FILE_PREFERRED = Path("Andalucia_medios.parquet")
DATA_FILE_CSV_PRIMARY = Path("Andalucia_medios.csv")
DATA_FILE_CSV_FALLBACK = Path("Andalucia_publicidad.csv")
OFFICIAL_SEARCH_URL = (
    "https://www.juntadeandalucia.es/haciendayadministracionpublica/apl/"
    "pdc-front-publico/perfiles-licitaciones/buscador-general"
)
OFFICIAL_PORTAL_URL = "https://www.juntadeandalucia.es/temas/contratacion-publica/perfiles-licitaciones.html"


st.set_page_config(
    page_title="Andalucía Transparencia | Publicidad y Patrocinios",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def parse_money(value: object) -> float:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0
    txt = str(value).strip()
    if not txt:
        return 0.0
    txt = txt.replace("€", "").replace(" ", "").replace(".", "").replace(",", ".")
    return float(txt) if txt else 0.0


def fmt_eur(value: float) -> str:
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def mask_nif(value: object) -> str:
    txt = "" if value is None else str(value).strip()
    if len(txt) <= 3:
        return txt
    return f"{txt[:2]}***{txt[-1:]}"


def _can_read_parquet() -> bool:
    try:
        import pyarrow  # noqa: F401
        return True
    except Exception:
        try:
            import duckdb  # noqa: F401
            return True
        except Exception:
            return False


def _resolve_input_file() -> Path:
    # Cloud-safe: CSV first to avoid hard dependency on pyarrow wheels.
    if DATA_FILE_CSV_PRIMARY.exists():
        return DATA_FILE_CSV_PRIMARY
    if DATA_FILE_CSV_FALLBACK.exists():
        return DATA_FILE_CSV_FALLBACK
    if DATA_FILE_PREFERRED.exists() and _can_read_parquet():
        return DATA_FILE_PREFERRED
    return DATA_FILE_CSV_PRIMARY


@st.cache_data(show_spinner="Cargando datos de transparencia...", ttl=3600, max_entries=2)
def load_data(path: Path) -> pd.DataFrame:
    last_error = None
    if path.suffix.lower() == ".parquet":
        try:
            df = pd.read_parquet(path)
            for col in df.columns:
                df[col] = df[col].fillna("").astype(str).str.strip()
        except Exception as exc:
            # Fallback 1: DuckDB (sin pyarrow)
            try:
                import duckdb
                df = duckdb.sql(f"SELECT * FROM read_parquet('{path.as_posix()}')").df()
                for col in df.columns:
                    df[col] = df[col].fillna("").astype(str).str.strip()
            except Exception:
                # Fallback 2: CSV si existe
                if DATA_FILE_CSV_PRIMARY.exists():
                    path = DATA_FILE_CSV_PRIMARY
                elif DATA_FILE_CSV_FALLBACK.exists():
                    path = DATA_FILE_CSV_FALLBACK
                else:
                    raise RuntimeError(f"No se pudo leer parquet (pandas/duckdb) y no hay CSV fallback: {exc}")
                for enc in ("utf-8-sig", "latin-1"):
                    try:
                        df = pd.read_csv(path, sep=";", dtype=str, encoding=enc, low_memory=False)
                        break
                    except Exception as inner_exc:  # pragma: no cover
                        last_error = inner_exc
                else:
                    raise RuntimeError(f"No se pudo leer el CSV fallback: {last_error}")
    else:
        for enc in ("utf-8-sig", "latin-1"):
            try:
                df = pd.read_csv(path, sep=";", dtype=str, encoding=enc, low_memory=False)
                break
            except Exception as exc:  # pragma: no cover
                last_error = exc
        else:
            raise RuntimeError(f"No se pudo leer el CSV: {last_error}")

    df.columns = [c.strip() for c in df.columns]
    for col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

    required_cols = [
        "detalle_importe_adjudicacion_sin_iva",
        "detalle_importe_adjudicacion_con_iva",
        "detalle_fecha_adjudicacion",
        "detalle_numero_expediente",
        "detalle_titulo_expediente",
        "detalle_organo_contratacion",
        "detalle_tipo_contrato",
        "detalle_estado_formalizado",
        "detalle_lugar_ejecucion",
        "detalle_persona_adjudicataria",
        "detalle_nif_adjudicatario",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise RuntimeError(f"Faltan columnas requeridas en el dataset: {', '.join(missing)}")

    numeric_cols = [
        "detalle_importe_licitacion_sin_iva",
        "detalle_importe_licitacion_con_iva",
        "detalle_valor_estimado",
        "detalle_importe_adjudicacion_sin_iva",
        "detalle_importe_adjudicacion_con_iva",
        "detalle_num_licitadores",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    if "Importe licitación" in df.columns:
        df["importe_licitacion_tabla"] = df["Importe licitación"].map(parse_money)
    else:
        df["importe_licitacion_tabla"] = 0.0

    if "Importe adjudicación" in df.columns:
        df["importe_adjudicacion_tabla"] = df["Importe adjudicación"].map(parse_money)
    else:
        df["importe_adjudicacion_tabla"] = 0.0

    date_cols = [
        "detalle_fecha_formalizacion",
        "detalle_fecha_adjudicacion",
    ]
    for col in date_cols:
        if col in df.columns:
            df[col + "_dt"] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
        else:
            df[col + "_dt"] = pd.NaT

    if "detalle_fecha_adjudicacion_dt" in df.columns:
        df["anio_adjudicacion"] = (
            df["detalle_fecha_adjudicacion_dt"].dt.year.fillna(0).astype(int).replace({0: pd.NA})
        )
    else:
        df["anio_adjudicacion"] = pd.NA

    df["expediente"] = df.get("detalle_numero_expediente", "")
    df["titulo"] = df.get("detalle_titulo_expediente", "")
    df["organo"] = df.get("detalle_organo_contratacion", df.get("Órgano de contratación", ""))
    df["tipo_contrato"] = df.get("detalle_tipo_contrato", df.get("Tipo de contrato", ""))
    df["estado_expediente"] = df.get("detalle_estado_formalizado", df.get("Estado", ""))
    df["provincia"] = df.get("detalle_lugar_ejecucion", "")

    df["adjudicataria_original"] = df.get("detalle_persona_adjudicataria", "")
    if "Adjudicatario" in df.columns:
        df["adjudicataria_normalizada"] = df["Adjudicatario"].astype(str).str.strip()
    else:
        df["adjudicataria_normalizada"] = df["adjudicataria_original"]
    df["adjudicataria_normalizada"] = df["adjudicataria_normalizada"].replace({"": "Sin especificar"})

    df["nif_masked"] = df.get("detalle_nif_adjudicatario", "").map(mask_nif)

    cat_cols = ["tipo_contrato", "estado_expediente", "provincia", "organo", "adjudicataria_normalizada"]
    for col in cat_cols:
        df[col] = df[col].replace({"": "Sin especificar"})

    return df


def filter_text(text: str) -> str:
    safe = re.sub(r"[^0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ .,_:/()\\-]", "", text or "")
    return safe[:120].strip()


DATA_FILE = _resolve_input_file()
if not DATA_FILE.exists():
    st.error(
        "No se encuentra el fichero de datos. Se buscó en: "
        f"{DATA_FILE_PREFERRED.resolve()}, {DATA_FILE_CSV_PRIMARY.resolve()} y {DATA_FILE_CSV_FALLBACK.resolve()}"
    )
    st.stop()

df_raw = load_data(DATA_FILE)

st.title("Andalucía Transparente: Publicidad Institucional")
st.caption("Panel ciudadano de contratación pública y patrocinios con enfoque de rendición de cuentas.")

st.info(
    "Descargo legal: esta app es una visualización no oficial para facilitar análisis público. "
    "Para datos oficiales y actualizados, consulta directamente la Junta de Andalucía: "
    f"[Buscador oficial]({OFFICIAL_SEARCH_URL}) · [Portal oficial]({OFFICIAL_PORTAL_URL})."
)

with st.sidebar:
    st.markdown("### Junta de Andalucía")
    st.caption("Ejercicio de transparencia con datos abiertos de contratación pública.")
    st.header("Filtros")
    search_text = filter_text(st.text_input("Buscar texto (expediente, título, órgano, adjudicataria)", ""))

    years_available = sorted([int(x) for x in df_raw["anio_adjudicacion"].dropna().unique().tolist()], reverse=True)
    selected_years = st.multiselect("Año de adjudicación", years_available, default=years_available)

    tipos = sorted(df_raw["tipo_contrato"].dropna().unique().tolist())
    selected_tipos = st.multiselect("Tipo de contrato", tipos, default=tipos)

    estados = sorted(df_raw["estado_expediente"].dropna().unique().tolist())
    selected_estados = st.multiselect("Estado", estados, default=estados)

    provincias = sorted(df_raw["provincia"].dropna().unique().tolist())
    selected_provincias = st.multiselect("Provincia", provincias, default=provincias)

    adj_top = (
        df_raw["adjudicataria_normalizada"]
        .value_counts()
        .head(60)
        .index
        .tolist()
    )
    selected_adj = st.multiselect("Adjudicataria (normalizada)", adj_top, default=[])

    include_errors = st.checkbox("Incluir registros con error de detalle", value=False)
    max_rows = st.slider("Filas máximas en tabla", min_value=100, max_value=5000, value=1000, step=100)

df = df_raw.copy()

if selected_years:
    df = df[df["anio_adjudicacion"].isin(selected_years)]
if selected_tipos:
    df = df[df["tipo_contrato"].isin(selected_tipos)]
if selected_estados:
    df = df[df["estado_expediente"].isin(selected_estados)]
if selected_provincias:
    df = df[df["provincia"].isin(selected_provincias)]
if selected_adj:
    df = df[df["adjudicataria_normalizada"].isin(selected_adj)]
if not include_errors and "detalle_error" in df.columns:
    df = df[df["detalle_error"].eq("")]

if search_text:
    idx = (
        df["expediente"].str.contains(search_text, case=False, na=False)
        | df["titulo"].str.contains(search_text, case=False, na=False)
        | df["organo"].str.contains(search_text, case=False, na=False)
        | df["adjudicataria_normalizada"].str.contains(search_text, case=False, na=False)
        | df.get("detalle_persona_adjudicataria", "").str.contains(search_text, case=False, na=False)
    )
    df = df[idx]

total_sin_iva = float(df["detalle_importe_adjudicacion_sin_iva"].sum())
total_con_iva = float(df["detalle_importe_adjudicacion_con_iva"].sum())
total_expedientes = int(len(df))
total_organos = int(df["organo"].nunique())

k1, k2, k3, k4 = st.columns(4)
k1.metric("Expedientes", f"{total_expedientes:,}".replace(",", "."))
k2.metric("Adjudicación sin IVA", fmt_eur(total_sin_iva))
k3.metric("Adjudicación con IVA", fmt_eur(total_con_iva))
k4.metric("Órganos distintos", f"{total_organos:,}".replace(",", "."))

tab1, tab2, tab3 = st.tabs(["Resumen", "Explorador", "Datos y legal"])

with tab1:
    c1, c2 = st.columns(2)

    with c1:
        by_year = (
            df.dropna(subset=["anio_adjudicacion"])
            .groupby("anio_adjudicacion", as_index=False)["detalle_importe_adjudicacion_sin_iva"]
            .sum()
            .sort_values("anio_adjudicacion")
        )
        if not by_year.empty:
            by_year["importe_fmt"] = by_year["detalle_importe_adjudicacion_sin_iva"].map(fmt_eur)
            fig_year = px.bar(
                by_year,
                x="anio_adjudicacion",
                y="detalle_importe_adjudicacion_sin_iva",
                text="importe_fmt",
                title="Inversión adjudicada sin IVA por año",
                template="plotly_white",
                color="detalle_importe_adjudicacion_sin_iva",
                color_continuous_scale="Blues",
            )
            fig_year.update_layout(xaxis_title="", yaxis_title="")
            fig_year.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(fig_year, use_container_width=True)
        else:
            st.warning("No hay datos para el gráfico anual con los filtros actuales.")

    with c2:
        by_tipo = (
            df.groupby("tipo_contrato", as_index=False)["detalle_importe_adjudicacion_sin_iva"]
            .sum()
            .sort_values("detalle_importe_adjudicacion_sin_iva", ascending=False)
        )
        if not by_tipo.empty:
            fig_tipo = px.pie(
                by_tipo,
                names="tipo_contrato",
                values="detalle_importe_adjudicacion_sin_iva",
                title="Distribución por tipo de contrato",
                hole=0.45,
                template="plotly_white",
            )
            st.plotly_chart(fig_tipo, use_container_width=True)
        else:
            st.warning("No hay datos por tipo de contrato.")

    top_org = (
        df.groupby("organo", as_index=False)["detalle_importe_adjudicacion_sin_iva"]
        .sum()
        .sort_values("detalle_importe_adjudicacion_sin_iva", ascending=False)
        .head(15)
    )
    if not top_org.empty:
        top_org["importe_fmt"] = top_org["detalle_importe_adjudicacion_sin_iva"].map(fmt_eur)
        fig_org = px.bar(
            top_org,
            x="detalle_importe_adjudicacion_sin_iva",
            y="organo",
            text="importe_fmt",
            orientation="h",
            title="Top 15 órganos por adjudicación sin IVA",
            template="plotly_white",
            color="detalle_importe_adjudicacion_sin_iva",
            color_continuous_scale="Tealgrn",
        )
        fig_org.update_layout(xaxis_title="", yaxis_title="")
        fig_org.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(fig_org, use_container_width=True)

    top_adj = (
        df.groupby("adjudicataria_normalizada", as_index=False)["detalle_importe_adjudicacion_sin_iva"]
        .sum()
        .sort_values("detalle_importe_adjudicacion_sin_iva", ascending=False)
        .head(15)
    )
    if not top_adj.empty:
        top_adj["importe_fmt"] = top_adj["detalle_importe_adjudicacion_sin_iva"].map(fmt_eur)
        fig_adj = px.bar(
            top_adj,
            x="detalle_importe_adjudicacion_sin_iva",
            y="adjudicataria_normalizada",
            text="importe_fmt",
            orientation="h",
            title="Top 15 adjudicatarias (nombre normalizado)",
            template="plotly_white",
            color="detalle_importe_adjudicacion_sin_iva",
            color_continuous_scale="Viridis",
        )
        fig_adj.update_layout(xaxis_title="", yaxis_title="")
        fig_adj.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(fig_adj, use_container_width=True)

with tab2:
    st.subheader("Tabla de expedientes")
    show_cols = [
        "expediente",
        "titulo",
        "organo",
        "tipo_contrato",
        "estado_expediente",
        "provincia",
        "detalle_importe_adjudicacion_sin_iva",
        "detalle_importe_adjudicacion_con_iva",
        "detalle_fecha_adjudicacion",
        "adjudicataria_normalizada",
        "adjudicataria_original",
        "nif_masked",
        "detalle_persona_adjudicataria",
        "URL detalle",
    ]
    safe_cols = [c for c in show_cols if c in df.columns]
    view = df[safe_cols].copy()
    view = view.sort_values("detalle_importe_adjudicacion_sin_iva", ascending=False).head(max_rows)

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
        column_config={
            "detalle_importe_adjudicacion_sin_iva": st.column_config.NumberColumn(format="%.2f €"),
            "detalle_importe_adjudicacion_con_iva": st.column_config.NumberColumn(format="%.2f €"),
            "URL detalle": st.column_config.LinkColumn(display_text="Abrir detalle"),
        },
    )

with tab3:
    st.subheader("Descargas")
    export_df = df.copy()
    csv_bytes = export_df.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="Descargar datos filtrados (CSV)",
        data=csv_bytes,
        file_name="andalucia_publicidad_filtrado.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("### Seguridad y buen uso")
    st.markdown(
        "- El panel no ejecuta HTML/JS arbitrario ni código de usuario.\n"
        "- Búsqueda sanitizada y limitada en longitud para evitar abusos.\n"
        "- NIF mostrado en formato enmascarado para minimizar exposición directa.\n"
        "- Normalización de adjudicatarias para evitar duplicados por variaciones de escritura.\n"
        "- Caché de datos para reducir carga de CPU y mejorar tiempos de respuesta."
    )

    st.markdown("### Fuentes oficiales")
    st.markdown(f"- Buscador oficial Junta de Andalucía: [abrir enlace]({OFFICIAL_SEARCH_URL})")
    st.markdown(f"- Portal de perfiles y licitaciones: [abrir enlace]({OFFICIAL_PORTAL_URL})")
