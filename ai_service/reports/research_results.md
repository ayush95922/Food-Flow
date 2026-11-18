# Research simulation results (SYNTHETIC scenarios)

Seeds 0..29; mean ± std over seeds. Weights are the untuned defaults in `dynamic_matching.Weights`. These numbers describe behaviour inside the simulator only.


## Experiments A/B/C - demand/supply ratio 0.5

| metric | A_nearest_recipient | B_rule_based | C_dynamic_multi_factor |
|---|---|---|---|
| redistributed | 1647.00 ± 189.55 | 1637.13 ± 186.54 | 1630.00 ± 188.14 |
| potential_wastage | 2687.67 ± 241.21 | 2697.53 ± 243.41 | 2704.67 ± 255.23 |
| unmet_demand | 520.37 ± 150.09 | 530.23 ± 149.92 | 537.37 ± 160.49 |
| recipients_served | 10.90 ± 1.06 | 10.77 ± 1.07 | 10.80 ± 1.10 |
| avg_transport_km | 5.69 ± 0.86 | 6.45 ± 0.98 | 6.50 ± 0.68 |
| jain_fairness | 0.87 ± 0.08 | 0.86 ± 0.09 | 0.86 ± 0.09 |
| matching_time_ms_per_donation | 0.10 ± 0.02 | 0.10 ± 0.01 | 0.12 ± 0.01 |


Paired Wilcoxon tests (proposed minus baseline), p-values for redistributed / jain_fairness / avg_transport_km:

- C_dynamic_multi_factor_vs_A_nearest_recipient: redistributed: diff -17.00 (p=0.0618), jain_fairness: diff -0.01 (p=0.0597), avg_transport_km: diff +0.81 (p=2.55e-07)
- C_dynamic_multi_factor_vs_B_rule_based: redistributed: diff -7.13 (p=0.241), jain_fairness: diff +0.00 (p=0.575), avg_transport_km: diff +0.05 (p=0.952)

## Experiments A/B/C - demand/supply ratio 1.0

| metric | A_nearest_recipient | B_rule_based | C_dynamic_multi_factor |
|---|---|---|---|
| redistributed | 2997.60 ± 350.72 | 3119.07 ± 356.60 | 3110.33 ± 340.86 |
| potential_wastage | 1337.07 ± 211.96 | 1215.60 ± 239.40 | 1224.33 ± 208.68 |
| unmet_demand | 1337.20 ± 212.17 | 1215.73 ± 239.53 | 1224.47 ± 208.70 |
| recipients_served | 10.70 ± 1.15 | 10.50 ± 1.11 | 10.73 ± 1.14 |
| avg_transport_km | 5.09 ± 0.96 | 5.87 ± 0.87 | 6.03 ± 0.91 |
| jain_fairness | 0.84 ± 0.09 | 0.84 ± 0.09 | 0.85 ± 0.09 |
| matching_time_ms_per_donation | 0.10 ± 0.00 | 0.10 ± 0.01 | 0.13 ± 0.01 |


Paired Wilcoxon tests (proposed minus baseline), p-values for redistributed / jain_fairness / avg_transport_km:

- C_dynamic_multi_factor_vs_A_nearest_recipient: redistributed: diff +112.73 (p=0.00024), jain_fairness: diff +0.01 (p=0.0246), avg_transport_km: diff +0.94 (p=1.86e-09)
- C_dynamic_multi_factor_vs_B_rule_based: redistributed: diff -8.73 (p=0.287), jain_fairness: diff +0.02 (p=0.181), avg_transport_km: diff +0.16 (p=0.0879)

## Experiments A/B/C - demand/supply ratio 1.5

| metric | A_nearest_recipient | B_rule_based | C_dynamic_multi_factor |
|---|---|---|---|
| redistributed | 3391.80 ± 407.62 | 3468.80 ± 384.28 | 3468.07 ± 377.36 |
| potential_wastage | 942.87 ± 327.94 | 865.87 ± 323.42 | 866.60 ± 312.00 |
| unmet_demand | 3110.10 ± 390.16 | 3033.10 ± 396.33 | 3033.83 ± 385.76 |
| recipients_served | 10.53 ± 1.14 | 9.63 ± 1.25 | 10.40 ± 1.16 |
| avg_transport_km | 4.38 ± 0.89 | 5.30 ± 0.96 | 5.28 ± 0.98 |
| jain_fairness | 0.76 ± 0.08 | 0.72 ± 0.10 | 0.79 ± 0.10 |
| matching_time_ms_per_donation | 0.11 ± 0.02 | 0.11 ± 0.02 | 0.14 ± 0.03 |


