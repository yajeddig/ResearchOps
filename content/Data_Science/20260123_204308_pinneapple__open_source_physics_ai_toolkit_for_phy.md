---
title: "PINNeAPPle: Open-source Physics AI Toolkit for Physics-Informed Neural Networks and Scientific ML"
date: 2026-01-23
category: Data_Science
confidence: 1.00
tags: ['Physics-Informed Neural Networks', 'PINNs', 'Scientific Machine Learning', 'Hybrid Modeling', 'Numerical Solvers', 'Geometry Processing', 'Data Pipelines', 'Reproducible ML', 'CFD', 'FEA', 'Digital Twin', 'Process Modeling', 'Optimization', 'Python', 'Open-source', 'Machine Learning Toolkit', 'AI']
source: "https://github.com/barrosyan/PINNeAPPle"
type: Article
source_type: Article
hash: 204308
---

## 🎯 Relevance
This toolkit is highly valuable for process engineering and industrial data science. It provides a structured, open-source platform for developing Physics-Informed AI models, which are critical for creating accurate digital twins, optimizing complex industrial processes, performing predictive maintenance, and simulating systems where data may be sparse or expensive. Its emphasis on physical consistency, scalability, and auditability directly addresses key challenges in industrial applications, offering a significant learning opportunity for practitioners to build robust hybrid models combining physical laws with data-driven insights.

## 📖 Content
GitHub - barrosyan/PINNeAPPle: Pinneaple is an open-source Physics AI toolkit for Physics-Informed Neural Networks (PINNs), scientific ML, geometry processing, solvers, and reproducible training pipelines.

Pinneaple 🍍
============

**Unified Physical Data, Geometry, Models and Training for Physics AI**

Pinneaple is an open-source Python platform designed to **bridge real physical data, geometry, numerical solvers, and machine learning models** into a single coherent ecosystem for **Physics-Informed AI**.

It is built to serve both **research** and **industrial workflows**, with strong emphasis on:

*   Physical consistency
*   Scalability
*   Auditability
*   Interoperability with CFD / CAD / scientific data formats

✨ Key Features
--------------

### 📦 Unified Physical Dataset (UPD)

A standardized abstraction to represent _physical samples_, including:

*   Physical state (grids, meshes, graphs)
*   Geometry (CAD / mesh)
*   Governing equations, ICs, BCs, forcings
*   Units, regimes, metadata and provenance

Used consistently across **data loading, training, validation, and inference**.

### 🌍 Data & IO (`pinneaple_data`)

*   NASA / scientific-ready data pipelines
*   Zarr-backed datasets with:
    *   Lazy loading
    *   Sharding
    *   Adaptive prefetch
    *   Byte-based LRU caching
*   Deterministic shard-aware iterators
*   Physical validation and schema enforcement

### 📐 Geometry & Mesh (`pinneaple_geom`)

*   CAD generation (CadQuery)
*   STL / mesh IO (trimesh, meshio, OpenFOAM MVP)
*   Mesh repair, remeshing and simplification
*   Sampling (points, grids, barycentric)
*   Geometry-aware feature extraction

### 🧠 Model Zoo (`pinneaple_models`)

A curated catalog of architectures commonly used in Physics AI:

*   PINNs (Vanilla, XPINN, VPINN, XTFC, Inverse PINN, PIELM)
*   Neural Operators (FNO, DeepONet, PINO, GNO, UNO)
*   Graph Neural Networks (GraphCast-style, GNN-ODE, equivariant GNNs)
*   Transformers (Informer, FEDformer, Autoformer, TFT)
*   Reduced Order Models (POD, DMD, HAVOK, Operator Inference)
*   Classical & hybrid models (Kalman, ARIMA, Koopman, ESN)
*   Physics-aware & structure-preserving networks

All models are discoverable via a **central registry**.

### 🧮 Physics Loss Factory (`pinneaple_pinn`)

*   Symbolic PDE definitions (SymPy-based)
*   Automatic differentiation graph construction
*   PINN-ready residuals and constraints
*   Works directly with UPD samples

### ⚙️ Solvers (`pinneaple_solvers`)

Numerical solvers and mathematical tools used for:

*   Data generation
*   Feature extraction
*   Validation

Includes:

*   FEM / FVM (MVP)
*   FFT
*   Hilbert–Huang Transform
*   Adapters to/from UPD

### 🏗️ Synthetic Data Generation (`pinneaple_data.synth`)

Generate datasets from:

*   Symbolic PDEs
*   Parametric distributions
*   Curve fitting from real data
*   Images and signals
*   Geometry perturbations and CAD parameter sweeps

### 🚂 Training & Evaluation (`pinneaple_train`)

*   Deterministic, auditable training
*   Dataset splitting (train/val/test)
*   Preprocessing pipelines & normalizers
*   Metrics & visualization
*   Physics-aware loss integration
*   Reproducible runs (seeds, env fingerprinting)
*   Checkpointing & inference utilities

🚀 Installation
---------------

