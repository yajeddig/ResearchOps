---
title: "Agentic Physics-Informed Digital Twin for Trustworthy Cyber-Physical System Recovery"
date: 2026-01-22
category: Data_Science
confidence: 0.95
tags: ['Digital Twin', 'Physics-Informed Neural Networks (PINN)', 'AI Agents', 'Cyber-Physical Systems (CPS)', 'Process Control', 'Hybrid Modeling', 'Anomaly Detection', 'Industry 4.0', 'Asset Administration Shell (AAS)', 'Duffing Oscillator', 'Machine Learning', 'Control Systems', 'Python', 'DeepXDE', 'PyTorch', 'Streamlit']
source: "https://github.com/hadijannat/agentic-physics-digital-twin"
type: Article
source_type: Article
hash: 152149
---

## 🎯 Relevance
This project offers a significant learning opportunity for industrial data scientists and process engineers interested in advanced control systems, hybrid modeling, and trustworthy AI. It demonstrates how to integrate physics-informed machine learning (PINNs) with multi-agent systems to create robust digital twins capable of autonomous decision-making and system recovery, ensuring operational integrity and safety in cyber-physical systems. The Industry 4.0 (AAS) integration also highlights its practical applicability for interoperable industrial automation.

## 📖 Content
This repository presents a reference implementation for Agentic Physics-Informed Digital Twins, an emerging paradigm where autonomous AI agents operate under physics-based governance to ensure trustworthy decision-making in cyber-physical systems.

The architecture implements a closed-loop cognitive control system with three specialized agents:

| Agent | Role | Key Mechanism |
| --- | --- | --- |
| 🧠 **Dreamer** | Proposes structured recovery actions | LLM/mock-based action generation |
| 🛡️ **Sheriff** | Validates proposals via physics residuals | PINN-based equation enforcement |
| 💊 **Healer** | Executes the propose→validate→execute loop | Closed-loop controller |

**Key Insight**: Unlike traditional threshold-based safety mechanisms, the Sheriff agent evaluates proposals against the governing differential equation, providing a principled, interpretable compliance check rooted in first-principles physics.

**System Architecture**

The system implements a cyber-physical feedback loop where:
1.  **Physical Plant** (Duffing Oscillator) generates time-series sensor data
2.  **Dreamer Agent** analyzes anomalies and proposes corrective actions
3.  **Sheriff Agent** validates proposals using physics residual $r(t)=\ddot{x}+\delta \dot{x}+\alpha x+\beta x^3-\gamma \cos(\omega t)$
4.  **Healer Agent** orchestrates the control loop with veto-and-reprompt capability
5.  **Dashboard** provides real-time visualization via Streamlit + Plotly

**Technology Stack**

| Layer | Technologies |
| --- | --- |
| **Physics Engine** | SciPy `solve_ivp`, NumPy |
| **Neural Networks** | DeepXDE (PINNs), PyTorch |
| **Agent Framework** | Pydantic models, Mock/LLM agents |
| **Configuration** | Hydra-core, YAML |
| **Visualization** | Streamlit, Plotly |
| **Standards** | AAS JSON artifacts (IDTA-aligned) |

**Architecture Quickstart**

To trace the data flow end-to-end:
1.  **Entry point**: `app.py` → loads config, runs `run_agentic_episode()`, renders dashboard.
2.  **Control loop**: `src/agentic_twin/healer/controller.py` → orchestrates Dreamer → Sheriff → Healer.
3.  **Physics truth**: `src/agentic_twin/physics/duffing.py` → Duffing simulation and anomaly injection.
4.  **Physics enforcement**: `src/agentic_twin/sheriff/validator.py` + `physics.py` → residual checks.
5.  **Agent proposals**: `src/agentic_twin/dreamer/agent.py` + `scenarios.py` → deterministic demo paths.
6.  **Industrial layer**: `src/agentic_twin/aas/manager.py` → writes AAS time series artifacts.

Fast trace command:
```python
python src/agentic_twin/scripts/run_episode.py
```
Then inspect:
```bash
cat artifacts/logs/latest_episode.json | head -n 40
```

**Physics Domain: The Forced Duffing Oscillator**

The demonstration uses the Duffing equation—a canonical nonlinear dynamical system exhibiting rich behaviors including chaos, bifurcations, and limit cycles:

$$\ddot{x}+\delta \dot{x}+\alpha x+\beta x^3=\gamma \cos(\omega t)$$

**Parameter Semantics**

| Symbol | Parameter | Physical Meaning | Typical Value |
| --- | --- | --- | --- |
| $\delta$ | Damping coefficient | Energy dissipation rate | 0.2 |
| $\alpha$ | Linear stiffness | Restoring force (can be negative for bistability) | -1.0 |
| $\beta$ | Nonlinear stiffness | Cubic hardening/softening | 1.0 |
| $\gamma$ | Forcing amplitude | External drive strength | 0.3 |
| $\omega$ | Forcing frequency | Drive periodicity | 1.2 |

