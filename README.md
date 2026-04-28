# Dashboard de Contratacion de Publicidad y Medios de Andalucia

Aplicacion Streamlit para explorar contratos, licitaciones y adjudicaciones relacionados con publicidad, comunicacion y medios en Andalucia.

La app lee `Andalucia_cpv.csv`, muestra KPIs, evolucion anual, top localizaciones, ranking de empresas, tipo de contrato y un grid de expedientes con importes formateados como EUR y enlaces oficiales clicables.

## Contenido del proyecto

- `app.py`: aplicacion Streamlit.
- `Andalucia_cpv.csv`: datos normalizados usados por la app.
- `normalizar_adjudicatarios_cpv.py`: script reproducible para limpiar nombres y NIF de adjudicatarios.
- `requirements.txt`: dependencias necesarias.
- `.gitignore`: excluye datasets grandes, logs, entornos locales y secretos.

## Ejecutar en local

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Si usas el runtime local de Codex en este equipo:

```powershell
& 'C:\Users\mmadr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m streamlit run app.py
```

## Actualizar / normalizar datos

Si partes de un `Andalucia_cpv.csv` sin normalizar, ejecuta:

```powershell
python normalizar_adjudicatarios_cpv.py
```

El script genera columnas como `adjudicatario_normalizado`, `nif_normalizado` y claves auxiliares. Si quieres que la app use el mismo nombre de archivo, sustituye el CSV original por el resultado normalizado manteniendo el nombre `Andalucia_cpv.csv`.

## Subida a GitHub

1. Crea un repositorio en GitHub.
2. Desde esta carpeta:

```powershell
git init
git add app.py Andalucia_cpv.csv normalizar_adjudicatarios_cpv.py requirements.txt README.md .gitignore
git commit -m "Add Andalucia contracts dashboard"
git branch -M main
git remote add origin https://github.com/<usuario>/<repositorio>.git
git push -u origin main
```

No subas los CSV grandes excluidos en `.gitignore`; Streamlit Cloud solo necesita `Andalucia_cpv.csv`.

## Despliegue en Streamlit Cloud

1. Entra en [Streamlit Community Cloud](https://streamlit.io/cloud).
2. Selecciona el repositorio de GitHub.
3. Configura:
   - Branch: `main`
   - Main file path: `app.py`
4. Despliega.

No hacen falta secretos ni variables de entorno para esta version.

## Seguridad

- La app no usa credenciales, tokens ni conexiones a bases de datos.
- No ejecuta comandos del sistema ni evalua codigo de usuario.
- Los filtros son operaciones de pandas sobre datos locales.
- Los enlaces clicables proceden del CSV y se muestran con `LinkColumn`.
- `.streamlit/secrets.toml` queda excluido por `.gitignore`.
- El HTML incrustado es estatico para estilo y disclaimer; no incorpora entrada del usuario.

## Fuente

Los datos proceden del buscador general de licitaciones de la Junta de Andalucia:

https://www.juntadeandalucia.es/haciendayadministracionpublica/apl/pdc-front-publico/perfiles-licitaciones/buscador-general
