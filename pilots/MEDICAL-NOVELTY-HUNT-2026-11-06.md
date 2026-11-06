# Medical novelty hunt (6 Nov 2026)

Goal: a medical-AI question with no existing paper, data available, publishable in a peer-reviewed journal.

## Already done (dropped)
- Adult→child X-ray transfer; paediatric pneumonia (hundreds of papers on Kermany set)
- Sperm movement → DNA damage (Vienna 2021, 122 men; also an ML "non-destructive DFI" paper 2024); sperm video → motility/morphology (MediaEval 2019 tasks)
- Gestational age from scans; growth restriction from age gap (Oxford/medRxiv 2024)
- Dental X-ray → bone growth/age (multiple)
- First-trimester screening (PAPP-A, hCG, NT) → Down syndrome / pre-eclampsia (multiple, 2022–2026)
- Embryo time-lapse → ploidy, implantation (many, incl. Nature Comms 2024, Lancet eClinMed meta-analysis)
- Intrapartum CTG → acidaemia (many)

## Structural finding
Open pregnancy ultrasound datasets (HC18, FETAL_PLANES_DB, ACOUSLIC-AI, 2026 multicentre sets…) have NO outcomes (birth weight, complications). The ART embryo dataset (14,776 embryos, live birth, ploidy, maternal age) is private (UAE collaborators only). Genuinely new + useful questions mostly need outcome-linked data → clinic partner.

## Survivors (no paper found in our searches)
1. **Embryo "age clock"**: AI estimates how old an embryo looks vs mother's real age; gap predicts aneuploidy / live birth. Prior: only a mouse young-vs-old ML study (Biol Reprod 2024). Data: not open, needs IVF clinic. Potential: high.
2. **Sperm video → hormones** (testosterone, FSH, inhibin B): reverse direction (hormones → semen quality) is published; video → hormones not found. Data: VISEM, 85 men, open (Hugging Face). Pilotable now. Risk: small n, weak signal.
3. **Who carries extra risk from fertility treatment** (individual-level causal ML on US birth certificates): average risks published (JAMA Netw Open 2023 etc.); individual heterogeneity via causal forests not found. Data: CDC natality microdata, millions of births/year, open. Pilotable now; econometrics skill fit; can be done solo. Caveat: birth-certificate treatment flag is noisy; infertility itself confounds.

## Pilot results (6 Nov 2026, afternoon)
- **Sperm video → hormones (VISEM, 85 men)**: video motion alone predicts serum inhibin B (rank corr. leave-one-out +0.45), FSH (+0.41), serum AMH (+0.40); about as well as the full lab semen analysis (+0.39 / +0.30 / +0.34). Adding video on top of lab results adds little (FSH +0.12, borderline; others not significant). Testosterone, LH, oestradiol: no signal. Verdict: the video captures the same testicular-function signal as semen quality; cheap and automatic, but not new biology.
- **Fertility treatment risk (US births 2023, 73,818 treated singletons, effect on treated vs 800k controls)**: preterm +4.1 pp (±0.25), NICU +3.2, low birth weight +1.4, caesarean +6.4. Larger in mothers < 30 (preterm +5.1, LBW +2.7) than 40+ (+3.5, +0.7), with obesity (+4.9) and pre-pregnancy hypertension (+6.6); IVF +4.5 vs drugs only +3.0. Held-out ranking of mothers works (preterm top vs bottom quarter +1.8 pp, caesarean +6.8). Age pattern already published (SART 2014, Nordic 2016) → mid-tier paper, not groundbreaking.
- **Fingerprint from commands only**: 86% (whole run), 75% after 25 commands, 44% after 3 (10 models, guessing 10%).
