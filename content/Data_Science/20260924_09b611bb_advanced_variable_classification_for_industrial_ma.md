---
title: Advanced Variable Classification for Industrial Machine Learning Models
date: '2026-09-24'
category: Data_Science
confidence: 0.95
tags: [Machine Learning, Industrial Data Science, Feature Engineering, Variable Classification,
  Process Control, Automation, Data Modeling, Causal Inference, Setpoint, Endogenous
    Variables, Exogenous Variables]
source: Know How (pouvant devnir une partie de la méthode ML industrielle)  la classification
  en deux catégories (pilotable / non pilotable) ne suffit pas. Sur les 12 choix,
  environ la moitié est à revoir, pa
type: Article
source_type: Other
hash: 09b611bb0c5a
---
## 🎯 Relevance
This classification framework is critical for developing robust, interpretable, and actionable Machine Learning models in industrial settings. It improves feature engineering, prevents common pitfalls in industrial data science, and ensures that model outputs can be directly translated into control strategies or operational adjustments, thereby maximizing ROI and operational efficiency.

## 📖 Content
This note details a critical methodology for classifying variables in industrial processes, specifically for the development of Machine Learning (ML) models. It argues that a simplistic two-category classification (e.g., 'pilotable' / 'non pilotable' - controllable / non-controllable) is insufficient and often misleading. The core issue highlighted is that a measured variable is rarely the one directly acted upon; instead, actions are typically applied to its setpoint (consigne).

The proposed framework introduces four distinct categories for process variables:

| Catégorie (Category) | Définition (Definition)                               | Test (Test Criterion)                                 | Usage dans le modèle (Usage in Model)                                |
| :------------------- | :---------------------------------------------------- | :---------------------------------------------------- | :------------------------------------------------------------------- |
| **Exogène** (Exogenous) | Vient de l'extérieur, personne ne la choisit.         | « Personne sur le site ne peut la changer »           | Entrée normale (à prévoir si on fait de la prévision)                |
| **Consigne (levier)** (Setpoint/Lever) | Valeur choisie par un humain.                         | « Un opérateur la tape dans la supervision »          | Levier du what-if (What-if lever)                                    |
| **Pilotée (endogène)** (Controlled/Endogenous) | Calculée par un automate à partir d'autres grandeurs. | « Elle bouge toute seule quand la charge ou le débit bougent » | Pas un levier. Soit on l'exclut, soit on la recalcule avec la règle de régulation à partir de la consigne. |
| **Sortie** (Output)  | Contient la cible Y ou en dérive.                     | « Elle se calcule avec Y »                            | Exclue des entrées (fuite d'information)                             |

This classification is crucial because it reflects the actual causal chain and control hierarchy within an industrial system. The note illustrates this with a causal diagram:

```mermaid
graph LR
    A[Consigne (humain)] --> B[Régulation (automate)]
    B --> C[Grandeur pilotée]
    C --> D[Procédé]
    E[Exogène (débit, charge)] --> D
    D --> F[Sortie Y]
```

The fundamental principle emphasized is: "On agit toujours sur la gauche de la chaîne." (One always acts on the left side of the chain.) This means that human intervention or optimization strategies should target the 'Consigne' (setpoint) variables. Treating a 'Grandeur pilotée' (controlled variable) as a direct lever in a model is erroneous, as it effectively ignores the existence and function of the automation system. Such a misclassification can lead to models that are not actionable or provide misleading insights.

## 💡 Key Insights
- A two-category classification (controllable/non-controllable) is insufficient for industrial ML variable analysis.
- A four-category classification (Exogenous, Setpoint/Lever, Controlled/Endogenous, Output) is proposed for robust industrial ML modeling.
- Actions in an industrial process are always applied to setpoints (consignes), not directly to variables controlled by automation.
- Misclassifying a 'controlled' variable as a direct lever ignores the underlying automation system and leads to non-actionable models.
- Output variables (target Y) must be excluded from model inputs to prevent information leakage and ensure predictive validity.

## 📚 References


## 🏷️ Classification
The content directly addresses a methodological challenge in applying Machine Learning to industrial processes, focusing on variable classification and its implications for model building and actionability, which falls squarely within the scope of Data Science in an industrial context.