Paired Wilcoxon tests (proposed minus baseline), p-values for redistributed / jain_fairness / avg_transport_km:

- C_dynamic_multi_factor_vs_A_nearest_recipient: redistributed: diff +76.27 (p=0.00394), jain_fairness: diff +0.04 (p=0.00664), avg_transport_km: diff +0.91 (p=3.73e-09)
- C_dynamic_multi_factor_vs_B_rule_based: redistributed: diff -0.73 (p=0.948), jain_fairness: diff +0.07 (p=2.6e-05), avg_transport_km: diff -0.02 (p=0.792)

## Ablation (ratio 1.0)

| metric | full | without_urgency | without_fairness | without_distance | without_usable_time | without_capacity |
|---|---|---|---|---|---|---|
| redistributed | 3110.33 ± 340.86 | 3120.30 ± 347.23 | 3112.07 ± 362.22 | 3114.53 ± 333.95 | 2561.50 ± 364.33 | 2961.27 ± 318.83 |
| potential_wastage | 1224.33 ± 208.68 | 1214.37 ± 214.68 | 1222.60 ± 233.24 | 1220.13 ± 194.60 | 1773.17 ± 328.04 | 1373.40 ± 229.23 |
| unmet_demand | 1224.47 ± 208.70 | 1214.50 ± 214.67 | 1222.73 ± 233.40 | 1220.27 ± 194.69 | 1773.30 ± 328.19 | 1373.53 ± 229.28 |
| recipients_served | 10.73 ± 1.14 | 10.70 ± 1.15 | 10.50 ± 1.17 | 10.70 ± 1.15 | 10.50 ± 1.17 | 10.73 ± 1.14 |
| avg_transport_km | 6.03 ± 0.91 | 6.04 ± 0.80 | 5.95 ± 0.89 | 6.97 ± 0.85 | 6.28 ± 0.95 | 5.52 ± 0.95 |
| jain_fairness | 0.85 ± 0.09 | 0.85 ± 0.09 | 0.84 ± 0.10 | 0.85 ± 0.09 | 0.80 ± 0.10 | 0.85 ± 0.09 |
| matching_time_ms_per_donation | 0.16 ± 0.03 | 0.15 ± 0.03 | 0.16 ± 0.03 | 0.16 ± 0.03 | 0.16 ± 0.04 | 0.15 ± 0.03 |


Delta vs full (variant - full), with Wilcoxon p:

- without_urgency: redistributed +9.97 (p=0.128), unmet_demand -9.97 (p=0.128), jain_fairness -0.01 (p=0.374), avg_transport_km +0.00 (p=0.917)
- without_fairness: redistributed +1.73 (p=0.808), unmet_demand -1.73 (p=0.808), jain_fairness -0.02 (p=0.209), avg_transport_km -0.09 (p=0.28)
- without_distance: redistributed +4.20 (p=0.548), unmet_demand -4.20 (p=0.548), jain_fairness -0.01 (p=0.429), avg_transport_km +0.93 (p=5.59e-09)
- without_usable_time: redistributed -548.83 (p=1.73e-06), unmet_demand +548.83 (p=1.73e-06), jain_fairness -0.06 (p=1.3e-07), avg_transport_km +0.24 (p=0.0185)
- without_capacity: redistributed -149.07 (p=5.6e-06), unmet_demand +149.07 (p=5.6e-06), jain_fairness -0.00 (p=0.349), avg_transport_km -0.51 (p=2.61e-08)

## Dynamic (event-driven re-matching) vs static allocation

| metric | static | dynamic |
|---|---|---|
| redistributed | 2531.12 ± 361.48 | 2709.84 ± 380.28 |
| potential_wastage | 1803.54 ± 337.05 | 1624.82 ± 323.07 |
| unmet_demand | 2112.75 ± 758.41 | 1934.08 ± 685.26 |
| jain_fairness | 0.77 ± 0.08 | 0.80 ± 0.08 |
| rejections | 4.60 ± 1.81 | 5.47 ± 2.54 |
| rematches | 0.00 ± 0.00 | 6.53 ± 2.64 |
| failed_delivery_qty | 171.45 ± 144.90 | 149.01 ± 138.07 |


Paired tests (dynamic minus static): redistributed: +178.72 (p=3.4e-05); potential_wastage: -178.72 (p=3.4e-05); unmet_demand: -178.67 (p=6.52e-06); jain_fairness: +0.03 (p=0.00104); rejections: +0.87 (p=0.000993); rematches: +6.53 (p=1.65e-06); failed_delivery_qty: -22.44 (p=0.313)