**Why Duffing?**
*   ✅ **Nonlinearity**: Simple MLP regressors can fit the data but violate the governing equation
*   ✅ **Rich dynamics**: Exhibits both periodic and chaotic regimes
*   ✅ **Industrial relevance**: Models nonlinear vibrations in mechanical systems
*   ✅ **Analytical tractability**: Well-understood for validation purposes

**Agent Workflow**

**Operational Sequence**
```
┌─────────────────────────────────────────────────────────────────┐
│  1. DETECT    Amplitude ratio change triggers anomaly alert     │
│  2. PROPOSE   Dreamer generates structured action proposal      │
│  3. VALIDATE  Sheriff computes physics residual |r(t)|          │
│  4. DECIDE    If compliant → execute; else → veto + feedback    │
│  5. EXECUTE   Healer applies approved parameter updates         │
│  6. VERIFY    System continues with physics-validated state     │
└─────────────────────────────────────────────────────────────────┘
```

**Proposal Schema**

The Dreamer produces JSON-structured proposals validated by Pydantic:
```json
{
  "proposal_type": "parameter_update",
  "rationale": "Hard reset violates forcing term; propose increasing damping and reducing forcing.",
  "parameters": {
    "delta": 0.4,
    "alpha": null,
    "beta": null,
    "gamma": 0.15,
    "omega": null
  }
}
```

**Physics Residual Check**

The Sheriff computes the governing equation residual:
```python
def duffing_residual(t, x, x_t, x_tt, p):
    """Physics residual: should be ≈ 0 for valid trajectories."""
    return x_tt + p.delta * x_t + p.alpha * x + p.beta * (x ** 3) - p.gamma * np.cos(p.omega * t)
```
If `mean(|r|) > tolerance`, the proposal is **vetoed** with actionable feedback.

**AAS Integration**

This implementation aligns with Industry 4.0 standards through Asset Administration Shell (AAS) artifacts:

| Artifact | Purpose | Path |
| --- | --- | --- |
| **Shell** | Asset identity container | `aas/shells/oscillator.json` |
| **Nameplate** | Asset identification data | `aas/submodels/nameplate.json` |
| **TechnicalData** | Physics parameters ($\delta$, $\alpha$, $\beta$, $\gamma$, $\omega$) | `aas/submodels/technical_data.json` |
| **TimeSeries** | Measurement data x(t), v(t) | `aas/submodels/time_series.json` |

**Standards Compliance**: Artifacts follow IDTA specifications for interoperability with BaSyx, AASX Package Explorer, and other AAS-compatible tooling.

**Key Features**
*   **Physics-Informed Validation**: Residual-based compliance checking, DeepXDE PINN integration, First-principles equation enforcement.
*   **Multi-Agent Architecture**: Separation of concerns (propose/validate/execute), Veto-and-reprompt feedback loop, Extensible to real LLM backends.
*   **Real-Time Dashboard**: Streamlit + Plotly visualization, Interactive agent sequence cards, Physics residual plots.
*   **Configurable Pipeline**: Hydra-based configuration, Modular physics parameters, Reproducible experiments.
*   **Industry 4.0 Ready**: AAS JSON artifact generation, IDTA-compliant submodels, Standards-aligned identity.
*   **Research-Grade Implementation**: Clean, documented codebase, Comprehensive test suite, CI/CD pipeline ready.

**Installation**

**Prerequisites**
*   Python 3.10+
*   pip or uv package manager

**Quick Setup**
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/agentic-physics-digital-twin.git
cd agentic-physics-digital_twin

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -U pip
pip install -e ".[dev]"

# Set DeepXDE backend (IMPORTANT: before any imports)
export DDE_BACKEND=pytorch
```

**Run the Dashboard**
```bash
streamlit run app.py
```

**Run Tests**
```bash
pytest -q
```

**Demo Showcase**

**Demo Narrative**

| Step | Event | Outcome |
| --- | --- | --- |
| 1 | Anomaly detected in oscillator amplitude | System triggers recovery |
| 2 | Dreamer proposes "hard reset" (x=0) | **Vetoed** by Sheriff |
| 3 | Sheriff feedback: "violates forcing term" | Dreamer reprompts |
| 4 | Dreamer proposes parameter update | **Approved** ✓ |
| 5 | Healer executes: $\delta$=0.4, $\gamma$=0.15 | System recovered |

**Technical Results**
```
Anomaly detected: True
Proposals generated: 2
Validations performed: 2
Final parameters:
  delta: 0.4      # Increased damping
  alpha: -1.0     # Unchanged
  beta: 1.0       # Unchanged 
  gamma: 0.15     # Reduced forcing
  omega: 1.2      # Unchanged
