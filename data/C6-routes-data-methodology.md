# Medellín Cuenca 6 (C6) Route Data: Research and Validation Methodology

## Purpose

This document describes the research, validation, and data-quality process used to build the accompanying JSON dataset for Medellín's **Cuenca 6 (C6)** feeder bus routes.

The objective was to identify the current C6 route inventory and, where possible, add operating hours (`horarios`) and service frequencies (`frecuencias`) while preserving the distinction between official information and third-party timetable data.

**Research date:** 20 September 2026.

## 1. Establishing the route inventory

The first step was to identify the C6 routes from primary sources.

The main reference was the **Metro de Medellín – Sistema Integrado** page:

- https://www.metrodemedellin.gov.co/usuarios/sistema-integrado/

Its section **“Mapas de la ruta de la cuenca 6”** lists the principal Cuenca 6 route identifiers and their origin/destination descriptions, including routes from C6-001 through C6-025, with several lettered variants.

The route inventory was then compared with information published by **Sistema Alimentador Oriental (SAO6)**:

- https://sao6.com.co/
- https://sao6.com.co/rutas

This comparison is important because SAO6 information can contain newer or additional variants not shown in exactly the same way on the Metro route overview. During the research, examples included **C6-002A, C6-004A and C6-025B**.

### Result

The JSON should not assume that the Metro overview alone is a complete version-controlled route registry. Route identifiers from official operator information should also be retained, with provenance recorded for each entry.

## 2. Searching for operating hours and frequencies

After establishing the routes, searches were performed for each type of operating information:

- `horario`
- `horarios de operación`
- `frecuencia`
- `intervalo`
- `despachos`
- `plan de operación`
- `resolución`
- `acto administrativo`

The research covered:

1. Metro de Medellín
2. Sistema Alimentador Oriental (SAO6)
3. Alcaldía de Medellín / Secretaría de Movilidad
4. Third-party timetable sources such as Moovit and TransitRun

The official Metro Cuenca 6 overview is useful for route identity and maps, but it did not provide a complete structured timetable/frequency table for every C6 route during this research.

## 3. Searching Alcaldía de Medellín publications

Because route changes and operating conditions may be documented outside the Metro website, the **Alcaldía de Medellín** and **Secretaría de Movilidad** material was searched separately.

A particularly useful primary source was the Alcaldía publication about route **C6-010**, published on **18 November 2024**:

- https://www.medellin.gov.co/es/sala-de-prensa/noticias/nueva-ruta-alimentadora-del-metro-da-solucion-de-movilidad-a-mas-de-11-000-estudiantes-del-itm-en-boston/

The publication identifies C6-010 as part of Sistema Alimentador Oriental, describes its connection with ITM Fraternidad, Metro station Prado and Metroplús station Catedral, and states an operating window of **04:00 to 23:30**.

This demonstrated why municipal publications and administrative/operational documents must be checked separately: they may contain operational information that is not exposed in the general Metro route overview.

## 4. Using third-party timetable sources

When official pages did not expose the required timetable data, third-party transport sources were examined as secondary evidence.

### Moovit example: C6-001

- https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-c6_001-Medellin-1642-3763299-351878625-0

At the time of checking, Moovit displayed a **30-minute frequency** for C6-001 and supplied operating-hour information. It also linked a route/timetable PDF.

However, values such as `05:00-04:30` are unusual and were not independently confirmed by an official source during the investigation. Consequently, these values must not be promoted to “official” status merely because they are precise.

### TransitRun example: C6-025

- https://transitrun.com/es/public-transit-line_C6-025_58675

At the time of checking, TransitRun reported:

- Monday–Saturday: `04:30–22:00`, frequency `6 min`
- Sunday: `05:00–22:00`, frequency `12 min`

No authoritative effective date or matching administrative decision was established during this phase. These values are therefore retained as secondary-source data pending official confirmation.

## 5. Source validation

The important URLs used in the investigation were reopened to determine whether they were still reachable and whether their content supported the values being recorded.

The validation process checked:

1. Does the URL resolve to the expected route or publication?
2. Is the route identifier explicitly present?
3. Are operating hours explicitly stated or merely inferred?
4. Is frequency explicitly stated or calculated from departures?
5. Does the page expose a publication/effective/update date?
6. Is the publisher an authority/operator or an independent journey-planning service?
7. Does another source contradict the value?

A reachable URL alone is **not** sufficient verification of a timetable value.

## 6. Source hierarchy

The accompanying JSON should use the following evidence hierarchy.

### Level 1: Official administrative or operational document

Highest confidence:

- resolución
- acto administrativo
- plan de operación
- officially issued technical operating document

These sources should take precedence when they explicitly state the route, validity/effective date, operating window, frequency or dispatch plan.

### Level 2: Official public authority

Examples:

- Alcaldía de Medellín
- Secretaría de Movilidad de Medellín
- Área Metropolitana del Valle de Aburrá

These are primary sources, particularly for approved route changes and service conditions.

### Level 3: Official transport system/operator

Examples:

- Metro de Medellín
- Sistema Alimentador Oriental (SAO6)

These are preferred for current route identity, maps, passenger information and operator-published service information.

### Level 4: Structured timetable / transport data

A published timetable or transport feed can be highly useful when its provenance and effective date are known. When those are unknown, it should not automatically override dated official material.

### Level 5: Third-party journey planners

