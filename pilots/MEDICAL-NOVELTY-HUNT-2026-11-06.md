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
