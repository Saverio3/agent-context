# Who carries extra risk from fertility treatment? (US births 2023, singletons)

Singleton births analysed: 3,275,161; fertility treatment: 73,818 (2.3%), of which ART (IVF etc.) 55,333. Controls subsampled to 800,000 and reweighted. Effects are risk differences in percentage points, adjusted for pre-pregnancy factors (age, BMI, smoking, parity, prior preterm, prior caesarean, diabetes, hypertension, education, insurance, marital status, race, prenatal care, baby sex).

| Outcome | Rate if untreated | Raw gap | Adjusted extra risk (pp) | Lowest-risk quarter of mothers | Highest-risk quarter | Top vs bottom (pp) |
|---|---|---|---|---|---|---|
| Preterm (<37 wk) | 10.4% | +3.89 | **+4.15** (±1.46) | +2.94 (±2.96) | +4.28 (±6.12) | +1.34 (±6.80) |
| Low birth weight | 6.7% | +1.39 | **+2.52** (±1.36) | +2.72 (±1.99) | +1.18 (±7.02) | -1.54 (±7.30) |
| NICU admission | 8.4% | +4.23 | **+3.56** (±1.37) | +4.54 (±5.24) | +4.21 (±5.95) | -0.33 (±7.93) |
| Apgar5 < 7 | 2.0% | +0.84 | **+1.05** (±0.74) | +0.24 (±2.13) | +1.43 (±2.75) | +1.20 (±3.48) |
| Caesarean | 30.7% | +17.02 | **+5.23** (±1.73) | +3.33 (±3.30) | +4.94 (±7.57) | +1.60 (±8.26) |

Quarters: mothers sorted by the model's predicted extra risk (fitted on one half), effect then measured on the other half — so a real top-vs-bottom gap is not overfitting. ± = 95% interval.

## What drives the extra risk (correlation with predicted extra risk)

- **Preterm (<37 wk)**: cig (+0.23), ppterm_y (-0.21), edu (+0.06), bmi_ (+0.06)
- **Low birth weight**: age (-0.15), race2 (+0.10), edu (-0.09), married (-0.09)
- **NICU admission**: cesar_prev_y (-0.10), phype_y (+0.08), bmi_ (+0.07), cig (+0.07)
- **Apgar5 < 7**: phype_y (+0.16), cig (+0.11), race6 (+0.08), bmi_ (+0.08)
- **Caesarean**: race2 (+0.33), race1 (-0.23), cesar_prev_y (-0.11), ppterm_y (+0.09)

# v2: Extra risk among mothers who used fertility treatment (effect on the treated)

73,818 treated singleton births compared with what models trained on 800,000 similar untreated births predict for them. Percentage points; ± = 95% interval.

| Outcome | Treated rate | Expected without treatment | Extra risk | Lowest predicted-risk quarter | Highest quarter | Top vs bottom |
|---|---|---|---|---|---|---|
| Preterm (<37 wk) | 14.3% | 10.1% | **+4.13** (±0.25) | +2.81 (±0.68) | +4.63 (±0.73) | +1.81 (±1.00) |
| Low birth weight | 8.1% | 6.8% | **+1.37** (±0.19) | +0.58 (±0.55) | +2.05 (±0.60) | +1.48 (±0.81) |
| NICU admission | 12.6% | 9.4% | **+3.24** (±0.24) | +3.22 (±0.68) | +2.99 (±0.70) | -0.23 (±0.98) |
| Apgar5 < 7 | 2.9% | 2.2% | **+0.70** (±0.12) | +0.86 (±0.35) | +0.91 (±0.37) | +0.05 (±0.51) |
| Caesarean | 47.8% | 41.3% | **+6.43** (±0.32) | +3.12 (±0.75) | +9.95 (±1.00) | +6.83 (±1.25) |

## Extra risk by group (percentage points)

| Group | n | Preterm (<37 wk) | Low birth weight | NICU admission | Apgar5 < 7 | Caesarean |
|---|---|---|---|---|---|---|
| All treated | 73,818 | +4.1 (±0.2) | +1.4 (±0.2) | +3.2 (±0.2) | +0.7 (±0.1) | +6.4 (±0.3) |
| ART (IVF etc.) | 55,333 | +4.5 (±0.3) | +1.2 (±0.2) | +3.5 (±0.3) | +0.6 (±0.1) | +7.6 (±0.4) |
| Fertility drugs only | 18,485 | +3.0 (±0.5) | +1.7 (±0.4) | +2.5 (±0.5) | +0.9 (±0.2) | +3.0 (±0.6) |
| Age < 30 | 8,941 | +5.1 (±0.7) | +2.7 (±0.6) | +4.2 (±0.7) | +1.1 (±0.4) | +4.3 (±0.9) |
| Age 30–34 | 23,424 | +4.7 (±0.4) | +2.0 (±0.3) | +3.5 (±0.4) | +0.8 (±0.2) | +7.1 (±0.6) |
| Age 35–39 | 27,014 | +3.6 (±0.4) | +0.7 (±0.3) | +2.9 (±0.4) | +0.5 (±0.2) | +7.0 (±0.5) |
| Age 40+ | 14,439 | +3.5 (±0.6) | +0.7 (±0.5) | +2.8 (±0.6) | +0.7 (±0.3) | +5.6 (±0.7) |
| First baby | 43,598 | +4.1 (±0.3) | +1.6 (±0.3) | +3.5 (±0.3) | +0.8 (±0.2) | +8.5 (±0.5) |
| BMI ≥ 30 | 21,887 | +4.9 (±0.5) | +2.2 (±0.4) | +3.8 (±0.5) | +1.0 (±0.3) | +5.2 (±0.6) |
| Pre-pregnancy hypertension | 3,833 | +6.6 (±1.4) | +1.8 (±1.2) | +4.5 (±1.3) | +1.8 (±0.7) | +6.0 (±1.4) |
| Medicaid | 4,558 | +4.7 (±1.1) | +2.5 (±0.9) | +3.6 (±1.0) | +1.5 (±0.6) | +5.9 (±1.2) |

## What drives it (correlation with predicted extra risk)

- **Preterm (<37 wk)**: bmi_ (+0.33), age (-0.28), phype_y (+0.26), care (-0.17)
- **Low birth weight**: age (-0.45), bmi_ (+0.36), edu (-0.24), care (-0.18)
- **NICU admission**: age (-0.38), bmi_ (+0.33), edu (-0.24), cesar_prev_y (-0.14)
- **Apgar5 < 7**: bmi_ (+0.25), edu (-0.17), age (-0.15), private (-0.15)
- **Caesarean**: parity (-0.48), cesar_prev_y (-0.37), bmi_ (-0.21), ppterm_y (-0.14)
