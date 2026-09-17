---
title: 'TAM (Time series Additive Model): A Unified Framework for Interpretable, Physics-Informed,
  and High-Performance Time Series Forecasting'
date: '2026-09-17'
category: Data_Science
confidence: 0.98
tags: [Time Series Forecasting, Machine Learning, Deep Learning, PyTorch, Interpretable
    AI, Physics-informed AI, Generalized Additive Models (GAMs), Convex Optimization,
  Industrial Data Science, Python, Open Source, EDF, Data Drift, Uncertainty Quantification,
  'sector:petrochem']
source: https://github.com/EDF-Lab/tam
type: Article
source_type: GitHub Repository
hash: bd368f63da4b
---
## 🎯 Relevance
This framework is highly useful for industrial data scientists and process engineers who need to develop robust, scalable, and interpretable time series forecasting models. Its ability to incorporate physical laws and handle massive datasets with GPU acceleration offers significant ROI through improved predictive accuracy, better operational planning, and enhanced risk management, particularly in complex industrial systems like those in the energy sector.

## 📖 Content
TAM (Time series Additive Model) is a unified Python framework developed by EDF-Lab and Sorbonne Université for interpretable, physics-informed, and high-performance time series forecasting. It aims to bridge the gap between classical statistics (like Generalized Additive Models, GAMs) and modern tensor algebra, leveraging deep learning capabilities (PyTorch) for scalability.

**Key Features and Philosophy:**
*   **Interpretable:** Features a glass-box architecture with isolated, interpretable components, providing transparency similar to standard statistical models (linear regression, splines).
*   **Physics-Informed:** Allows embedding physical laws (ODEs/PDEs) directly into the model as analytical regularization constraints.
*   **High-Performance:** Designed to handle massive datasets and complex feature topologies by bypassing CPU limits and dual inversion bottlenecks. It uses GPU acceleration via PyTorch, robust memory management, Group-Chunking for infinite data volumes, and a matrix-free Sparse Conjugate Gradient solver for large feature spaces.
*   **Primal Space Resolution:** Solves a global convex optimization problem strictly in the Primal space.

**Stable Framework (v1.2+) Modules:**
*   **Machine Learning for Time Series:** Projects exogenous features into a finite-dimensional space via basis mappings against a target.
*   **Core (`StaticTAM`):** Fits the optimal linear model via primal resolution, with optional joint tuning of the ridge penalty $\lambda$ (using Generalized Cross-Validation - GCV) and other hyperparameters via Multi-Start Coordinate Descent.
*   **Adaptive (`AdaptiveTAM`):** Corrects residuals in real-time using parallel sliding-windows to handle concept drift.
*   **Expertise (`OperaTAM`):** Dynamically aggregates external expert models with mathematical regret bounds.
*   **Evaluation (`BenchmarkTracker`):** Tracks temporal degradation, calculates NaN-safe metrics, and analyzes residual autocorrelation.
*   **Distributional & Uncertainty (`statistics`):** Supports non-Gaussian targets (Poisson, Gamma, Binomial), Location-Scale modeling, EM Mixtures, Gaussian Copulas, and rigorous risk bounding via Conformal Prediction (ACI) and Extreme Value Theory (EVT).

**Experimental Research Lab (BETA / EXP) Modules:**
*   **Physics-Informed (`UniversalPhysicsEffect`) (BETA):** Embeds physical laws directly.
*   **Dynamic (`KalmanTAM`) (BETA):** Tracks evolving behaviors and coefficients via an Extended Kalman Filter.
*   **Hierarchy (`HierarchicalTAM`) (BETA):** Optimizes parent/child series simultaneously.
*   **AutoML (`AutoTAM`) (EXP):** Evolutionary Search for optimal GAM topologies.
*   **Hybrid (`NeuralTAM`) (EXP):** Integrates Deep Neural Networks via orthogonal residual backfitting.

**System Architecture Overview (v1.2.1+):**
The architecture is divided into four tiers:
1.  **Data Ingestion & Preprocessing:** Raw data flows through dynamic normalizers.
2.  **Core Engine:** Processed by the `StaticTAM` core.
3.  **Meta-Learner Orchestrators:** Outputs wrapped by advanced Meta-Learners (`AdaptiveTAM`, `OperaTAM`) to handle real-world constraints.
4.  **Output Management.**

```mermaid
graph TD
    A[Raw Data] --> B[Dynamic Normalizers]
    B --> C[StaticTAM Core Engine]
    C --> D[Meta-Learner Orchestrators (AdaptiveTAM, OperaTAM, etc.)]
    D --> E[Output Management]
```

