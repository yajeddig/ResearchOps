---
title: 'SD-DPC: Sparse Dictionary Differentiable Predictive Control (SINDy identification
  + sparse closed-form policy learning)'
date: '2026-10-16'
category: Hybrid_SciML
confidence: 0.88
tags: [sindy, control-mpc, identification, simulation-dynamic, optimization]
sectors: []
source: https://solaris-jhu.github.io/SD-DPC-website/
type: Article
source_type: Paper
hash: 75b7b8435940
---
## 🎯 Relevance
Offers a route to turn identified (SINDy) process models into explicit, certifiable, microsecond-cost controllers that can run on PLC or edge hardware, as an alternative to online MPC or opaque NN policies. It fits hybrid and data-driven control of industrial processes (tank levels, nonlinear reactors, constrained trajectory tasks) where interpretability, memory footprint and robustness guarantees matter.

## 📖 Content
## Overview

SD-DPC (Garmroodi & Drgoňa, JHU SOLARIS, 2026) is a framework for learning **sparse, interpretable, closed-form feedback policies** for nonlinear systems from trajectory data. It chains two stages, both based on the same sequentially thresholded gradient descent:

1. **Sparse identification** of the dynamics by rollout-based SINDy.
2. **Differentiable predictive control (DPC)** policy learning, where the policy is a sparse combination of dictionary functions.

```mermaid
flowchart LR
  A[Trajectory data] --> B[Rollout-based SINDy: sparse model f(x,u)]
  B --> C[Sparse dictionary policy pi(x,r)=Proj(Theta*phi)]
  C --> D[Differentiate constrained finite-horizon MPC loss through closed-loop rollouts]
  D --> E[Sequential thresholding + debiasing]
  E --> F[Explicit feedback law with a few terms]
```

## Methodology

### Stage 1: Sparse identification from rollout error
- Dynamics are written as a linear combination of library functions, x_{k+1} = F(x_k,u_k;Ξ).
- Coefficients are fit by **multistep rollout error**, not by state derivatives, so numerical differentiation never enters the objective.
- With a one-step horizon and an explicit Euler step, the loss reduces to the classical l1-regularized SINDy regression with forward-difference derivatives.

### Stage 2: Sparse dictionary policy
- The feedback law uses a second library over the policy inputs (state, reference).
- The output is **projected onto the admissible input set**, so input constraints hold by construction, and each channel keeps its own subset of terms.
- Forward pass: exact projection. Backward pass: a **banded, leaky surrogate derivative**, so coefficients feeding a saturated channel still receive gradient.

### Policy learning
Coefficients are obtained by differentiating a constrained predictive-control objective through closed-loop rollouts of the identified model over sampled initial conditions and references. The stage loss combines tracking, control regularization and differentiable hinge penalties for state-constraint violations.

### Algorithm 1: sequentially thresholded gradient descent with debiasing
1. Update the coefficients with a first-order method on loss + l1 subgradient.
2. Every fixed number of epochs, prune entries below a threshold λ per channel. Pruned terms are locked at zero, terms removed from every channel are dropped from the library, and the optimizer is reinitialized.
3. Early stopping via patience once the support is stable.
4. **Debias phase**: refit the retained coefficients without the l1 penalty, warm-started from the biased sparse solution, to remove shrinkage bias.

## Theoretical statements
Under an assumption of compact sets, Lipschitz library functions and a bounded library:

| Result | Content |
|---|---|
| Prop. 1 | Finite support stabilization: a pruned coefficient never returns, so the thresholding loop terminates after at most (number of coefficients) prune events. |
| Prop. 2 | Pruning cost: zeroing entries below the threshold raises the objective by a bounded amount, which is why the l1 weight and the threshold are tuned jointly. |
| Prop. 3 | Sensitivity and perturbation: the policy is Lipschitz with an explicit constant computed from the coefficients and the library. Pruning moves the action by a bounded amount, and trajectory deviation under model or policy error is bounded. A constraint with margin on one trajectory therefore holds on the other. |

Because every constant follows from the two sparse coefficient matrices and the library, the certificate is cheap. For deep neural policies the equivalent bounds need products of layer norms or semidefinite relaxations.

## Case studies
1. **Two-tank system**: states are two levels, inputs are pump command and valve split. Task: track time-varying references with hinge penalties on level bounds.
2. **Forced Van der Pol oscillator**: regulate to the origin, with limit-cycle dynamics around an unstable origin.
3. **2-D integrator with obstacle avoidance**: linear dynamics, nonlinear state constraint (circle of radius 1.5), reaching a terminal setpoint.

The policy is trained on the **identified** model and evaluated on the **true plant**, so the results include model mismatch.

### Baselines
- **IPOPT**: per-scenario optimization with exact model, a performance reference.
- **NN-DPC**: 2x32 ReLU MLP trained with the same closed-loop objective on the same identified model.
- **NN-Distilled**: sparse policy regressed onto NN-DPC actions on the terms SD-DPC retained. It isolates the effect of how coefficients are obtained on a common support.

