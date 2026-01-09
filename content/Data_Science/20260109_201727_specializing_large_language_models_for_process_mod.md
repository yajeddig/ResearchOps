---
title: "Specializing Large Language Models for Process Modeling via Reinforcement Learning with Verifiable and Universal Rewards"
date: 2026-01-09
category: Data_Science
confidence: 1.00
tags: ['Reinforcement Learning', 'Large Language Models', 'Process Modeling', 'Business Process Management', 'POWL', 'Petri Nets', 'BPMN', 'LLM-as-a-Judge', 'GRPO', 'Process Mining', 'Natural Language Processing', 'Model Generation', 'Behavioral Fidelity', 'Structural Validity']
source: "Telegram Document"
type: Article
source_type: Paper
hash: 201727
---

## 🎯 Relevance
This research is highly relevant for industrial data science, as it offers a method to automate and improve the accuracy of process model generation from natural language. This can significantly reduce the labor and expertise required for creating and maintaining process models, accelerating digital twin initiatives, improving conformance checking, and enabling more efficient process analysis and automation, leading to substantial ROI in business process management.

## 📖 Content
The document describes a novel approach to automatically generate formal, executable process models from natural-language descriptions using specialized Large Language Models (LLMs). The core problem addressed is that traditional process modeling is labor-intensive, requiring expertise in both the domain and formal notations like Petri nets or BPMN, while many organizations possess rich informal textual descriptions (e.g., work instructions).

Generic LLMs, despite their general-purpose capabilities, often produce syntactically invalid or behaviorally incorrect process models when applied directly to this task. To overcome this, the authors propose specializing a pretrained LLM using Reinforcement Learning (RL).

**Key Concepts and Methodology:**

1.  **Process Model Generation**: The task is defined as taking a textual process description `x` and automatically producing a complete, executable process model `M` that captures the described behavior.

2.  **Partially Ordered Workflow Language (POWL)**:
    *   POWL is chosen as the intermediate representation for process models. It is a graph-based representation combining a strict partial order with control-flow operators for exclusive choice (XOR) and looping (LOOP).
    *   POWL models are programmatically constructible from text using the `pm4py` Python library, allowing for automatic verification and translation into Petri nets or BPMN.
    *   **Formal Definition Snippet (Conceptual):**
        *   An activity `a ∈ Σ∪ {τ}` is a model.
        *   If `M₁,..., Mk` are models, then `XOR(M₁,..., Mk)` is a model.
        *   If `B` and `R` are models, then `LOOP(B, R)` is a model.
        *   If `N = M1, ..., Mk` is a finite set of models and `≺⊆ N × N` is a strict partial order, then `PO(N, ≺)` is a model.

3.  **Structural Validity Objectives (S1-S6)**:
    *   S1: Code parses (valid AST) and uses only allowed POWL/utility imports.
    *   S2: Constructs a single, top-level POWL object (`Transition`, `SilentTransition`, `OperatorPOWL`, `StrictPartialOrder`).
    *   S3: Operator arities/types are correct (e.g., `LOOP` has (body, redo); `XOR` has ≥ 2 children).
    *   S4: Strict partial order is irreflexive, asymmetric, and acyclic.
    *   S5: Activity labels are strings; silent steps use designated symbol; no inconsistent object reuse.
    *   S6: No side effects beyond model construction.
    *   A predicate `validstruct(y) ∈ {0,1}` and a soft code-quality score `Scode ∈ [0, 1]` summarize these.

4.  **Behavioral Fidelity (Footprints)**:
    *   Footprints are a compact, relation-based summary of a process model's observable behavior, capturing direct succession (`Seq(M)`) and potential concurrency (`Par(M)`).
    *   `footprints(M) = (Seq(M), Par(M))`.
    *   Similarity to a reference model `Mref` is measured via the Jaccard index:
        $$\text{sim}(M, M_{\text{ref}}) = \frac{|\text{Seq}(M) \cap \text{Seq}(M_{\text{ref}})| + |\text{Par}(M) \cap \text{Par}(M_{\text{ref}})|}{|\text{Seq}(M) \cup \text{Seq}(M_{\text{ref}})| + |\text{Par}(M) \cup \text{Par}(M_{\text{ref}})|}$$