Hard reset residual: mean=0.1916, max=0.3000 # REJECTED
Accepted update residual: mean=0.0002, max=0.1364 # APPROVED
```

**Project Structure**
```
agentic-physics-digital-twin/
├── 📄 app.py                      # Streamlit dashboard entrypoint
├── 📄 pyproject.toml              # Package configuration
├── 📄 README.md                   # This file
├── 📄 AGENTS.md                   # Repository guidelines
│
├── 📂 src/agentic_twin/           # Core package
│   ├── 📂 dreamer/                # Proposal agent
│   │   ├── agent.py               # DreamerAgent class
│   │   └── prompts.py             # LLM prompt templates
│   ├── 📂 sheriff/                # Validation agent
│   │   ├── validator.py           # Sheriff class
│   │   ├── physics.py             # Residual computation
│   │   ├── pinn.py                # DeepXDE PINN builder
│   │   └── baseline_ml.py         # MLP comparison baseline
│   ├── 📂 healer/                 # Control loop agent
│   │   └── controller.py          # run_agentic_episode()
│   ├── 📂 physics/                # Domain simulation
│   │   └── duffing.py             # Duffing oscillator
│   └── 📂 visualization/          # Dashboard components
│       ├── dashboard.py           # Streamlit layout
│       └── plots.py               # Plotly figures
│
├── 📂 configs/                    # Hydra configuration
│   ├── config.yaml                # Root config
│   ├── 📂 physics/
│   │   └── duffing.yaml           # Oscillator parameters
│   └── 📂 model/
│       └── default.yaml           # PINN/validator settings
│
├── 📂 aas/                        # Industry 4.0 artifacts
│   ├── 📂 shells/
│   │   └── oscillator.json        # Asset shell
│   └── 📂 submodels/
│       ├── nameplate.json         # Identification
│       ├── technical_data.json    # Parameters
│       └── time_series.json       # Measurements
│
├── 📂 tests/                      # Test suite
│   └── test_physics_compliance.py # Physics validation tests
│
├── 📂 docs/                       # Documentation
│   ├── IMPLEMENTATION_GUIDE.md    # Build guide
│   ├── 📂 images/                 # README diagrams
│   └── 📂 showcase/               # Demo artifacts
│
└── 📂 docker/                     # Containerization
    ├── Dockerfile
    └── docker-compose.yml
```

**Configuration**

**Hydra Structure**
```yaml
# configs/config.yaml
defaults:
  - physics: duffing
  - model: default

artifacts:
  log_dir: artifacts/logs
  model_dir: artifacts/models
```

**Physics Parameters**
```yaml
# configs/physics/duffing.yaml
nominal:
  delta: 0.2
  alpha: -1.0
  beta: 1.0
  gamma: 0.3
  omega: 1.2

anomaly:
  kind: delta_step
  start_time: 5.0
  delta_new: 0.05  # Anomaly: damping drops
```

**Validator Settings**
```yaml
# configs/model/default.yaml
validator:
  residual_tolerance: 0.1
  max_reprompts: 3

baseline_ml:
  layers: [64, 64]
  lr: 0.001
  epochs: 500
```

**Testing**

**Test Suite**
```bash
# Run all tests
pytest -q

# Run with coverage
pytest --cov=src/agentic_twin --cov-report=term-missing

# Run specific test
pytest tests/test_physics_compliance.py -v
```

**Key Test Cases**

| Test | Description |
| --- | --- |
| `test_residual_zero_for_harmonic` | Validates residual $\approx$ 0 for known analytical solution |
| `test_sheriff_veto_hard_reset` | Confirms Sheriff rejects x(t)=0 under forcing |


## 💡 Key Insights
- Introduction of Agentic Physics-Informed Digital Twins for trustworthy cyber-physical system recovery.
- A closed-loop cognitive control system with three specialized AI agents: Dreamer (proposes actions), Sheriff (validates via physics residuals), and Healer (orchestrates).
- The Sheriff agent uses Physics-Informed Neural Networks (PINNs) to enforce first-principles physics by evaluating proposals against governing differential equations, offering a principled compliance check beyond traditional thresholding.
- Demonstration using the Forced Duffing Oscillator, a nonlinear dynamical system, highlighting the approach's relevance for complex industrial systems.
- Integration with Industry 4.0 standards through Asset Administration Shell (AAS) artifacts for interoperability and digital twin representation.

## 📚 References
- hadijannat, Agentic Physics-Informed Digital Twin Demo, GitHub, https://github.com/hadijannat/agentic-physics-digital-twin *(source)*
- DeepXDE - Physics-Informed Neural Network library, https://github.com/lululxvi/deepxde *(cited)*
- Eclipse BaSyx - AAS reference implementation inspiration, https://www.eclipse.org/basyx/ *(cited)*
- IDTA - Submodel template specifications, https://industrialdigitaltwin.org/ *(cited)*

## 🏷️ Classification
The content focuses on developing an advanced AI system using multi-agent architecture, Physics-Informed Neural Networks (PINNs), and hybrid modeling for autonomous control and recovery in cyber-physical systems, which aligns with the core principles of Data Science (ML, stats, modélisation hybride, optimisation).