## Results (500 held-out scenarios)

| System | Method | Task loss [1e-3] | Time/step | Memory | Violations |
|---|---|---|---|---|---|
| Two-tank | IPOPT | 8.8e-6 | 8444 µs | 26 MiB | 0% |
| | NN-DPC | 0.144 | 30 µs | 5.01 kB | 0% |
| | **SD-DPC** | **0.012** | 17 µs | 0.047 kB | 0% |
| | NN-Distilled | 0.209 | 17 µs | 0.047 kB | 0% |
| Van der Pol | NN-DPC | 41.0 | 29 µs | 5.01 kB | 0% |
| | SD-DPC | 49.9 | 17 µs | 0.023 kB | 0% |
| | NN-Distilled | 96.8 | 17 µs | 0.023 kB | 0% |
| 2-D integrator | NN-DPC | 0.298 | 28 µs | 5.01 kB | 0% |
| | SD-DPC | 4.75 | 17 µs | 0.094 kB | 0% |
| | NN-Distilled | 62.6 | 17 µs | 0.094 kB | **60.8%** |

- Retained terms: 6 (two-tank), 3 (Van der Pol, out of 14 candidates), 12 (integrator).
- SD-DPC cumulative control effort is within 0.6% of the IPOPT minimum on the integrator.
- The distilled policy fails because its regression has no obstacle penalty. The imitation error reaches 0.35 on student-visited states, while the teacher clears the obstacle by only 0.06.
- Van der Pol: the closed loop is analytic, and global asymptotic stability of the origin follows from the learned coefficients.
- **Sensitivity certificate**: conservative by a factor of at most 1.7 versus the autodiff maximum gradient on a dense grid, and the pruning bound held at every prune.
- The cost of sparsity is system dependent: flat for Van der Pol, degrading for the two-tank beyond the selected l1 weight.

## Limitations and future work
- Constraint satisfaction is promoted by penalties and verified empirically, with no hard guarantee.
- Future work: safety filters, region-of-attraction certification, robustness under identification error, noisy data, library mismatch, task-informed libraries, and online adaptation of coefficients.

## Code
Python 3.10, PyTorch 2.6, Neuromancer 1.5.3, CasADi (IPOPT benchmark).

```bash
git clone https://github.com/SOLARIS-JHU/SD-DPC.git && cd SD-DPC
pip install -e .
CASE=TwoTank   # or VanDerPol, DoubleIntegrator
python scripts/$CASE/system_id.py
python scripts/$CASE/train_sd_dpc.py
python scripts/$CASE/train_nn_dpc.py
python scripts/$CASE/evaluation.py
```

The page also contains an interactive browser demo of the policy training and a "try it yourself" mode.

## 💡 Key Insights
- Policy terms are selected by closed-loop constrained MPC performance rather than by imitating a pretrained NN controller, which avoids distillation failure (60.8% obstacle violations for NN-Distilled vs 0% for SD-DPC on the same terms).
- The same sequentially thresholded gradient descent with debiasing is reused for the SINDy model and for the policy, giving a unified, simple pipeline.
- SINDy is fit on multistep rollout error, so no numerical differentiation of noisy data is needed; one step plus Euler recovers classical SINDy.
- The projection onto input limits is exact in the forward pass, and a banded leaky surrogate gradient keeps saturated channels trainable.
- The final policy is tiny (under 0.1 kB, 17 µs per step) versus a 5 kB NN and 18–26 MiB / 0.3–8 ms per IPOPT solve, which suits embedded PLC/edge deployment.
- Explicit Lipschitz and sensitivity certificates are computed from coefficients alone, conservative by at most 1.7x, and enable perturbation and constraint-margin transfer arguments.
- A closed-form policy and model enable analytic stability proofs, e.g. global asymptotic stability for the Van der Pol case.
- Limitations: soft constraints only, a hand-chosen library, and benchmarks restricted to low-dimensional systems; the accuracy cost depends on the system (the integrator loses 16x versus NN-DPC).

## 📚 References
- Garmroodi, A. R. D. & Drgoňa, J. (2026). SD-DPC: Sparse Dictionary Differentiable Predictive Control. arXiv preprint arXiv:2610.02466. Project page: https://solaris-jhu.github.io/SD-DPC-website/ *(source)*
- Code repository: https://github.com/SOLARIS-JHU/SD-DPC *(source)*
- Brunton, Proctor & Kutz (2016). Discovering governing equations from data by sparse identification of nonlinear dynamical systems (SINDy). PNAS. *(cited)*
- Drgoňa et al. Differentiable Predictive Control (DPC) and the Neuromancer library. *(cited)*

## 🏷️ Classification
The content combines SINDy-based sparse system identification with differentiable predictive control policy learning, which is a scientific-ML (SciML) methodology for control.
