---
title: "DeepThermoMix: Classical Thermodynamics Flavored with Modern Deep Learning for Multicomponent Activity Coefficient Prediction"
date: 2026-01-23
category: Data_Science
confidence: 1.00
tags: ['machine learning', 'deep learning', 'thermodynamics', 'activity coefficients', 'multicomponent mixtures', 'VLE', 'neural networks', 'MPNN', 'MLP', 'Gibbs-Duhem', 'process simulation', 'chemical engineering', 'hybrid modeling', 'Python', 'PyTorch']
source: "https://github.com/afriwahyudi/deepthermomix"
type: Article
source_type: GitHub Repository Documentation
hash: 215808
---

## 🎯 Relevance
This project offers a cutting-edge, data-driven approach to accurately predict activity coefficients, a critical thermodynamic property for process design, simulation, and optimization in chemical engineering. By leveraging deep learning and enforcing thermodynamic consistency, it can lead to more robust and accurate models, potentially reducing the need for extensive experimental data and improving the efficiency of chemical processes across various industries. It represents a significant learning opportunity in hybrid modeling (physics-informed machine learning) for industrial applications.

## 📖 Content
**DeepThermoMix**

**Project Overview**
DeepThermoMix is a thermodynamically consistent machine learning model designed to predict multicomponent activity coefficients across binary, ternary, and N-component mixtures.

