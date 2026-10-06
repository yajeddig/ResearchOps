---
title: 'ProcessGuard-AI-CDU: Advisory Digital Twin Prototype for an Atmospheric Crude
  Distillation Unit with Preheat Train Fouling Health Module'
date: '2026-10-06'
category: Digital_Twin_Ops
confidence: 0.8
tags: [digital-twin, heat-exchanger, decision-support, simulation-dynamic, anomaly-detection]
sectors: ['sector:petrochem']
source: https://github.com/ShreeChem/ProcessGuard-AI-CDU
type: Article
source_type: Other
hash: 72662b932064
---
## 🎯 Relevance
It is a compact reference design for an advisory digital twin on a refinery CDU. It combines a mechanistic heat-exchanger network model, fouling modelling, a residual-based clean-baseline health indicator, rule-based root-cause analysis and an economic cleaning-scheduling layer. The same pattern applies to fouling monitoring in other heat-exchange or process units. The safety boundary and synthetic-data approach are useful templates for prototyping before access to plant data. It is only an early portfolio prototype with no real-plant validation, so it is better as inspiration than as proven methodology.

## 📖 Content
# ProcessGuard-AI-CDU (GitHub portfolio prototype)

**Status:** initial-phase engineering prototype (V17). It uses **synthetic data only**. It is a read-only, advisory concept for an atmospheric Crude Distillation Unit (CDU) and does not replace the DCS, SIS or ESD.

## Architecture

```mermaid
flowchart LR
  A[Synthetic historian-style tags] --> B[JS physics engine (browser)]
  A2[Optional FastAPI backend: F-101 physics] -.same model.-> B
  B --> C[Residuals / clean-baseline model]
  C --> D[Rule-based diagnostics + scoring]
  D --> E[Operator / Engineer UI: PFD, trends, Tag Explorer, Reports]
```

- Runtime files in `public/`: `index.html`, `styles.css`, `app.js`, `preheat-engine.js`, `preheat-ui.js`, `preheat.css`.
- A static site is deployed through GitHub Pages from `main`.
- The optional Python service (FastAPI/uvicorn in `backend/`) exposes the same F-101 heater physics. An identical JavaScript twin runs in the browser, so the backend is not required.
- Self-check: `node tools/validate-preheat.js`.

## Scenarios

| # | Scenario | Phenomenon |
|---|---|---|
| 1 | F-101 Heater Performance | Gradual heat-transfer degradation, coil fouling or coking |
| 2 | Reflux Valve Response | Control-valve stiction / response mismatch |
| 3 | E-201 Condenser Performance | Reduced overhead heat removal |
| 4 | Column Hydraulic Loading | High feed, approach to hydraulic limit |
| 5 | Preheat Train Performance | Fouling in E-101…E-106 with selectable cause: desalter upset, antifoulant pump stopped, unstable crude blend, or a single exchanger (local cause) |

## Preheat Health module (V17)

### Network model
Six counter-current exchangers in series (E-101…E-106) are modelled with the ε-NTU method. They heat desalted crude from 120 °C up to the F-101 coil inlet. The residue loop (E-106 → E-105) couples the exchangers and is solved iteratively.

$$Q = \varepsilon\, C_{min}\,(T_{h,in}-T_{c,in}),\qquad NTU=\frac{UA}{C_{min}}$$

### Fouling model
An Ebert–Panchal-type threshold model is used: deposition rises with film temperature and is suppressed by wall shear/velocity:

$$\frac{dR_f}{dt}=\alpha\,Re^{-0.66}Pr^{-0.33}\exp\!\left(-\frac{E}{R\,T_{film}}\right)-\gamma\,\tau_w$$

The parameters are illustrative and not fitted to a plant.

### Synthetic history
- 12 months of hourly historian-style tags.
- Imperfections injected: noise, crude switches, a desalter upset, an antifoulant outage, two past cleanings, a drifting transmitter, and one missing temperature (reconstructed from the energy balance).
- Exportable as CSV.

