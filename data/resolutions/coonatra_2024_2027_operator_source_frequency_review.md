# Coonatra 2024–2027 operator frequency and operating-window recovery — 18 November 2026

## New direct operator document (visually checked)

[COONATRA Política Pública 2024–2027, original PDF](https://coonatra.com/wp-content/uploads/2023/09/POLITICA-PUBLICA-COONATRA.pdf). The operator's own presentation includes **frecuencia prom. (min)** and **horario de operación** for six *families*, with the count of ramales for each family. PDF pp5–10 (zero-based screenshot pp4–9) were visually inspected. The website [Coonatra Circular routes](https://coonatra.com/circular-coonatra/) and [Metro-integrated Circular project](https://metro.coonatra.com/) additionally describe Circular services 300/301, direct La 80 branches and **04:10 first / 21:30 last dispatch**, with a later stop presence at UdeA (22:20 / 22:10, **not** separate terminal departure).

| Operator family | Average minutes | General operation | Branches | Primary evidence |
|---|---:|---|---:|---|
| Circular Coonatra | **4** | 04:00–21:30 | 4 | PDF p5 |
| Circular Sur | **3** | 04:00–21:30 | 1 | PDF p6 |
| Calasanz Intermedia | **5** | 04:10–21:30 | 3 | PDF p7 |
| Calasanz Integrada | **7** | 04:00–23:00 | 3 | PDF p8 |
| Floresta–San Juan | **6** | 03:45–21:30 | 4 | PDF p9 |
| Floresta Integrada | **8** | 04:00–23:15 | 2 | PDF p10 |

All six original entries have been captured in [`coonatra_2024_2027_operator_published_family_windows_frequencies.csv`](coonatra_2024_2027_operator_published_family_windows_frequencies.csv).

### Deliberate interpretation

These are **operator-published average family headways, not separately verified frequencies of each ArcGIS variant, direction or weekday/saturday/sunday**. The PDF title refers to 2024–2027 but does **not** prove all individual services remained unchanged on 18 Nov 2026. No unjustified copy of the **4 min** family frequency into all 300/301/303 legacy route codes; no use of **Circular Sur** as a proxy for Santra's Circular 315. The 04:10–21:30 Circular source on the live site refers to its own specific presentation, while the PDF prints general 04:00–21:30; **preserve both and do not overwrite one silently**.

This reduces the number of service **families without any operator frequency lead**, but does not change the **252-route schedule coverage** numerator yet because a one-to-one variant crosswalk remains missing. The [operator-level gap priorities](medellin_operator_frequency_gap_priorities.csv) still correctly show 11 Coonatra old variants without individually linked modern source records. They are **not eleven total unknown timetables**.

The wider [252-route prioritization report](medellin_frequency_coverage_review_2026-11-18.md) keeps resolution-first lookup, then verified original operator schedule, then 2015 provisional fallback and third-party where needed. No GTFS generator modifications.
