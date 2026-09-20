# Medellin Bus Empresas and Routes

## Scope

At this stage, the dataset focuses only on the **bus empresa (operator)** and the **routes operated by that empresa**.

The official **Alcaldia de Medellin / Secretaria de Movilidad** bus-company directory is used as the master list of empresas. The directory contains 40 bus companies, but this specific page does **not** identify which routes each company operates. Therefore, the route fields below are intentionally left blank until an official route source can be linked to each operator.

## Empresa to Routes

| Empresa | Ruta(s) |
|---|---|
| Autobuses El Poblado Laureles S.A. | |
| Autocol | |
| Coinvetrans | |
| Combuses | |
| Conaltracoop | |
| Conducciones America S.A. | |
| Conducciones Palenque Robledal | |
| Coometropol Ltda. | |
| Coonatra Ltda. | |
| Coopcerquin | |
| Coopetransa Ltda. | |
| Cooptransnor | |
| Cootrabel Ltda. | |
| Cootracovi | |
| Cootransblan | |
| Cootranscataluna | |
| Cootranscol | |
| Cootransgranizal | |
| Cootransi | |
| Cootransmallat | |
| Cootransmon | |
| Cootranspinal | |
| Cootransvi | |
| Cootrasana | |
| Copatra Ltda. | |
| Expreso Campo Valdes | |
| Flota La "V" S.C.A. | |
| Flota La Milagrosa S.A. | |
| Flota Nueva Villa S.A. | |
| Invetrans | |
| Metrosan | |
| Rapido San Cristobal | |
| Santra Ltda. | |
| Sotrames | |
| Tax Maya S.A. | |
| Transconor | |
| Transportes Aranjuez Santa Cruz S.A. | |
| Transportes La Mayoritaria Guayabal Ltda. | |
| Transportes Medellin Castilla S.A. | |
| Trasancoop | |

## Recommended Route Mapping Format

Once route information is found, it is preferable to store **one route per row** instead of placing many route codes in one cell:

| Empresa | Codigo | Ruta |
|---|---|---|
| Example empresa | 001 | Route description |
| Example empresa | 002 | Route description |
| Another empresa | 100 | Route description |

This structure will make it easier to combine the operator information later with route schedules, operating hours, frequencies and the C6 data.

## Source

- Alcaldia de Medellin, Secretaria de Movilidad, **Directorio de empresas de buses en Medellin**: https://www.medellin.gov.co/es/secretaria-de-movilidad/transporte-publico/buses-de-medellin/directorio-de-buses/

## Source limitation

The directory page identifies the bus companies and provides contact information, but it does not contain route codes or route assignments. No Empresa-to-Ruta relationship has therefore been inferred from company names or other non-route information.