**The Dictionary of Effects:**
TAM allows building models by summing generic "Effects," each with its mathematical behavior, mapping function, and structural penalty. Examples include:
*   [Linear](https://github.com/EDF-Lab/tam/blob/main/math/spectrum/LINEAR.md)
*   [Fourier](https://github.com/EDF-Lab/tam/blob/main/math/spectrum/FOURIER.md)
*   [Spline](https://github.com/EDF-Lab/tam/blob/main/math/spectrum/SPLINES.md)
*   [Chebyshev](https://github.com/EDF-Lab/tam/blob/main/math/spectrum/CHEBYSHEV.md)
*   [Categorical](https://github.com/EDF-Lab/tam/blob/main/math/spectrum/CATEGORICAL.md)
*   [Interaction](https://github.com/EDF-Lab/tam/blob/main/math/spectrum/CROSS_TENSOR.md)
*   [RBF](https://github.com/EDF-Lab/tam/blob/main/math/spectrum/RBF.md)
*   [Neural](https://github.com/EDF-Lab/tam/blob/main/math/spectrum/NEURAL.md)
*   [Tree](https://github.com/EDF-Lab/tam/blob/main/math/spectrum/TREE.md)
*   [Linear Tree](https://github.com/EDF-Lab/tam/blob/main/math/spectrum/LINEAR_TREE.md)
*   [Wavelet](https://github.com/EDF-Lab/tam/blob/main/math/spectrum/WAVELETS.md)
*   [PID](https://github.com/EDF-Lab/tam/blob/main/math/spectrum/PID.md)
*   [Physics](https://github.com/EDF-Lab/tam/blob/main/math/spectrum/PHYSICS_PIKL.md) (BETA)

**Installation:**
```bash
pip install tam-ml
```
Requires PyTorch with appropriate hardware distribution (CUDA for NVIDIA, MPS for Apple Silicon) for GPU acceleration.

**Quick Start Example:**
```python
import pandas as pd
import numpy as np
import tam as ta
from importlib import resources

# 1. Load Data
df = pd.read_csv(resources.files('tam.data').joinpath('airpassengers.csv')).dropna().copy()
df['date'] = pd.to_datetime(df['date'])
d_dict = {'train': df.iloc[:-24], 'test': df.iloc[-24:]}

# 2. Define competing architectures via formulas
f1 = "log_passengers ~ c(month, topo='fourier', ap=-8.0) + l(lag_log_passengers, ap=-30.0)"
f2 = "log_passengers ~ n(month) + l(lag_log_passengers, ap=-30.0)"

# 3. Fit and predict standard models
df['E1'] = ta.StaticTAM(formula=f1, date_col="date").fit(d_dict['train']).predict(df)["Estimatedlog_passengers"].values
df['E2'] = ta.StaticTAM(formula=f2, date_col="date").fit(d_dict['train']).predict(df)["Estimatedlog_passengers"].values

# 4. Dynamically aggregate experts using OperaTAM
opera = ta.OperaTAM("log_passengers ~ l(E1) + l(E2)", algorithm='MLPOL', date_col='date', horizon_steps=12)
df['OPERA'] = opera.predict_online(df)['prediction_opera'].values

# Option B (Production): Train on history, apply frozen weights to the future
# opera.fit(d_dict['train'])
# test_predictions = opera.predict(d_dict['test'])

# 5. Evaluate and plot
for name, col in [("Expert 1", "E1"), ("Expert 2", "E2"), ("OPERA", "OPERA")]:
    tr = ta.BenchmarkTracker(name)
    tr.y_pred_full = np.exp(df[col].values)
    tr.slice_and_evaluate(d_dict, target_col='value')
    print(f"[{name}] Test MAPE: {tr.get_metric('test', 'MAPE'):.2f}%")

opera.plot_weights(df=df)
```

**Project Structure & Documentation:**
*   `src/tam/` - SOURCE CODE
*   `math/` - Mathematical theory, theorems, and RKHS equations.
*   `architecture/` - PyTorch OOP, VRAM management, and code extraction.

**Citation:**
If used in research, cite the TAM package and the FORCE Dataset using their Zenodo DOIs.

## 💡 Key Insights
- TAM is a Python framework for interpretable, physics-informed, and high-performance time series forecasting, bridging classical statistics with modern tensor algebra and deep learning.
- It offers a glass-box architecture, GPU acceleration via PyTorch, and robust memory management techniques (Group-Chunking, Sparse Conjugate Gradient) to handle massive datasets and complex feature spaces.
- The framework includes stable modules for core modeling (`StaticTAM`), concept drift (`AdaptiveTAM`), expert aggregation (`OperaTAM`), and comprehensive uncertainty quantification (`statistics`).
- Experimental modules are under active development for physics-informed modeling, Kalman filtering, hierarchical optimization, AutoML, and hybrid neural network integration.
- Developed by EDF-Lab and Sorbonne Université, TAM is designed for robust industrial deployment, with applications in sectors like energy, finance, and medicine.

## 📚 References
- EDF-Lab/tam: TAM (Time series Additive Model) - The unified framework for interpretable, physics-informed, and high-performance time series forecasting, GitHub, URL: https://github.com/EDF-Lab/tam *(source)*
- TAM: https://doi.org/10.5281/zenodo.20543271 *(cited)*
- FORCE Dataset: https://doi.org/10.5281/zenodo.21109133 *(cited)*
- JOSS Paper: https://github.com/EDF-Lab/tam/blob/main/paper.md *(cited)*
- Allioux, Yann and Goude, Yannig. (2026). TAM: Time series Additive Model (v1.3.0). Zenodo. doi:10.5281/zenodo.22544995 *(cited)*
- Allioux, Yann and Goude, Yannig. (2026). FORCE Dataset: French Open Research Catalogue of Energy - 2026 Snapshot. Zenodo. doi:10.5281/zenodo.21109134 *(cited)*

## 🏷️ Classification
The content describes a Python library for advanced time series forecasting using machine learning, statistical modeling, and optimization techniques, which are core components of data science.