**Paper**: [Link to the paper preprint](https://doi.org/10.26434/chemrxiv.10001495/v1)

**Documentation**: See `docs/` for comprehensive details:
*   **`docs/model.md`** — Neural network architecture, constraint modes, and loss functions
*   **`docs/data.md`** — Data pipeline and dataset splitting strategies
*   **`docs/train.md`** — Training workflow and hyperparameter optimization
*   **`docs/inference.md`** — Prediction for binary, ternary, and N-component systems
*   **`docs/user_guide.md`** — Tutorials and application examples

### **Core Concept**
The model builds upon the local-composition assumption found in classical thermodynamic models (e.g., Wilson, NRTL, UNIQUAC, UNIFAC). However, DeepThermoMix diverges from these traditional approaches by relaxing the explicit algebraic form of the intermolecular interaction expression.

[![Image 1: architectural overview](https://github.com/afriwahyudi/deepthermomix/raw/main/docs/figs/architectural_overview.png)](https://github.com/afriwahyudi/deepthermomix/blob/main/docs/figs/architectural_overview.png)

### **Key Innovation**
Instead of relying on rigid functional forms such as Boltzmann-distribution-like functions used to encode pairwise molecular interactions, DeepThermoMix utilizes Message Passing Neural Networks (MPNNs) and Multi-Layer Perceptrons (MLPs) as universal function approximators. This allows the model to learn complex, non-linear interactions while maintaining core physical assumptions.

The architecture enforces thermodynamic consistency through three complementary modes:

| Mode | Behavior |
| --- | --- |
| **'none'** | Direct prediction without constraints |
| **'soft'** | Penalty-based regularization via Gibbs-Duhem loss |
| **'hard'** | Physics-guaranteed consistency via automatic differentiation |

For detailed specifications, refer to `docs/model.md`.

### **Core Capabilities**

| Capability | Details |
| --- | --- |
| **Component agnostic** | Accepts arbitrary components in binary, ternary, or N-component mixtures |
| **Permutation invariant** | Invariant to component ordering |
| **Linear complexity** | Computational cost scales as O(N) with mixture size |
| **Learnable mixing rule** | Non-linear learned mixing rule replacing rigid algebraic forms |
| **Flexible constraint modes** | Unconstrained, soft (penalty), or hard (guaranteed) thermodynamic enforcement |
| **Uncertainty quantification** | Ensemble-based prediction variance estimation |

### **Supported Predictions**
*   **Binary VLE**: Phase equilibrium diagrams with pressure-composition-temperature calculations
*   **Ternary systems**: Excess Gibbs energy surfaces on simplex coordinates
*   **N-component mixtures**: Activity coefficients for arbitrary component counts
*   **NIST integration**: Automatic saturation pressure retrieval via NIST WebBook API

See `docs/inference.md` and `docs/user_guide.md` for usage examples.

**Project Environment**

### **Hardware specification**
```
> CPU: Intel(R) Core(TM) i9-13900KF
> GPU: NVIDIA RTX A4000 16 GB VRAM
> RAM: 128 GB DDR5
```

### **Installation**
#### Automatic Installation (Recommended)
Run the installation script from the project root in an Anaconda Prompt (base environment):

```python
python install.py
```
The script will prompt you to choose whether to install with CUDA-enabled GPU support or CPU only.

> **Which version should I choose?**
> 
> 
> *   **GPU support**: Recommended if you plan to train models or perform development work.
> *   **CPU only** : Sufficient for inference and moderate-sized predictions without the overhead of CUDA dependencies.

**Note:** For GPU support, ensure you have the following prerequisites installed before running `install.py`:

1.  NVIDIA driver
2.  CUDA Toolkit (cu129)
3.  cuDNN

#### Manual Installation
##### Step 1. Core requirements (GPU only)
1.  Install NVIDIA driver
2.  Install CUDA Toolkit (cu129)
3.  Install cuDNN

##### Step 2. Library setup
**For GPU-support:**
```bash
conda create --name deepthermomix-gpu python=3.11
conda activate deepthermomix-gpu
pip install torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu129
pip install torch_geometric
pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.8.0+cu129.html
conda install nomkl pandas matplotlib mpltern seaborn scikit-learn networkx rdkit jupyter ipykernel -c conda-forge -y
pip install optuna optuna-dashboard
```

**For CPU-only:**
```bash
conda create --name deepthermomix-cpu python=3.11
conda activate deepthermomix-cpu
pip install torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0
pip install torch_geometric
pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.8.0+cpu.html
conda install pandas nomkl matplotlib mpltern seaborn scikit-learn networkx rdkit jupyter ipykernel -c conda-forge -y
pip install optuna optuna-dashboard
```

### **Project Information**
#### Verified Environment & Build Versions

| Package | Version / Status |
| --- | --- |
| pandas | 2.3.3 |
| numpy | 1.26.4 |
| matplotlib | 3.10.7 |
| seaborn | 0.13.2 |
| sklearn | 1.7.2 |
| networkx | 3.5 |
| rdkit | 2025.09.1 |
| joblib | 1.5.2 |
| tqdm | 4.67.1 |
| torch | 2.8.0+cu129 |
| torchvision | 0.23.0+cu129 |
| torchaudio | 2.8.0+cu129 |
| torch_geometric | 2.7.0 |
| pyg_lib | 0.5.0+pt28cu129 |
| torch_scatter | 2.1.2+pt28cu129 |
| torch_sparse | 0.6.18+pt28cu129 |
| torch_cluster | 1.6.3+pt28cu129 |
| torch_spline_conv | 1.2.2+pt28cu129 |
| optuna | 4.5.0 |
| optuna_dashboard | 0.19.0 |
| jupyter | Installed (no version attribute) |
| ipykernel | 7.1.0 |

#### PyTorch & CUDA Info

| Property | Value |
| --- | --- |
| Torch version | 2.8.0+cu129 |
| CUDA available | True |
| CUDA version | 12.9 |
| cuDNN version | 91002 |
| GPU device count | 1 |
| Current GPU device | NVIDIA RTX A4000 |

**Citations**
Please also cite the following packages if used in your work:
*   PyG
*   RDKit

## 💡 Key Insights
- DeepThermoMix is a thermodynamically consistent machine learning model for predicting multicomponent activity coefficients across binary, ternary, and N-component mixtures.
- It replaces rigid algebraic forms of intermolecular interaction expressions found in classical thermodynamic models (e.g., Wilson, NRTL) with Message Passing Neural Networks (MPNNs) and Multi-Layer Perceptrons (MLPs) as universal function approximators.
- Thermodynamic consistency is enforced through flexible constraint modes: 'none' (direct prediction), 'soft' (penalty-based regularization via Gibbs-Duhem loss), and 'hard' (physics-guaranteed consistency via automatic differentiation).
- The model offers core capabilities such as component agnosticism, permutation invariance, linear computational complexity O(N), a learnable non-linear mixing rule, and ensemble-based uncertainty quantification.
- It supports predictions for binary VLE, ternary systems (excess Gibbs energy surfaces), N-component mixtures (activity coefficients), and integrates with NIST WebBook API for saturation pressure retrieval.

## 📚 References
- afriwahyudi, DeepThermoMix: Classical thermodynamics flavored with modern deep learning, GitHub, https://github.com/afriwahyudi/deepthermomix *(source)*
- Link to the paper preprint: https://doi.org/10.26434/chemrxiv.10001495/v1 *(cited)*
- PyG (PyTorch Geometric) *(cited)*
- RDKit *(cited)*

## 🏷️ Classification
The content describes a project that develops a 'thermodynamically consistent machine learning model' using deep learning techniques (MPNNs, MLPs) to predict activity coefficients, directly aligning with the 'ML, stats, modélisation hybride, optimisation' focus of the Data_Science category.
