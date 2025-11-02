# Análisis del Índice de Precios de Consumo Armonizado (IPCA / HICP)

Este proyecto contiene un script de Python (`hicp_step_by_step.py`) diseñado para procesar y analizar los datos del Índice de Precios de Consumo Armonizado (HICP) publicados por Eurostat.

El script es robusto y automatiza gran parte del proceso de limpieza y transformación, realizando las siguientes tareas:

1.  **Carga Inteligente**: Localiza el archivo de datos (`prc_hicp_aind.xlsx`) en varias carpetas comunes y permite especificar una ruta mediante una variable de entorno.
2.  **Detección Automática**: Analiza el archivo Excel para encontrar automáticamente la fila de cabecera correcta, ignorando las filas de metadatos que Eurostat suele incluir.
3.  **Transformación de Datos**: Convierte la tabla de un formato ancho (años en columnas) a un formato largo (una columna para el año y otra para el valor), ideal para análisis y visualización.
4.  **Limpieza de Datos**: Elimina filas y columnas vacías, y filtra registros con datos insuficientes.
5.  **Generación de Archivo Limpio**: Crea un archivo `hicp_clean.csv` en la carpeta `data/`, listo para ser importado en herramientas como Power BI, Tableau o Excel.
6.  **Análisis Estadístico**: Calcula estadísticas descriptivas y una matriz de correlación entre los países, guardando los resultados en la carpeta `outputs/`.
7.  **Visualización de Datos**: Genera y guarda cuatro gráficos clave en la carpeta `outputs/`:
    *   Inflación media por país en el último año.
    *   Evolución temporal de la inflación para los 5 países con mayor índice.
    *   Mapa de calor de la matriz de correlación.
    *   Variación interanual de la inflación por país.

## Requisitos

Para ejecutar el script, necesitas tener Python instalado junto con las siguientes librerías:

*   pandas
*   numpy
*   matplotlib
*   openpyxl

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