Pinneaple is currently distributed as an open-source research & industry framework directly from GitHub.

1.   Clone the repository

```shell
git clone https://github.com/barrosyan/pinneaple.git
cd pinneaple
```

2.   Create a virtual environment (strongly recommended)

Python ≥ 3.10 is recommended (3.11 works well; 3.13 may require extra care on Windows).

```shell
python -m venv .venv
```

Activate it:

Linux / macOS

```shell
source .venv/bin/activate
```

Windows (PowerShell)

```shell
.venv\Scripts\Activate.ps1
```

3.   Install core dependencies

Install Pinneaple in editable (development) mode:

```shell
pip install -e .
```

This installs:

pinneaple_data

pinneaple_geom

pinneaple_models

pinneaple_pinn

pinneaple_pdb

pinneaple_solvers

pinneaple_train

4.   Optional dependencies (recommended)

Pinneaple is modular. Install only what you need:

🔹 Geometry / CAD / Mesh

```shell
pip install trimesh meshio
pip install cadquery  # requires OCC stack
```

⚠️ On Windows, CadQuery is best installed via Conda:

```shell
conda create -n pinneaple-cq python=3.10 cadquery -c conda-forge
conda activate pinneaple-cq
pip install -e .
```

🔹 Scientific & ML stack

```shell
pip install torch numpy scipy sympy
```

Optional (recommended for performance & operators):

```shell
pip install zarr numcodecs
pip install open3d fast-simplification
```

5️. Development & testing tools

For contributors:

```shell
pip install -e ".[dev]"
```

1.   Verify installation

Quick smoke test:

```python
from pinneaple_models.register_all import register_all
from pinneaple_models.registry import ModelRegistry

register_all()
print("Registered models:", len(ModelRegistry.list()))
```

🧠 Notes

Pinneaple is not yet released on PyPI — cloning the repo is required.

Some features (CFD, CAD, large-scale Zarr) rely on optional native backends.

All examples in examples/ are runnable after installation.

🧪 Quick Example
----------------

```python
from pinneaple_data.physical_sample import PhysicalSample
import xarray as xr
import numpy as np

ds = xr.Dataset(
    data_vars=dict(T2M=(("t","x"), np.random.randn(24,16))),
    coords=dict(t=np.arange(24), x=np.arange(16))
)

sample = PhysicalSample(
    state=ds,
    domain={"type": "grid"},
    schema={"governing": "toy"},
)

print(sample.summary())
```

🧑‍🔬 Who Is This For?
----------------------

*   Physics AI researchers
*   CFD / FEA / climate ML teams
*   Industrial R&D groups
*   Scientific ML practitioners
*   Anyone building **surrogates, inverse models, or hybrid solvers**

🤝 Contributing
---------------

We welcome contributions in:

*   New datasets & adapters
*   Models and solvers
*   Benchmarks
*   Documentation

See [CONTRIBUTING.md](https://github.com/barrosyan/PINNeAPPle/blob/main/CONTRIBUTING.md).

📄 License
----------

Apache 2.0 — see [LICENSE](https://github.com/barrosyan/PINNeAPPle/blob/main/LICENSE).

📚 Citation
-----------

If you use Pinneaple in research, please cite via `CITATION.cff`.

🌱 Project Philosophy
---------------------

Pinneaple is **not** a single model or method.

It is a **platform** — designed to let physical data, geometry, equations and learning systems interact cleanly, reproducibly, and at scale.

> _From raw physics to deployable intelligence._

**Status:** Early but ambitious.

**Feedback & collaboration welcome.**

## 💡 Key Insights
- PINNeAPPle is an open-source Python toolkit for Physics-Informed AI, integrating physical data, geometry, numerical solvers, and machine learning models.
- It emphasizes physical consistency, scalability, auditability, and interoperability with scientific data formats (CFD/CAD).
- Key components include a Unified Physical Dataset (UPD) for standardized physical sample representation, advanced data I/O, geometry and mesh processing capabilities, and a comprehensive Model Zoo.
- The toolkit provides a Physics Loss Factory for symbolic PDE definitions and automatic differentiation, along with various numerical solvers and synthetic data generation tools.
- It offers a robust training and evaluation pipeline designed for deterministic, auditable, and reproducible Physics-AI model development.
- The platform supports a wide range of Physics AI applications, including surrogates, inverse models, and hybrid solvers, targeting researchers and industrial R&D groups in fields like CFD/FEA and climate ML.

## 📚 References
- barrosyan/PINNeAPPle: Pinneaple is an open-source Physics AI toolkit for Physics-Informed Neural Networks (PINNs), scientific ML, geometry processing, solvers, and reproducible training pipelines., GitHub, https://github.com/barrosyan/PINNeAPPle *(source)*

## 🏷️ Classification
The content describes an open-source Python toolkit focused on Physics-Informed Neural Networks (PINNs), scientific machine learning, and hybrid modeling, which directly falls under the 'ML, stats, modélisation hybride, optimisation' aspects of Data_Science.
