# Per-operator documentation

One file per operator this project builds a GTFS(-Flex) feed for — real
data sources, what's confirmed vs. provisional, and known gaps. The root
`README.md` still has the original pipeline's full decision log (MDO/SAO6);
[`mdo.md`](mdo.md) and [`sao6.md`](sao6.md) here are short pointers into
it rather than duplicates.

| Operator | Feed type | Status |
|---|---|---|
| [MDO](mdo.md) | Regular GTFS | 15/15 routes with real schedule data |
| [SAO6](sao6.md) | Regular GTFS | Real geometry; **no real schedule data found anywhere** |
| [Sotrames](sotrames.md) | GTFS-Flex | 34 routes, real zone-level schedule |
| [Autobuses El Poblado](elpoblado.md) | GTFS-Flex | 11 routes, 4 with real hours |
| [Coonatra](coonatra.md) | Regular GTFS | 17 routes, mix of literal-time/frequency-based/spatial-only |
| [TRSC](trsc.md) | Regular GTFS | 21 routes, 554 trips |
| [Tax Maya](taxmaya.md) | Regular GTFS | 11 routes, all frequency-based |
