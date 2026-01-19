---
title: "ModelPredictiveControl.jl: Open-Source Model Predictive Control Package for Julia"
date: 2026-01-19
category: Process_Engineering
confidence: 0.98
tags: ['Model Predictive Control', 'MPC', 'Julia', 'Control Systems', 'State Estimation', 'Process Control', 'Optimization', 'Nonlinear Control', 'Advanced Control']
source: "https://github.com/JuliaControl/ModelPredictiveControl.jl"
type: Article
source_type: GitHub Repository
hash: 223617
---

## 🎯 Relevance
This package is highly useful for process engineers and industrial data scientists for designing, simulating, and deploying advanced control strategies (MPC) in industrial processes. It offers a robust, flexible, and open-source platform in Julia, enabling improved process efficiency, stability, and adherence to operational constraints, potentially leading to significant ROI through optimized production and reduced waste. Its real-time and embedded capabilities make it suitable for practical industrial implementation.

## 📖 Content
GitHub - JuliaControl/ModelPredictiveControl.jl: An open source model predictive control package for Julia.

ModelPredictiveControl.jl
=========================

[![Build Status](https://github.com/JuliaControl/ModelPredictiveControl.jl/actions/workflows/CI.yml/badge.svg?branch=main)](https://github.com/JuliaControl/ModelPredictiveControl.jl/actions/workflows/CI.yml?query=branch%3Amain)[![codecov](https://camo.githubusercontent.com/9a15fa0713b1562794b0eef0747a9ef8846605cf1c42e46d592b17067e6f5a80/68747470733a2f2f636f6465636f762e696f2f67682f4a756c6961436f6e74726f6c2f4d6f64656c50726564696374697665436f6e74726f6c2e6a6c2f6272616e63682f6d61696e2f67726170682f62616467652e7376673f746f6b656e3d4b3456304c3131334d34)](https://codecov.io/gh/JuliaControl/ModelPredictiveControl.jl)[![doc-stable](https://camo.githubusercontent.com/78966041cb8a102bdaae0029ec342540ba69d657cfa80bdb439aafa3150221b3/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f646f63732d737461626c652d626c75652e737667)](https://juliacontrol.github.io/ModelPredictiveControl.jl/stable)[![doc-dev](https://camo.githubusercontent.com/63dcf31079b74cf2b5943d1d3916f53518db13d2ecb77cf2d1a2cac7d4ab967c/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f646f63732d6665762d626c75652e737667)](https://juliacontrol.github.io/ModelPredictiveControl.jl/dev)[![arXiv](https://camo.githubusercontent.com/eb978ee00fcc4b6af65ac715bc4859bbc0281ad9d9352bf27778e7de96da0174/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f61725869762d323431312e30393736342d6233316231622e737667)](https://arxiv.org/abs/2411.09764)

An open source [model predictive control](https://en.wikipedia.org/wiki/Model_predictive_control) package for Julia.

The package depends on [`ControlSystemsBase.jl`](https://github.com/JuliaControl/ControlSystems.jl) for the linear systems, [`JuMP.jl`](https://github.com/jump-dev/JuMP.jl) for the optimization and [`DifferentiationInterface.jl`](https://github.com/JuliaDiff/DifferentiationInterface.jl) for the derivatives.

🛠️ Installation
----------------

To install the `ModelPredictiveControl` package, run this command in the Julia REPL:

```julia
using Pkg; Pkg.add("ModelPredictiveControl")
```

🚀 Getting Started
------------------

To construct model predictive controllers (MPCs), we must first specify a plant model that is typically extracted from input-output data using [system identification](https://github.com/baggepinnen/ControlSystemIdentification.jl). The model here is linear with one input, two outputs and a large time delay in the first channel (a transfer function matrix, with s as the Laplace variable):

$$G(s)=\frac{y(s)}{u(s)}=\begin{bmatrix}\frac{2 e^{-20 s}}{10 s+1} \\ \frac{10}{4 s+1}\end{bmatrix}$$

We first construct the plant model with a sample time $T_s=1 s$:

```julia
using ModelPredictiveControl, ControlSystemsBase
G = [ tf( 2 , [10, 1])*delay(20)
      tf( 10, [4,  1]) ]
Ts = 1.0
model = LinModel(G, Ts)
```

Our goal is controlling the first output $y_1$, but the second one $y_2$ should never exceed 35:

```julia
mpc = LinMPC(model, Mwt=[1, 0], Nwt=[0.1])
mpc = setconstraint!(mpc, ymax=[Inf, 35])
```

The keyword arguments `Mwt` and `Nwt` are the output setpoint tracking and move suppression weights, respectively. A setpoint step change of five tests `mpc` controller in closed-loop. The result is displayed with [`Plots.jl`](https://github.com/JuliaPlots/Plots.jl):

```julia
using Plots
ry = [5, 0]
res = sim!(mpc, 40, ry)
plot(res, plotry=true, plotymax=true)
```

[![StepChangeResponse](https://github.com/JuliaControl/ModelPredictiveControl.jl/raw/main/docs/src/assets/readme_result.svg)](https://github.com/JuliaControl/ModelPredictiveControl.jl/blob/main/docs/src/assets/readme_result.svg)

See the [manual](https://juliacontrol.github.io/ModelPredictiveControl.jl/stable/manual/linmpc/) for more detailed examples.

✨ Features
----------

### 🎯 Model Predictive Control Features

*   🏭️ **Plant Model**: Linear or nonlinear models exploiting multiple dispatch.
*   ⛳️ **Objectives**: Tracking for inputs/outputs, move suppression, terminal costs, and economic costs.
*   ⏳️ **Horizons**: Distinct prediction/control horizons with custom move blocking.
*   📸 **Linearization**: Auto-differentiation for exact Jacobians.
*   ⚙️ **Adaptive MPC**: Manual model updates or automatic successive linearization.
*   🏎️ **Explicit MPC**: Specialized for unconstrained problems.
*   🚧 **Constraints**: Soft/hard limits on inputs, outputs, increments, and terminal states.
*   🔁 **Feedback**: Internal model or state estimators (see features below).
*   📡 **Feedforward**: Integrated support for measured disturbances.
*   🔮 **Preview**: Custom predictions for setpoints and measured disturbances.
*   📈 **Offset-Free**: Automatic model augmentation with integrators.
*   📊 **Visuals**: Easy integration with `Plots.jl`.
*   🧩 **Solvers**: Optimization via `JuMP.jl` (quadratic & nonlinear) and derivatives via `DifferentiationInterface.jl`.
*   📝 **Transcription**: Direct single/multiple shooting and trapezoidal collocation.
*   🩺 **Troubleshooting**: Detailed diagnostic information about optimum.
*   ⏱️ **Real-Time**: Optimized for low memory allocations with soft real-time utilities.
*   📟️ **Embedded**: Lightweight C code generation via `LinearMPC.jl`

### 🔭 State Estimation Features

*   🔍️ **Estimators**: Many Kalman filters, Luenberger, and Moving Horizon Estimator (MHE).
*   🎛️ **Customization**: Ability to use custom/external state estimates.
*   🌊 **Disturbances**: Estimate unmeasured disturbances via integrators on inputs/outputs.
*   🛣️ **Bumpless Transfer**: Smooth transitions from manual to automatic control.
*   ⌚️ **Timing**: Estimators available in filter (current) or predictor (delayed) forms.
*   🏷️ **MHE Types**: Formulations for both linear (quadratic optimization) and nonlinear plants.
*   🛡️ **MHE Constraints**: Tunable soft/hard constraints on state and noise estimates.

About
-----

An open source model predictive control package for Julia.

### Topics

julia, control-systems, nonlinear-dynamics, state-estimation, feedback-systems, model-predictive-control, nonlinear-control, automatic-control, linear-control, moving-horizon-estimation, feedforward-control, linear-dynamic-systems

## 💡 Key Insights
- ModelPredictiveControl.jl is an open-source Julia package for implementing Model Predictive Control (MPC) strategies.
- It supports both linear and nonlinear plant models, offering flexibility for various process engineering applications.
- The package integrates with key Julia libraries for control systems (`ControlSystemsBase.jl`), optimization (`JuMP.jl`), and automatic differentiation (`DifferentiationInterface.jl`).
- It provides a comprehensive set of MPC features including objective functions (tracking, move suppression, economic costs), distinct prediction/control horizons, adaptive and explicit MPC, and various constraint handling capabilities (soft/hard limits).
- Extensive state estimation features are included, such as Kalman filters, Luenberger observers, and Moving Horizon Estimators (MHE), with options for disturbance estimation and bumpless transfer.
- The package is optimized for real-time applications, offering low memory allocations and the capability for lightweight C code generation for embedded systems.

## 📚 References
- JuliaControl/ModelPredictiveControl.jl, GitHub Repository, Accessed 2024, https://github.com/JuliaControl/ModelPredictiveControl.jl *(source)*
- ControlSystemsBase.jl, GitHub Repository, https://github.com/JuliaControl/ControlSystems.jl *(cited)*
- JuMP.jl, GitHub Repository, https://github.com/jump-dev/JuMP.jl *(cited)*
- DifferentiationInterface.jl, GitHub Repository, https://github.com/JuliaDiff/DifferentiationInterface.jl *(cited)*
- ControlSystemIdentification.jl, GitHub Repository, https://github.com/baggepinnen/ControlSystemIdentification.jl *(cited)*
- Plots.jl, GitHub Repository, https://github.com/JuliaPlots/Plots.jl *(cited)*
- Model Predictive Control, Wikipedia, https://en.wikipedia.org/wiki/Model_predictive_control *(cited)*

## 🏷️ Classification
The content describes an open-source Julia package for Model Predictive Control (MPC), a core advanced control strategy used in process engineering for system design, simulation, and control implementation.