Examples:

- Moovit
- TransitRun

These sources can provide useful missing timetable information, but values remain provisional until reconciled with an official source.

## 7. Confidence/status model

Each timetable value in the JSON should carry a provenance/confidence status rather than presenting every value as equally authoritative.

Recommended statuses:

- `official` – directly supported by an official authority, operator publication, resolution or operational document.
- `secondary` – supplied by a third-party timetable or journey-planning source and not yet independently confirmed.
- `conflicting` – credible sources provide incompatible values.
- `unknown` – no reliable value has yet been located.

Do not substitute assumptions for missing values. Use `null` for unknown structured values and explain the gap in a note if necessary.

## 8. Publication date versus effective date

Three dates should be treated separately:

- `publication_date`: when a source was published.
- `effective_date`: when the timetable or route configuration became valid.
- `checked_date`: when the research team last verified the source.

A web page without a visible publication date should **not** be assigned an invented date. Record the publication date as `null` or `unknown`, while still recording `checked_date`.

This is particularly important for journey-planner pages labelled “updated” without displaying a verifiable update date.

## 9. Handling conflicting information

Conflicts were treated as data-quality findings rather than silently resolved.

For example, an official municipal publication for C6-010 explicitly states an operating window of **04:00–23:30**. If a journey planner supplies a materially different window for a route with the same identifier, the official dated publication should be retained as the stronger source unless a newer official document supersedes it.

The JSON should therefore allow more than one observation/source to be retained when necessary instead of overwriting the losing value without a trace.

## 10. Recommended JSON fields

For each route, the following minimum fields are recommended:

```json
{
  "route_id": "C6-010",
  "name": "Villatina - ITM - Estación Prado",
  "operator": "Sistema Alimentador Oriental",
  "service": {
    "weekday": {
      "start": "04:00",
      "end": "23:30",
      "frequency_minutes": null
    },
    "saturday": null,
    "sunday_holiday": null
  },
  "status": "official",
  "sources": [
    {
      "publisher": "Alcaldía de Medellín",
      "url": "https://www.medellin.gov.co/es/sala-de-prensa/noticias/nueva-ruta-alimentadora-del-metro-da-solucion-de-movilidad-a-mas-de-11-000-estudiantes-del-itm-en-boston/",
      "publication_date": "2024-11-18",
      "effective_date": null,
      "checked_date": "2026-09-20",
      "source_type": "official_publication"
    }
  ],
  "notes": "Operating window explicitly stated by Alcaldía de Medellín; frequency still requires verification."
}
```

This structure is preferable to storing only a single `frequency` field because C6 frequencies may differ by day, period or source.

## 11. Data that remains incomplete

The main unresolved research task is to identify the authoritative operating schedules for all C6 routes, especially:

- first and last service by day type;
- peak frequency;
- off-peak frequency;
- Saturday frequency;
- Sunday/holiday frequency;
- effective date of each schedule;
- associated resolution, administrative act or operating-plan identifier.

A missing value in the JSON means **“not yet verified”**, not “no service”.

## 12. Recommended next research phase

Future updates should concentrate on official documents from:

- Alcaldía de Medellín
- Secretaría de Movilidad de Medellín
- Área Metropolitana del Valle de Aburrá
- Metro de Medellín
- Sistema Alimentador Oriental (SAO6)

Searches should combine each exact route identifier (`C6-001`, `C6-002`, etc.) with Spanish operational terminology such as `frecuencia`, `intervalo`, `despachos`, `horario`, `plan de operación`, `resolución` and `acto administrativo`.

Where a new official source is found:

1. preserve the old observation for auditability;
2. add the new source URL and dates;
3. determine whether the document supersedes the previous value;
4. update the route's preferred/current value;
5. change the confidence/status only after provenance is recorded.

## 13. Known source URLs

### Official / primary

- Metro de Medellín, Sistema Integrado: https://www.metrodemedellin.gov.co/usuarios/sistema-integrado/
- Sistema Alimentador Oriental: https://sao6.com.co/
- SAO6 routes: https://sao6.com.co/rutas
- Alcaldía de Medellín, C6-010 publication (18 November 2024): https://www.medellin.gov.co/es/sala-de-prensa/noticias/nueva-ruta-alimentadora-del-metro-da-solucion-de-movilidad-a-mas-de-11-000-estudiantes-del-itm-en-boston/

### Secondary

- Moovit C6-001: https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-c6_001-Medellin-1642-3763299-351878625-0
- Moovit C6-001 PDF: https://appassets.mvtdev.com/map/188/l/1642/351878625.pdf
- TransitRun C6-025: https://transitrun.com/es/public-transit-line_C6-025_58675

## 14. Publication note

The resulting dataset should be described as a **research-based aggregation**, not as an official timetable issued by Metro de Medellín, SAO6 or the Alcaldía de Medellín.

Suggested disclaimer:

> This dataset aggregates C6 route and timetable information from official transport/public-authority sources and selected third-party timetable services. Source provenance and confidence are recorded per item. Missing values indicate information that could not yet be verified. For travel-critical decisions, consult the current information published by Metro de Medellín, Sistema Alimentador Oriental and the relevant Medellín mobility authorities.

---

**Last methodological review:** 20 September 2026  
**Scope:** Medellín, Colombia – Cuenca 6 / Sistema Alimentador Oriental C6 routes