5.  **Model Complexity**: `FP(M) = |Seq(M)| + |Par(M)|` is used as a proxy for structural richness.

6.  **Optimization with GRPO (Group Relative Policy Optimization)**:
    *   GRPO is used to optimize the LLM policy. For a given prompt, the model generates a small group of candidate programs. Each program is scored, and those scoring better than the group's average are reinforced.
    *   Advantages `A_i = r_i - \bar{r}` are used for updates.

7.  **Reward Signals**:
    *   **Universal reward (LLM-as-a-Judge)**: An evaluator LLM inspects the prompt and `K` candidates, returning per-candidate grades in `[-1,1]` based on correctness, completeness, and adherence to the prompt. This provides dense, prompt-relative feedback.
    *   **Verifiable reward (footprints agreement)**: Rewards `r_simple(M)` based on `sim(M, Mref)`.
        $$r_{\text{simple}}(M) = g(\text{sim}(M, M_{\text{ref}}))$$
        (where `g` is a monotone map `[0,1] → [-1,1]`)
    *   **Verifiable reward (self-agreement)**: For reference-free scenarios, encourages consensus among `K` candidates.
        $$r_{\text{self}}(M_i) = \frac{1}{K-1} \sum_{j \neq i} \text{sim}(M_i, M_j)$$
    *   **Verifiable reward (footprint shaping)**: Controls model complexity.
        $$r_{\pm \text{foot}}(M) = \begin{cases} h(\text{FP}(M)) & \text{encourage richer behavior} \\ 1-h(\text{FP}(M)) & \text{encourage simpler behavior} \end{cases}$$
        (where `h` is an increasing and saturating function `N → (0,1)`)
    *   **Verifiable reward (composite partial credit)**: Blends activity coverage, code quality, and behavior.
        $$r_{\text{complex}} = \lambda_{\alpha} \frac{|A_{\text{exp}} \cap A_{\text{gen}}|}{|A_{\text{exp}} \cup A_{\text{gen}}|} + \lambda_c S_{\text{code}} + \lambda_b \text{sim}(M, M_{\text{ref}})$$
        (with `λ_α + λ_c + λ_b = 1`, `A_exp` = expected activity labels, `A_gen` = generated activity labels).

8.  **Training Curriculum**: A staged approach is used to progressively increase reward density and tighten the optimization target:
    *   **Optional Warm Start (SFT)**: Supervised Fine-Tuning on text-model pairs to stabilize syntax and teach POWL structure.
    *   **Stage A (Judge → GRPO)**: Uses LLM-as-a-Judge to reduce structural invalidity and align coarse semantics.
    *   **Stage B (Footprints → GRPO)**: Uses `r_simple` to consolidate behavioral fidelity and maximize agreement with target behavior.
    *   **Optional Branches**: Self-agreement (`r_self`) for robustness, complexity shaping (`r_±foot`), or composite partial credit (`r_complex`).

9.  **Inference and Selection**: At test time, `K` candidates are sampled, validated, their behavior summarized (footprints), and the best model is selected based on footprints similarity to a reference model (if available) or structural code-quality, activity coverage, and consensus with peers (if no reference).

**Results:**
Experiments on a dataset of 1312 textual process descriptions and the ProMoAI benchmark demonstrate that RL significantly reduces invalid model generations, improves behavioral correctness, and allows control over model complexity. The RL-trained checkpoint approaches the performance of state-of-the-art proprietary models (like GPT-4o) while producing fewer invalid generations, highlighting the value of domain-specific reward design.

**Limitations and Future Work:**
Limitations include reward quality (bias in judge-based rewards, limited scope of verifiable rewards), potential systematic biases from LLM-generated reference models, and sensitivity of training to the balance between universal and verifiable components. Future work involves broadening training data with human-authored models, integrating automatic repair loops, and extending to other notations (BPMN, process trees) and richer process perspectives (resource, data).

