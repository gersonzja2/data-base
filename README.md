# Análisis del Índice de Precios de Consumo Armonizado (HICP)

Este proyecto contiene un script de Python (`hicp_step_by_step.py`) diseñado para procesar y analizar los datos del Índice de Precios de Consumo Armonizado (HICP) publicados por Eurostat.

El script realiza las siguientes tareas:
1.  Carga el archivo de datos de Eurostat (`prc_hicp_aind.xlsx`).
2.  Limpia y transforma los datos de un formato ancho a uno largo.
3.  Genera un archivo CSV limpio (`hicp_clean.csv`) ideal para ser utilizado en herramientas de visualización como Power BI.
4.  Calcula estadísticas descriptivas y una matriz de correlación entre países.
5.  Crea y guarda varios gráficos de análisis, como la inflación por país, la evolución temporal y la variación interanual.

## Requisitos

Para ejecutar el script, necesitas tener Python instalado junto con las siguientes librerías:

- pandas
- numpy
- matplotlib
- openpyxl

Puedes instalarlas todas con el siguiente comando:
```bash
pip install pandas numpy matplotlib openpyxl
```

## Estructura del Proyecto

Para que el script funcione correctamente, tu proyecto debe seguir la siguiente estructura de carpetas:

```
tu_proyecto/
├── hicp_step_by_step.py    # El script principal
├── data/
│   └── prc_hicp_aind.xlsx    # El archivo de datos de Eurostat
└── outputs/                  # Carpeta creada por el script para guardar los resultados
```

## Uso

1.  **Descarga los datos**: Obtén el archivo `prc_hicp_aind.xlsx` desde la base de datos de Eurostat.
2.  **Organiza los archivos**: Coloca el archivo `prc_hicp_aind.xlsx` dentro de la carpeta `data/`.
3.  **Ejecuta el script**: Abre una terminal en la carpeta raíz de tu proyecto y ejecuta el siguiente comando:
    ```bash
    python hicp_step_by_step.py
    ```
4.  **Revisa los resultados**: Una vez finalizada la ejecución, encontrarás los archivos generados en la carpeta `outputs/` y el archivo de datos limpio en `data/hicp_clean.csv`.
