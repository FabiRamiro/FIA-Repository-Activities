[↩ Volver a la Unidad 1](../README.md)

# BASH: preparación de datos de PIB y satisfacción

Preparación con Bash de dos conjuntos de datos para relacionar el PIB per cápita de cada país con su satisfacción de vida, según el Better Life Index 2015 de la OCDE. Se limpian ambos archivos, se ordenan por país y se unen en uno solo.

| Archivo | Contenido |
|---|---|
| [gdp_per_capita.csv](gdp_per_capita.csv) | PIB per cápita original. |
| [oecd_bli_2015.csv](oecd_bli_2015.csv) | Better Life Index 2015 original. |
| `*_sinultimafila.csv`, `*_solodatos.csv`, `*_ordenado.csv`, `gdp_per_capita_comas.csv`, `gdp_per_capita_COUNTRY.csv`, `oecd_bli_2015_SWLIFETOT.csv` | Pasos intermedios: quitar pie de página, quedarse con las columnas útiles, filtrar el indicador de satisfacción de vida y ordenar por país. |
| [merged_data.csv](merged_data.csv) | Datos unidos: país, satisfacción de vida y PIB per cápita. |
| [X.csv](X.csv) / [Y.csv](Y.csv) | PIB per cápita (variable de entrada) y satisfacción de vida (variable objetivo), listos para un modelo. |