```python
import pm4py
from pm4py.objects.powl.obj import StrictPartialOrder, OperatorPOWL, Transition,
    SilentTransition
from pm4py.objects.process_tree.obj import Operator

# Activities
register = Transition(label="register request")
reinitiate = Transition(label="reinitiate request")
examine_casually = Transition(label="examine casually")
examine_thoroughly = Transition(label="examine thoroughly")
check_ticket = Transition(label="check ticket")
decide = Transition(label="decide")
reject = Transition(label="reject request")
pay = Transition(label="pay compensation")

# Examination XOR choice
examine_choice = OperatorPOWL(operator=Operator.XOR, children=[examine_casually,
                                                  examine_thoroughly])

# Examination subprocess
examine_subproc = StrictPartialOrder(nodes=[examine_choice, check_ticket, decide])
examine_subproc.add_edge(examine_choice, decide)
examine_subproc.add_edge(check_ticket, decide)

# Loop: body examination subprocess, redo reinitiate
loop = OperatorPOWL(operator=Operator.LOOP, children=[examine_subproc, reinitiate])

# After loop: XOR between reject or pay
decision_choice = OperatorPOWL(operator=Operator.XOR, children=[reject, pay])

# Root partial order
root = StrictPartialOrder(nodes=[register, loop, decision_choice])
root.add_edge(register, loop)
root.add_edge(loop, decision_choice)

# Saves a visualization of the POWL model
pm4py.save_vis_powl(root, "powl_ru.pdf")

# Converts the POWL model to a Petri net
net, im, fm = pm4py.convert_to_petri_net(root)
pm4py.save_vis_petri_net(net, im, fm, "petri_ru.pdf")
```

```json
{
  "grades": [0.8, 0.5, 1.0, 0.4]
}
```

## 💡 Key Insights
- Reinforcement Learning (RL) effectively specializes Large Language Models (LLMs) for process model generation, significantly outperforming generic pretrained models and SFT.
- The approach combines automatically verifiable rewards (structural checks, behavioral footprints via POWL) with universal judgments from an LLM-as-a-Judge to ensure both syntactic correctness and semantic fidelity.
- A staged training curriculum (Judge-based then Footprints-based) is crucial for progressively increasing reward density and stabilizing model behavior, leading to a drastic reduction in invalid model generations.
- The RL-trained models achieve performance comparable to state-of-the-art proprietary models (e.g., GPT-4o) on benchmarks like ProMoAI, while exhibiting higher reliability and fewer invalid generations.
- The framework allows for explicit control over model complexity (e.g., structural richness) through specific reward shaping mechanisms.

## 📚 References
- Berti et al. Process Science (2025) 2:26, https://doi.org/10.1007/s44311-025-00034-4 *(source)*
- Kourani H, van Zelst SJ (2023) POWL: partially ordered workflow language. In: BPM. Lecture notes in computer science, vol 14159. Springer, pp 92-108 *(cited)*
- Berti A, van Zelst SJ, Schuster D (2023) Pm4py: a process mining library for python. Softw Impacts 17:100556 *(cited)*
- Bai Y, Jones A, Ndousse K et al (2022): training a helpful and harmless assistant with reinforcement learning from human feedback. CoRR abs/2204.05862 *(cited)*
- Shao Z, Wang P, Zhu Q et al (2024) R.X.: Deepseekmath: pushing the limits of mathematical reasoning in open language models. CoRR abs/2402.03300 *(cited)*
- Kourani H, Berti A, Schuster D, van der Aalst WMP (2024a) Evaluating large language models on business process modeling: framework, benchmark, and self-improvement analysis. CoRR abs/2412.00023 *(cited)*

## 🏷️ Classification
The content focuses on using Machine Learning (Reinforcement Learning and LLMs) for process modeling, which is a core application of data science in industrial/process engineering contexts, fitting the 'ML, stats, modélisation hybride, optimisation' sub-category.