### Clean-baseline model (the only trained ML model)
Per-exchanger regression of ln UA on crude flow, hot flow and time, trained on the first 28 days after turnaround:

$$\ln UA_{clean}=\beta_0+\beta_1 F_{crude}+\beta_2 F_{hot}+\beta_3 t$$

$$\text{Health}\,\% = 100\cdot\frac{UA_{actual}}{UA_{clean,pred}}$$

Validated against the synthetic ground truth: R² of 0.6–0.95 depending on the exchanger.

### Economics
- Network-aware loss per exchanger.
- Extra F-101 fuel, € and t CO₂ per day, heater firing margin.
- Cleaning plan minimising the average cost per day, with one exchanger offline at a time.
- Prices are editable placeholders.

### Diagnostics
Rule-based root-cause hints use desalter salt, antifoulant rate, a blend fouling index, and the pattern of which exchangers accelerated. The F-101 firing residual stays near zero in this scenario, which separates preheat fouling from heater-coil fouling.

## Investigation workflow
`Detect -> Correlate -> Explain -> Forecast -> What-if -> Replay`

Views: operator view, engineer view, scenario testing, tag explorer, trends, DCS-alarm comparison, product/KPI views, evidence matrices, diagnostic ranking, recommended checks, event reconstruction. The UI is in English and German.

## AI/ML positioning
Only one lightweight trained model is deployed (the clean-baseline regression). The rest is physics (F-101 energy balance), residuals, rules, engineering scoring and forecast logic. An Isolation Forest concept and expanded pumparound/side-stripper scenarios are roadmap items.

## Safety boundary
- Read-only, advisory.
- No command is sent to DCS/SIS/ESD.
- What-if is simulation-only.
- Does not replace alarms, interlocks, procedures or engineering judgement.

## Run locally
```bash
python -m http.server 8080 --directory public
# optional physics service
pip install -r backend/requirements.txt
cd backend && uvicorn api:app --host 127.0.0.1 --port 8000
node tools/validate-preheat.js
```

## Caveats
- No open-source license is selected, so reuse rights are not granted.
- The repo must not contain proprietary PFD/P&IDs, real plant data or credentials.
- All parameters and data are synthetic, so results are demonstrative and not validated on a real plant.

## 💡 Key Insights
- The prototype couples a first-principles ε-NTU preheat train model with an Ebert–Panchal threshold fouling model to track exchanger health on synthetic data.
- Exchanger health is defined as actual UA divided by the UA predicted by a clean-baseline regression of ln UA, trained on the first 28 days after turnaround.
- The F-101 firing residual separates preheat-train fouling (residual near zero) from heater-coil fouling.
- Most of the predictive layer is physics, residuals and rules; only one lightweight ML model is deployed, and an Isolation Forest is still on the roadmap.
- The system is explicitly advisory and read-only, with no write path to DCS/SIS/ESD, which is a sound safety pattern for decision-support tools.
- A dual implementation (an identical JavaScript twin in the browser plus an optional FastAPI service) lets the demo run as a static GitHub Pages site.
- The synthetic history deliberately includes realistic data defects (drifting transmitter, missing tag reconstructed by energy balance, crude switches, cleanings) to test the diagnostics.
- The economic layer converts UA loss into extra fuel, € and CO₂ per day and optimises cleaning schedules.

## 📚 References
- ShreeChem, ProcessGuard-AI-CDU, GitHub repository, https://github.com/ShreeChem/ProcessGuard-AI-CDU (live demo: https://shreechem.github.io/ProcessGuard-AI-CDU/) *(source)*
- Ebert, W. and Panchal, C.B., Analysis of Exxon crude-oil-slip-stream coking data (threshold fouling model) *(cited)*

## 🏷️ Classification
The repository documents an operations-oriented, advisory digital twin for a crude distillation unit, with diagnostics, what-if scenarios and a fouling health module.
