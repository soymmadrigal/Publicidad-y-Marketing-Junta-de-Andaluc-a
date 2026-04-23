# Andalucía Transparente: Publicidad Institucional

Aplicación en **Streamlit** para visualizar expedientes de publicidad institucional y contratación en Andalucía, con enfoque de transparencia pública.

## Qué incluye

- Carga optimizada desde `Parquet` (`Andalucia_medios.parquet`).
- Filtros por año, estado, tipo de contrato, provincia y adjudicatario.
- KPIs y gráficos interactivos con importes en formato monetario.
- Tabla de exploración con enlace al detalle oficial del expediente.
- Descarga de datos filtrados en CSV.
- Uso de columna normalizada de adjudicatario: `Adjudicatario`.

## Estructura mínima recomendada (para Streamlit Cloud)

```text
.streamlit/config.toml
app.py
requirements.txt
Andalucia_medios.parquet
```

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Despliegue en Streamlit Cloud

1. Sube estos 4 archivos al repositorio.
2. En Streamlit Cloud, crea una nueva app apuntando a `app.py`.
3. Streamlit instalará dependencias desde `requirements.txt` automáticamente.

## Fuente y aviso legal

Esta app es una visualización no oficial con fines informativos y de transparencia.

Para datos oficiales y actualizados, consulta:

- Buscador oficial Junta de Andalucía:  
  https://www.juntadeandalucia.es/haciendayadministracionpublica/apl/pdc-front-publico/perfiles-licitaciones/buscador-general
- Portal oficial de perfiles y licitaciones:  
  https://www.juntadeandalucia.es/temas/contratacion-publica/perfiles-licitaciones.html

