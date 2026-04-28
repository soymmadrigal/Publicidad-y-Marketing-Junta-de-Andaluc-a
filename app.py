import streamlit as st
import pandas as pd
import plotly.express as px


SOURCE_FILE = "Andalucia_cpv.csv"
PORTAL_URL = "https://www.juntadeandalucia.es/haciendayadministracionpublica/apl/pdc-front-publico/perfiles-licitaciones/buscador-general"

GREEN = "#007A3D"
GREEN_DARK = "#00582C"
GREEN_SOFT = "#EAF6EF"
GOLD = "#D6A419"
INK = "#123125"
MUTED = "#60756B"


st.set_page_config(
    page_title="Andalucia | Contratacion de publicidad y medios",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    f"""
    <style>
    :root {{
        --andalucia-green: {GREEN};
        --andalucia-green-dark: {GREEN_DARK};
        --andalucia-green-soft: {GREEN_SOFT};
        --andalucia-gold: {GOLD};
        --andalucia-ink: {INK};
        --andalucia-muted: {MUTED};
    }}

    .stApp {{
        background:
            linear-gradient(180deg, #f7fbf8 0%, #ffffff 36%, #f3f8f5 100%);
        color: var(--andalucia-ink);
    }}

    section[data-testid="stSidebar"] {{
        background: #ffffff;
        border-right: 1px solid #d8e7df;
    }}

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {{
        color: var(--andalucia-green-dark);
    }}

    h1, h2, h3 {{
        color: var(--andalucia-ink);
        letter-spacing: 0;
    }}

    hr {{
        border: 0;
        border-top: 1px solid #d8e7df;
        margin: 1.2rem 0;
    }}

    .hero {{
        border-left: 8px solid var(--andalucia-green);
        padding: 0.35rem 0 0.35rem 1rem;
        margin: 0.4rem 0 1.2rem 0;
    }}

    .hero .eyebrow {{
        color: var(--andalucia-green-dark);
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.78rem;
        letter-spacing: 0.08em;
    }}

    .hero .subtitle {{
        color: var(--andalucia-muted);
        font-size: 1rem;
        max-width: 980px;
    }}

    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.85rem;
        margin: 0.4rem 0 1.1rem 0;
    }}

    .kpi-card {{
        background: #ffffff;
        border: 1px solid #d8e7df;
        border-top: 4px solid var(--andalucia-green);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 10px 24px rgba(0, 88, 44, 0.08);
        min-height: 112px;
    }}

    .kpi-label {{
        color: var(--andalucia-muted);
        font-size: 0.84rem;
        font-weight: 700;
        text-transform: uppercase;
    }}

    .kpi-value {{
        color: var(--andalucia-green-dark);
        font-size: 1.55rem;
        font-weight: 800;
        line-height: 1.2;
        margin-top: 0.45rem;
        overflow-wrap: anywhere;
    }}

    .kpi-note {{
        color: var(--andalucia-muted);
        font-size: 0.82rem;
        margin-top: 0.35rem;
    }}

    .source-box {{
        background: #ffffff;
        border: 1px solid #d8e7df;
        border-left: 5px solid var(--andalucia-gold);
        border-radius: 8px;
        padding: 0.9rem 1rem;
        color: var(--andalucia-ink);
    }}

    .source-box a {{
        color: var(--andalucia-green-dark);
        font-weight: 700;
        text-decoration: none;
    }}

    .source-box a:hover {{
        text-decoration: underline;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid #d8e7df;
        border-radius: 8px;
        overflow: hidden;
    }}

    .stDownloadButton button,
    .stButton button {{
        background: var(--andalucia-green);
        color: #ffffff;
        border: 1px solid var(--andalucia-green-dark);
        border-radius: 6px;
        font-weight: 700;
    }}

    @media (max-width: 980px) {{
        .kpi-grid {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }}
    }}

    @media (max-width: 640px) {{
        .kpi-grid {{
            grid-template-columns: 1fr;
        }}
        .kpi-value {{
            font-size: 1.35rem;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt_eur(value):
    if pd.isna(value):
        value = 0
    text = f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{text} EUR"


def fmt_int(value):
    return f"{int(value):,}".replace(",", ".")


def parse_money(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace("EUR", "", regex=False)
        .str.replace("â‚¬", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip(),
        errors="coerce",
    ).fillna(0)


def clean_text(series, default="Sin especificar"):
    return (
        series.fillna(default)
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .replace({"": default, "nan": default, "None": default})
    )


@st.cache_data(show_spinner="Cargando contratos de publicidad y medios de Andalucia...")
def load_data():
    df = pd.read_csv(SOURCE_FILE, sep=";", dtype=str, encoding="utf-8")

    text_columns = [
        "tipoRegistro",
        "numeroExpediente",
        "titulo",
        "urlDetalle",
        "estado",
        "tipoContrato",
        "procedimiento",
        "perfilContratante",
        "adjudicatarios",
        "adjudicatario_normalizado",
        "nif_normalizado",
        "cpv",
        "provinciasEjecucion",
        "origen",
    ]
    for col in text_columns:
        if col in df.columns:
            df[col] = clean_text(df[col])

    if "adjudicatario_normalizado" in df.columns:
        df["empresa"] = clean_text(df["adjudicatario_normalizado"])
    else:
        df["empresa"] = clean_text(df["adjudicatarios"])

    if "nif_normalizado" in df.columns:
        df["nif_empresa"] = clean_text(df["nif_normalizado"], "")
    else:
        df["nif_empresa"] = clean_text(df.get("nifAdjudicatarios", pd.Series("", index=df.index)), "")

    for col in [
        "importeLicitacion",
        "importeLicitacionConIva",
        "valorEstimado",
        "importeFormalizacion",
        "importeFormalizacionConIva",
        "importeFormalizado",
        "importeFormalizadoConIva",
        "importeAdjudicacion",
        "importeAdjudicacionConIva",
    ]:
        if col in df.columns:
            df[col] = parse_money(df[col])

    for col in [
        "fechaPublicacion",
        "fechaLimitePresentacion",
        "fechaResolucionAdjudicacion",
        "fechaFormalizacion",
    ]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True).dt.tz_convert(None)

    df["anio"] = df["fechaPublicacion"].dt.year.fillna(0).astype(int)
    df["mes"] = df["fechaPublicacion"].dt.to_period("M").astype(str).replace("NaT", "Sin fecha")
    importe_formalizado = pd.Series(0, index=df.index, dtype="float64")
    importe_formalizado_iva = pd.Series(0, index=df.index, dtype="float64")
    for col in ["importeFormalizacion", "importeFormalizado"]:
        if col in df.columns:
            importe_formalizado = importe_formalizado.where(importe_formalizado > 0, df[col])
    for col in ["importeFormalizacionConIva", "importeFormalizadoConIva"]:
        if col in df.columns:
            importe_formalizado_iva = importe_formalizado_iva.where(importe_formalizado_iva > 0, df[col])

    df["importe_base"] = importe_formalizado.where(
        importe_formalizado > 0,
        df["importeAdjudicacion"].where(df["importeAdjudicacion"] > 0, df["importeLicitacion"]),
    )
    df["importe_con_iva_base"] = importe_formalizado_iva.where(
        importe_formalizado_iva > 0,
        df["importeAdjudicacionConIva"].where(df["importeAdjudicacionConIva"] > 0, df["importeLicitacionConIva"]),
    )
    df["tipo_importe_mostrado"] = "Licitacion"
    df.loc[df["importeAdjudicacion"] > 0, "tipo_importe_mostrado"] = "Adjudicacion"
    df.loc[importe_formalizado > 0, "tipo_importe_mostrado"] = "Formalizacion"

    df["cpv_codigo"] = df["cpv"].str.extract(r"^([0-9]{2,8}(?:-[0-9])?)", expand=False).fillna("Sin CPV")
    df["cpv_descripcion"] = df["cpv"].str.replace(r"^[0-9]{2,8}(?:-[0-9])?\s*", "", regex=True)
    df["cpv_descripcion"] = clean_text(df["cpv_descripcion"], "Sin descripcion")

    return df


def top_table(df, group_col, value_col="importe_base", n=12):
    return (
        df.groupby(group_col, dropna=False)[value_col]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )


def short_label(value, max_chars=64):
    text = str(value)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "..."


def bar_chart(data, x, y, orientation="h", color=GREEN, height=420, left_margin=8, hover_col=None):
    fig = px.bar(data, x=x, y=y, orientation=orientation, text=data[x if orientation == "h" else y].apply(fmt_eur))
    hovertemplate = "%{y}<br>%{x:,.2f} EUR<extra></extra>" if orientation == "h" else "%{x}<br>%{y:,.2f} EUR<extra></extra>"
    if hover_col and hover_col in data.columns:
        fig.update_traces(customdata=data[[hover_col]], hovertemplate="%{customdata[0]}<br>%{x:,.2f} EUR<extra></extra>")
    else:
        fig.update_traces(hovertemplate=hovertemplate)
    fig.update_traces(marker_color=color, textposition="outside", cliponaxis=False)
    fig.update_layout(
        height=height,
        margin=dict(l=left_margin, r=80, t=20, b=30),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK, size=12),
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(gridcolor="#e1ede6", tickformat=",.0f"),
        yaxis=dict(categoryorder="total ascending"),
        showlegend=False,
    )
    return fig


def detail_grid(source_df, key):
    st.subheader("Detalle de expedientes")
    table = source_df[
        [
            "numeroExpediente",
            "titulo",
            "perfilContratante",
            "tipoContrato",
            "procedimiento",
            "estado",
            "provinciasEjecucion",
            "importe_base",
            "importe_con_iva_base",
            "tipo_importe_mostrado",
            "fechaPublicacion",
            "empresa",
            "nif_empresa",
            "adjudicatarios",
            "urlDetalle",
        ]
    ].copy()
    table = table.rename(
        columns={
            "numeroExpediente": "Expediente",
            "titulo": "Titulo",
            "perfilContratante": "Organo",
            "tipoContrato": "Tipo",
            "procedimiento": "Procedimiento",
            "estado": "Estado",
            "provinciasEjecucion": "Localizacion",
            "importe_base": "Importe base",
            "importe_con_iva_base": "Importe con IVA",
            "tipo_importe_mostrado": "Tipo importe",
            "fechaPublicacion": "Fecha publicacion",
            "empresa": "Empresa normalizada",
            "nif_empresa": "NIF normalizado",
            "adjudicatarios": "Adjudicatario original",
            "urlDetalle": "Detalle oficial",
        }
    )
    table = table.sort_values("Fecha publicacion", ascending=False)
    table["Importe base"] = table["Importe base"].apply(fmt_eur)
    table["Importe con IVA"] = table["Importe con IVA"].apply(fmt_eur)
    table["Fecha publicacion"] = pd.to_datetime(table["Fecha publicacion"], errors="coerce").dt.strftime("%d/%m/%Y").fillna("")

    st.dataframe(
        table,
        width="stretch",
        hide_index=True,
        height=520,
        column_config={
            "Detalle oficial": st.column_config.LinkColumn("Detalle oficial", display_text="Abrir"),
        },
        key=key,
    )


def annual_bar_chart(data, x, y):
    fig = px.bar(data, x=x, y=y, text=data[y].apply(fmt_eur))
    fig.update_traces(
        marker_color=GREEN,
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{x}<br>%{y:,.2f} EUR<extra></extra>",
    )
    fig.update_layout(
        height=360,
        margin=dict(l=8, r=20, t=20, b=35),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK, size=12),
        xaxis_title="",
        yaxis_title="",
        yaxis=dict(gridcolor="#e1ede6", tickformat=",.0f"),
        showlegend=False,
    )
    return fig


df_raw = load_data()

st.sidebar.title("Filtros")
years = sorted([year for year in df_raw["anio"].unique().tolist() if year > 0], reverse=True)
sel_years = st.sidebar.multiselect("Ejercicio", years, default=years)
sel_origin = st.sidebar.multiselect("Origen", sorted(df_raw["origen"].unique()), default=sorted(df_raw["origen"].unique()))
sel_type = st.sidebar.multiselect("Tipo de contrato", sorted(df_raw["tipoContrato"].unique()))
sel_status = st.sidebar.multiselect("Estado", sorted(df_raw["estado"].unique()))
sel_province = st.sidebar.multiselect("Provincia / lugar ejecucion", sorted(df_raw["provinciasEjecucion"].unique()))
sel_org = st.sidebar.selectbox("Organo de contratacion", ["Todos"] + sorted(df_raw["perfilContratante"].unique().tolist()))
company_options = sorted(df_raw.loc[df_raw["empresa"] != "Sin especificar", "empresa"].unique().tolist())
sel_company = st.sidebar.selectbox("Empresa adjudicataria", ["Todas"] + company_options)
query = st.sidebar.text_input("Buscar en titulo, organo o empresa")

df = df_raw.copy()
if sel_years:
    df = df[df["anio"].isin(sel_years)]
if sel_origin:
    df = df[df["origen"].isin(sel_origin)]
if sel_type:
    df = df[df["tipoContrato"].isin(sel_type)]
if sel_status:
    df = df[df["estado"].isin(sel_status)]
if sel_province:
    df = df[df["provinciasEjecucion"].isin(sel_province)]
if sel_org != "Todos":
    df = df[df["perfilContratante"] == sel_org]
if sel_company != "Todas":
    df = df[df["empresa"] == sel_company]
if query:
    q = query.strip().casefold()
    mask = (
        df["titulo"].str.casefold().str.contains(q, na=False)
        | df["perfilContratante"].str.casefold().str.contains(q, na=False)
        | df["empresa"].str.casefold().str.contains(q, na=False)
        | df["adjudicatarios"].str.casefold().str.contains(q, na=False)
        | df["nif_empresa"].str.casefold().str.contains(q, na=False)
    )
    df = df[mask]

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Junta de Andalucia</div>
        <h1>Contratacion de publicidad, comunicacion y medios</h1>
        <div class="subtitle">
            Panel de seguimiento de expedientes publicados en la Plataforma de Contratacion de la Comunidad Autonoma.
            Importes mostrados en EUR con separador de miles.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

total_base = df["importe_base"].sum()
total_iva = df["importe_con_iva_base"].sum()
avg_contract = df["importe_base"].mean() if len(df) else 0
formalizados = int(df["estado"].str.contains("resuelto|formalizado|adjudicado", case=False, na=False).sum())

st.markdown(
    f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Importe formalizado / adjudicado / licitado</div>
            <div class="kpi-value">{fmt_eur(total_base)}</div>
            <div class="kpi-note">Mejor importe disponible sin IVA</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Total con impuestos</div>
            <div class="kpi-value">{fmt_eur(total_iva)}</div>
            <div class="kpi-note">Formalizacion, adjudicacion o licitacion con IVA</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Expedientes</div>
            <div class="kpi-value">{fmt_int(len(df))}</div>
            <div class="kpi-note">{fmt_int(formalizados)} con estado resuelto/adjudicado</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Importe medio</div>
            <div class="kpi-value">{fmt_eur(avg_contract)}</div>
            <div class="kpi-note">Media sobre expedientes filtrados</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_overview, tab_entities, tab_records = st.tabs(["Dashboard", "Organos y adjudicatarios", "Expedientes"])

with tab_overview:
    col1, col2 = st.columns([1.15, 0.85])
    with col1:
        st.subheader("Evolucion por ejercicio")
        by_year = df[df["anio"] > 0].groupby("anio")["importe_base"].sum().reset_index()
        st.plotly_chart(annual_bar_chart(by_year, "anio", "importe_base"), width="stretch")

    with col2:
        st.subheader("Top Localizaciones")
        province = top_table(df, "provinciasEjecucion", n=10)
        st.plotly_chart(bar_chart(province, "importe_base", "provinciasEjecucion", color=GREEN_DARK), width="stretch")

    st.subheader("Empresas con mayor importe")
    companies = top_table(df[df["empresa"] != "Sin especificar"], "empresa", n=12)
    companies["empresa_etiqueta"] = companies["empresa"].apply(lambda value: short_label(value, 72))
    st.plotly_chart(
        bar_chart(
            companies,
            "importe_base",
            "empresa_etiqueta",
            color=GREEN,
            height=520,
            left_margin=20,
            hover_col="empresa",
        ),
        width="stretch",
    )

    st.subheader("Tipo de contrato")
    by_type = top_table(df, "tipoContrato", n=12)
    fig = px.pie(by_type, names="tipoContrato", values="importe_base", hole=0.55)
    fig.update_traces(
        marker=dict(colors=[GREEN, GREEN_DARK, GOLD, "#78B98A", "#A7D8B0", "#51685B"]),
        textinfo="percent+label",
        hovertemplate="%{label}<br>%{value:,.2f} EUR<extra></extra>",
    )
    fig.update_layout(
        height=420,
        margin=dict(l=8, r=8, t=20, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK),
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")

    detail_grid(df, "dashboard_detail_grid")

with tab_entities:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Organos de contratacion")
        organs = top_table(df, "perfilContratante", n=15)
        st.plotly_chart(bar_chart(organs, "importe_base", "perfilContratante", color=GREEN_DARK), width="stretch")

    with col2:
        st.subheader("Empresas adjudicatarias")
        awarded = df[df["empresa"] != "Sin especificar"]
        bidders = top_table(awarded, "empresa", n=15)
        st.plotly_chart(bar_chart(bidders, "importe_base", "empresa", color=GOLD), width="stretch")

with tab_records:
    detail_grid(df, "records_detail_grid")

csv_data = df.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
st.sidebar.download_button(
    label="Descargar seleccion (CSV)",
    data=csv_data,
    file_name="andalucia_publicidad_filtrado.csv",
    mime="text/csv",
)

st.markdown("---")
st.markdown(
    f"""
    <div class="source-box">
        <strong>Aviso de transparencia.</strong>
        Esta visualizacion procesa datos publicos con fines informativos. Los importes pueden diferir de la
        liquidacion definitiva por redondeos, actualizaciones o correcciones en la fuente original.
        No constituye un documento oficial. Fuente:
        <a href="{PORTAL_URL}" target="_blank">Buscador general de licitaciones de la Junta de Andalucia</a>.
    </div>
    """,
    unsafe_allow_html=True,
)
