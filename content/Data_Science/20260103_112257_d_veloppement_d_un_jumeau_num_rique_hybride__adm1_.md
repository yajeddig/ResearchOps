---
title: "Développement d'un Jumeau Numérique Hybride (ADM1 + UDE) pour la Méthanisation Industrielle"
date: 2026-01-03
category: Data_Science
confidence: 1.00
tags: ['Anaerobic Digestion', 'ADM1', 'Digital Twin', 'Hybrid Modeling', 'Universal Differential Equations', 'UDE', 'Neural ODEs', 'Bioprocess Modeling', 'Enzymatic Hydrolysis', 'Kinetics', 'Michaelis-Menten', 'Contois', 'Chitin', 'Black Soldier Fly', 'BSF Frass', 'Stiff ODEs', 'Julia', 'SciML', 'Process Simulation', 'Scale-up', 'Reactor Modeling', 'Biogas Production', 'Waste Valorization', 'Process Optimization', 'sector:biogas', 'sector:anaerobic-digestion', 'sector:methanization']
source: "Telegram Document (.md)"
type: Article
source_type: Report
hash: 112257
---

## 🎯 Relevance
This report provides a critical roadmap for developing a robust and predictive digital twin for industrial anaerobic digestion. It offers significant ROI by enabling precise control of complex feedstocks (e.g., insect waste, cereal dust) and enzymatic additives, optimizing biogas production, preventing process upsets (e.g., acidosis, ammonia inhibition), and facilitating efficient scale-up from lab to industrial operations. It also highlights the importance of selecting appropriate computational tools (Julia/SciML) for handling complex, stiff bioprocess models, offering a learning opportunity in advanced data science for process engineers.

## 📖 Content
# **Rapport d'Expertise : Développement d'un Jumeau Numérique Hybride (ADM1 + UDE) pour la Méthanisation Industrielle**

Date : 24 Mai 2024  
Auteur : Expert Senior Génie des Procédés & Data Scientist  
Objet : État de l'art critique et spécifications techniques pour la modélisation hybride d'intrants complexes (Insectes/Poussières) et l'ajout d'enzymes.

## ---

**1. Résumé Exécutif**

Ce rapport établit les fondations scientifiques pour le développement d'un Jumeau Numérique d'une unité de méthanisation industrielle. L'analyse de la littérature (2018-2024) confirme que l'approche standard ADM1 (Anaerobic Digestion Model No. 1) est insuffisante pour prédire les effets non-linéaires de l'ajout d'enzymes exogènes et la dégradation de matrices complexes comme la chitine d'insectes.

**Conclusions Majeures :**

1.  **Modélisation Enzymatique :** Le modèle cinétique de premier ordre ($k_{hyd}$) doit être abandonné pour l'hydrolyse enzymatique au profit d'une structure hybride combinant **Contois** (biomasse endogène) et **Michaelis-Menten saturé** (enzymes exogènes).1  
2.  **Caractérisation Insectes :** L'utilisation du facteur de conversion Azote/Protéine standard (6.25) sur les résidus d'insectes surestime massivement la fraction protéique due à l'azote non-protéique de la Chitine. Un fractionnement spécifique isolant une variable "Chitine" ($X_c$ modifié) est impératif.3  
3.  **Architecture Hybride (SciML) :** Pour gérer la raideur (*stiffness*) des équations ADM1, l'écosystème **Julia (SciML)** surpasse les implémentations Python (Torchdiffeq) en termes de stabilité et de vitesse (facteur x15 à x800) grâce aux solveurs implicites Rosenbrock optimisés.5  
4.  **Scale-up :** Le transfert Labo $\to$ Indus nécessite l'intégration d'un facteur de correction hydraulique ($\eta \approx 0.9$) et la modélisation explicite des zones mortes ($V_d$), qui peuvent représenter 10 à 30% du volume réacteur.7

## ---

**2. AXE 1 : Modélisation de l'Action Enzymatique dans l'ADM1**

L'ajout d'enzymes crée une discontinuité cinétique que l'ADM1 standard (cinétique de premier ordre : $\rho = k_{hyd}X$) ne peut capturer, car il ne sature pas et ne dépend pas de la concentration enzymatique.

### **2.1 Limitations du Premier Ordre et Transition vers Michaelis-Menten**

Les travaux récents sur l'hydrolyse lignocellulosique démontrent que l'équation de vitesse doit intégrer explicitement la concentration d'enzyme adsorbée. Le modèle de **Michaelis-Menten (M-M)** modifié est la référence pour les ajouts exogènes, tandis que le modèle de **Contois** est supérieur pour l'hydrolyse biologique de fond (limitée par la surface disponible).2

### **2.2 Équation Cible pour le Jumeau Numérique**

Nous proposons une cinétique additive dissociant l'action biologique naturelle de l'action enzymatique ajoutée ("boost").

$$\frac{dX_{sub}}{dt} = - (\rho_{endo} + \rho_{exo})$$
Terme Endogène (Biomasse acclimatée) - Modèle de Contois :

$$\rho_{endo} = k_{m,endo} \cdot \frac{X_{sub}/X_{bio}}{K_{SX} + (X_{sub}/X_{bio})} \cdot X_{bio}$$

Justification : Capture l'effet de saturation de surface (colonisation) critique pour les particules solides (exuvies, fibres).9  
Terme Exogène (Enzyme ajoutée) - Modèle Michaelis-Menten avec Inhibition :  
Ce terme sera estimé par le réseau de neurones (UDE), mais structurellement contraint par cette forme physique :

$$\rho_{exo} = k_{cat} \cdot E_{free} \cdot \frac{X_{sub}}{K_M (1 + \frac{S_{prod}}{K_I}) + X_{sub}}$$

*   $E_{free}$ : Concentration d'enzyme active (doit inclure un terme de désactivation thermique $k_{dec, enz}$).  
*   Terme $(1 + S_{prod}/K_I)$ : Modélise l'inhibition par les produits (ex: cellobiose ou acides aminés accumulés) souvent négligée mais critique à forte charge.1

### **2.3 Gestion de la Saturation (Dose-Réponse)**

L'effet "plateau" observé lors des tests de dosage enzymatique est modélisé par l'adsorption de Langmuir. L'enzyme n'agit que si elle est adsorbée.

$$E_{ads} = \frac{E_{max} \cdot K_{ads} \cdot E_{free}}{1 + K_{ads} \cdot E_{free}}$$

Le Jumeau Numérique devra calibrer $E_{max}$ (capacité maximale d'adsorption du substrat) pour prédire le point de saturation économique.

## ---

**3. AXE 2 : Paramètres Cinétiques & Fractionnement (Mapping ADM1)**

### **3.1 Le Défi des Insectes (Black Soldier Fly - BSF)**

Les déjections (Frass) et exuvies d'insectes sont riches en **Chitine** ($C_8H_{13}O_5N)_n$). L'erreur classique est d'utiliser le facteur de conversion Azote $\to$ Protéine de 6.25 (basé sur 16% N). Or, la chitine contient ~6.9% d'azote qui n'est *pas* de la protéine fermentescible rapidement.12

**Recommandation de Fractionnement BSF :**

*   Utiliser un facteur $Kp \approx 4.76$ pour les larves/exuvies au lieu de 6.25.3  
*   La Chitine doit être mappée soit dans une variable inerte hydrolysable ($X_{ch,slow}$), soit dans $X_c$ avec un $k_{hyd}$ très faible.

### **3.2 Tableau de Synthèse des Paramètres (Littérature 2018-2024)**

| Substrat | Fractionnement ADM1 (Mapping) | Paramètres Cinétiques (khyd​ @ 35°C) | Spécificités & Risques | Sources |
| :---- | :---- | :---- | :---- | :---- |
| **BSF Frass / Exuvies** | $X_{pr}$: 30-40% (Corriger N) $X_{li}$: 10-15% $X_{ch}$ (Chitine): 5-10% $X_I$ (Inerte): 20-30% | $k_{hyd, pr}$: 0.2 - 0.4 $d^{-1}$ $k_{hyd, chitin}$: < 0.1 $d^{-1}$ (très lent) BMP: 200-280 mL $CH_4$/gVS | Risque inhibition NH3 élevé ($TAN > 4g/L$). La Chitine se comporte comme une fibre très récalcitrante. | 13 |
| **Poussières Céréales** | $X_{ch}$ (Amidon): 60-70% $X_{pr}$: 10-12% $X_I$: < 5% | $k_{hyd, ch}$: 2.0 - 10.0 $d^{-1}$ (Très rapide) Risque d'explosion cinétique (VFA boom) | Substrat "Flash". Nécessite un feeding lissé pour éviter l'acidose. | 14 |
| **Pulpe Betterave** | $X_{ch}$ (Pectines): ~75% $X_{li}$: < 1% | $k_{hyd}$: 0.5 - 0.8 $d^{-1}$ | Haute digestibilité. Attention au pH drop rapide (acidogenèse intense). | [15] |
| **Fumier Bovin (Ref)** | $X_c$: 40% $X_I$: 40% | $k_{hyd}$: 0.1 - 0.2 $d^{-1}$ | Sert de tampon et d'inoculum. | 16 |

## ---

**4. AXE 3 : Architectures Hybrides (Neural ODEs / UDE)**

L'approche purement "Data-Driven" échoue sur les bioprocédés par manque de données massives. L'approche **Universal Differential Equations (UDE)** est validée comme la solution optimale : on garde la structure ADM1 (conservation de masse, thermodynamique) et on remplace uniquement les termes incertains (cinétique enzymatique) par un Réseau de Neurones (NN).

### **4.1 Architecture Recommandée : Physics-Informed UDE**

$$\frac{d\mathbf{u}}{dt} = \mathbf{f}_{ADM1}(\mathbf{u}) + \mathbf{M} \cdot \text{softplus}(NN(\mathbf{u}_{in}, \theta))$$

*   **$\mathbf{f}_{ADM1}$** : Le modèle mécaniste standard (bilans de masse, équilibres pH).  
*   **$NN(\mathbf{u}_{in}, \theta)$** : Réseau de neurones (MLP simple 2-3 couches, ou LSTM si effet mémoire) qui prédit un *taux de réaction* additionnel ou un coefficient correctif variable.  
*   **Softplus** : Fonction d'activation $\ln(1+e^x)$ pour garantir la positivité des taux (contrainte physique).17

### **4.2 Le Problème "Stiff" et le Choix du Solveur**

L'ADM1 est un système **raide** (*stiff*) : les constantes de temps varient de la milliseconde (pH) à la semaine (hydrolyse).

*   **Problème Python (Torchdiffeq) :** Les solveurs explicites (Dopri5) échouent ou sont extrêmement lents. Les méthodes "Adjoint" inverses sont instables sur les systèmes raides chaotiques.19  
*   **Solution Julia (SciML) :** L'écosystème Julia est impératif pour ce projet.  
    *   Solveur : Rodas5 (Rosenbrock method) ou FBDF (Fixed-leading-coefficient Backward Differentiation Formula).  
    *   Gradient : Utiliser InterpolatingAdjoint ou BacksolveAdjoint avec gestion de la raideur ("stiff-aware") 6.  
    *   Benchmark : Julia est rapporté 15x à 800x plus rapide que les implémentations Python/Matlab pour l'ADM1.5

## ---

**5. AXE 4 : Scale-up Labo vers Industriel (Test A/B)**

### **5.1 Fonction de Transfert Cinétique ($k_{hyd}$ Shift)**

Les paramètres obtenus en BMP (Batch) surestiment la cinétique industrielle.

$$k_{hyd}^{Indus} = \eta \cdot k_{hyd}^{Labo}$$

Les études montrent que $\eta$ varie typiquement entre 0.5 et 0.92.7 Ce facteur corrige les effets de diffusion limitante dans les grands volumes (transfert de masse moins efficace qu'en fiole agitée).  
Stratégie : Fixer $\eta$ comme un hyper-paramètre à apprendre par le Jumeau Numérique lors de la phase de calibration sur données site (Test A/B).

### **5.2 Facteurs Hydrauliques (Zones Mortes)**

Le réacteur industriel CSTR n'est jamais parfait. Le modèle doit intégrer une structure Tanks-in-Series (TIS) modifiée avec volume mort.

$$HRT_{eff} = \frac{V_{geo} \cdot (1 - V_d)}{Q_{in}}$$

*   **$V_d$ (Volume mort) :** 10% à 35% du volume total, dû à la sédimentation (sables, résidus d'insectes) et mauvaise agitation.21  
*   **Modèle TIS :** Modéliser chaque CSTR physique comme une série de $N \approx 1.5 - 2$ réacteurs virtuels pour représenter le court-circuit hydraulique partiel.22

## ---

**6. Bibliographie Sélectionnée (Top 5)**

1.  23 Menard, J. (2022). *Universal Differential Equations Applied to Bioprocesses.* (Thèse démontrant la supériorité des UDE pour capturer les dynamiques inconnues en bioproduction).  
2.  6 Allen et al. (2024). *A New ODE-Based Julia Implementation of ADM1 Greatly Outperforms Existing Implementations.* (Preuve cruciale pour le choix technologique de Julia vs Python).  
3.  2 Mairet et al. (2011). *Modelling of microalgae anaerobic digestion: ADM1 extended with Contois kinetics.* (Papier fondateur pour remplacer la cinétique de 1er ordre par Contois sur substrats particulaires).  
4.  7 van der Berg et al. (2024). *Predicting commercial-scale anaerobic digestion using biomethane potential.* (Donne le facteur d'échelle 0.92 pour le transfert Labo/Indus).  
5.  4 Caligiani et al. (2018). *Composition of Black Soldier Fly prepupae: proteins, lipids and chitin.* (Référence clé pour la caractérisation biochimique et la correction du facteur azote).

#### **Sources des citations**

1.  Development of modified HCH-1 kinetic model for long-term enzymatic cellulose hydrolysis and comparison with literature models - SciSpace, consulté le décembre 21, 2025, [https://scispace.com/pdf/development-of-modified-hch-1-kinetic-model-for-long-term-17kj1twos4.pdf](https://scispace.com/pdf/development-of-modified-hch-1-kinetic-model-for-long-term-17kj1twos4.pdf)  
2.  Modeling anaerobic digestion of microalgae using ADM1 - Inria, consulté le décembre 21, 2025, [http://www-sop.inria.fr/members/Francis.Mairet/Mairet11_BT_ADM1algae.pdf](http://www-sop.inria.fr/members/Francis.Mairet/Mairet11_BT_ADM1algae.pdf)  
3.  Effects of dietary chitin on nutrient digestibility, cholesterol metabolism, digestive enzyme activity, and gut microbiome in ra - DTU Research Database, consulté le décembre 21, 2025, [https://orbit.dtu.dk/files/410544073/1-s2.0-S0377840125002421-main.pdf](https://orbit.dtu.dk/files/410544073/1-s2.0-S0377840125002421-main.pdf)  
4.  Composition of black soldier fly prepupae and systematic ... - PubMed, consulté le décembre 21, 2025, [https://pubmed.ncbi.nlm.nih.gov/29433277/](https://pubmed.ncbi.nlm.nih.gov/29433277/)  
5.  A New ODE-Based Julia Implementation of the Anaerobic Digestion Model No. 1 Greatly Outperforms Existing DAE-Based Java and Python Implementations - MDPI, consulté le décembre 21, 2025, [https://www.mdpi.com/2227-9717/11/7/1899](https://www.mdpi.com/2227-9717/11/7/1899)  
6.  ADM1jl: a Julia implementation of the anaerobic digestion model 1 - NRC Publications Archive, consulté le décembre 21, 2025, [https://nrc-publications.canada.ca/eng/view/ft/?id=ad080b8b-4e95-4bc8-9556-4ff1710caa55](https://nrc-publications.canada.ca/eng/view/ft/?id=ad080b8b-4e95-4bc8-9556-4ff1710caa55)  
7.  Predicting commercial-scale anaerobic digestion using biomethane potential, consulté le décembre 21, 2025, [https://ideas.repec.org/a/eee/renene/v235y2024ics0960148124013727.html](https://ideas.repec.org/a/eee/renene/v235y2024ics0960148124013727.html)  
8.  (PDF) Impact of the hydraulic loading rate on the hydrodynamic characteristics of an anaerobic fixed bed reactor treating cattle slaughterhouse wastewater - ResearchGate, consulté le décembre 21, 2025, [https://www.researchgate.net/publication/325936061_Impact_of_the_hydraulic_loading_rate_on_the_hydrodynamic_characteristics_of_an_anaerobic_fixed_bed_reactor_treating_cattle_slaughterhouse_wastewater](https://www.researchgate.net/publication/325936061_Impact_of_the_hydraulic_loading_rate_on_the_hydrodynamic_characteristics_of_an_anaerobic_fixed_bed_reactor_treating_cattle_slaughterhouse_wastewater)  
9.  Modified ADM1 disintegration/hydrolysis structures for modeling batch thermophilic anaerobic digestion of thermally pretreated waste activated sludge | Request PDF - ResearchGate, consulté le décembre 21, 2025, [https://www.researchgate.net/publication/26304765_Modified_ADM1_disintegrationhydrolysis_structures_for_modeling_batch_thermophilic_anaerobic_digestion_of_thermally_pretreated_waste_activated_sludge](https://www.researchgate.net/publication/26304765_Modified_ADM1_disintegrationhydrolysis_structures_for_modeling_batch_thermophilic_anaerobic_digestion_of_thermally_pretreated_waste_activated_sludge)  
10. Hydrolysis kinetics in anaerobic degradation of particulate organic material: an overview - PubMed, consulté le décembre 21, 2025, [https://pubmed.ncbi.nlm.nih.gov/17544638/](https://pubmed.ncbi.nlm.nih.gov/17544638/)  
11. Development and validation of a kinetic model for enzymatic hydrolysis of lignocellulosic biomass | Request PDF - ResearchGate, consulté le décembre 21, 2025, [https://www.researchgate.net/publication/8529759_Development_and_validation_of_a_kinetic_model_for_enzymatic_hydrolysis_of_lignocellulosic_biomass](https://www.researchgate.net/publication/8529759_Development_and_validation_of_a_kinetic_model_for_enzymatic_hydrolysis_of_lignocellulosic_biomass)  
12. (PDF) Chitin Analysis in Insect-Based Feed Ingredients and Mixed Feed: Development of a Cost-Effective and Practical Method - ResearchGate, consulté le décembre 21, 2025, [https://www.researchgate.net/publication/388105314_Chitin_Analysis_in_Insect-Based_Feed_Ingredients_and_Mixed_Feed_Development_of_a_Cost-Effective_and_Practical_Method](https://www.researchgate.net/publication/388105314_Chitin_Analysis_in_Insect-Based_Feed_Ingredients_and_Mixed_Feed_Development_of_a_Cost-Effective_and_Practical_Method)  
13. Biogas Production from Residues of Industrial Insect Protein Production from Black Soldier Fly Larvae Hermetia illucens (L.): An Evaluation of Different Insect Frass Samples - MDPI, consulté le décembre 21, 2025, [https://www.mdpi.com/2227-9717/11/2/362](https://www.mdpi.com/2227-9717/11/2/362)  
14. Explosive property and combustion kinetics of grain dust with different particle sizes - NIH, consulté le décembre 21, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC7057223/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7057223/)  
15. Modelling of food waste digestion using ADM1 integrated with Aspen Plus - ePrints Soton, consulté le décembre 21, 2025, [https://eprints.soton.ac.uk/375082/2/HHN_Thesis_FINAL_Feb_2017_rechecked.pdf](https://eprints.soton.ac.uk/375082/2/HHN_Thesis_FINAL_Feb_2017_rechecked.pdf)  
16. Improving ADM1 model to simulate anaerobic digestion start-up with inhibition phase based on cattle slurry | Request PDF - ResearchGate, consulté le décembre 21, 2025, [https://www.researchgate.net/publication/278049670_Improving_ADM1_model_to_simulate_anaerobic_digestion_start-up_with_inhibition_phase_based_on_cattle_slurry](https://www.researchgate.net/publication/278049670_Improving_ADM1_model_to_simulate_anaerobic_digestion_start-up_with_inhibition_phase_based_on_cattle_slurry)  
17. Current state and open problems in universal differential equations for systems biology, consulté le décembre 21, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC12398592/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12398592/)  
18. Physiology-informed regularisation enables training of universal differential equation systems for biological applications - Research journals - PLOS, consulté le décembre 21, 2025, [https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1012198](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1012198)  
19. MIT Open Access Articles Stiff neural ordinary differential equations, consulté le décembre 21, 2025, [https://dspace.mit.edu/bitstream/handle/1721.1/138719/2103.15341.pdf?sequence=2&isAllowed=y](https://dspace.mit.edu/bitstream/handle/1721.1/138719/2103.15341.pdf?sequence=2&isAllowed=y)  
20. Training stiff neural ordinary differential equations with implicit single-step methods - NIH, consulté le décembre 21, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC11646139/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11646139/)  
21. Experimental and numerical assessment of the hydraulic behavior of a pilot-scale Periodic Anaerobic Baffled Reactor (PABR) | Request PDF - ResearchGate, consulté le décembre 21, 2025, [https://www.researchgate.net/publication/322840772_Experimental_and_numerical_assessment_of_the_hydraulic_behavior_of_a_pilot-scale_Periodic_Anaerobic_Baffled_Reactor_PABR](https://www.researchgate.net/publication/322840772_Experimental_and_numerical_assessment_of_the_hydraulic_behavior_of_an_anaerobic_fixed_bed_reactor_treating_cattle_slaughterhouse_wastewater)  
22. The Tanks-in-Series Model - THE PULSAR Engineering, consulté le décembre 21, 2025, [https://www.thepulsar.be/article/the-tanks-in-series-model/](https://www.thepulsar.be/article/the-tanks-in-series-model/)  
23. Universal Differential Equations Applied to Bioprocesses, consulté le décembre 21, 2025, [https://uwaterloo.ca/computational-mathematics/sites/default/files/uploads/documents/menard_jyler_0.pdf](https://uwaterloo.ca/computational-mathematics/sites/default/files/uploads/documents/menard_jyler_0.pdf)

## 💡 Key Insights
- Hybrid kinetic modeling combining Contois (endogenous biomass) and Michaelis-Menten (exogenous enzymes) is crucial for enzymatic hydrolysis in ADM1.
- Accurate characterization of insect-derived substrates requires specific nitrogen-to-protein conversion factors and explicit modeling of chitin.
- Julia's SciML ecosystem with optimized implicit solvers (e.g., Rodas5) is essential for stable and efficient resolution of stiff ADM1-based Universal Differential Equations (UDEs), significantly outperforming Python implementations.
- Industrial scale-up requires incorporating hydraulic correction factors ($\eta$) and explicitly modeling dead volumes ($V_d$) and imperfect mixing (Tanks-in-Series model).

## 📚 References
- Expert Senior Génie des Procédés & Data Scientist, Rapport d'Expertise : Développement d'un Jumeau Numérique Hybride (ADM1 + UDE) pour la Méthanisation Industrielle, 24 Mai 2024 *(source)*
- Development of modified HCH-1 kinetic model for long-term enzymatic cellulose hydrolysis and comparison with literature models - SciSpace, consulté le décembre 21, 2025, https://scispace.com/pdf/development-of-modified-hch-1-kinetic-model-for-long-term-17kj1twos4.pdf *(cited)*
- Modeling anaerobic digestion of microalgae using ADM1 - Inria, consulté le décembre 21, 2025, http://www-sop.inria.fr/members/Francis.Mairet/Mairet11_BT_ADM1algae.pdf *(cited)*
- Effects of dietary chitin on nutrient digestibility, cholesterol metabolism, digestive enzyme activity, and gut microbiome in ra - DTU Research Database, consulté le décembre 21, 2025, https://orbit.dtu.dk/files/410544073/1-s2.0-S0377840125002421-main.pdf *(cited)*
- Composition of black soldier fly prepupae and systematic ... - PubMed, consulté le décembre 21, 2025, https://pubmed.ncbi.nlm.nih.gov/29433277/ *(cited)*
- A New ODE-Based Julia Implementation of the Anaerobic Digestion Model No. 1 Greatly Outperforms Existing DAE-Based Java and Python Implementations - MDPI, consulté le décembre 21, 2025, https://www.mdpi.com/2227-9717/11/7/1899 *(cited)*
- ADM1jl: a Julia implementation of the anaerobic digestion model 1 - NRC Publications Archive, consulté le décembre 21, 2025, https://nrc-publications.canada.ca/eng/view/ft/?id=ad080b8b-4e95-4bc8-9556-4ff1710caa55 *(cited)*
- Predicting commercial-scale anaerobic digestion using biomethane potential, consulté le décembre 21, 2025, https://ideas.repec.org/a/eee/renene/v235y2024ics0960148124013727.html *(cited)*
- (PDF) Impact of the hydraulic loading rate on the hydrodynamic characteristics of an anaerobic fixed bed reactor treating cattle slaughterhouse wastewater - ResearchGate, consulté le décembre 21, 2025, https://www.researchgate.net/publication/325936061_Impact_of_the_hydraulic_loading_rate_on_the_hydrodynamic_characteristics_of_an_anaerobic_fixed_bed_reactor_treating_cattle_slaughterhouse_wastewater *(cited)*
- Modified ADM1 disintegration/hydrolysis structures for modeling batch thermophilic anaerobic digestion of thermally pretreated waste activated sludge | Request PDF - ResearchGate, consulté le décembre 21, 2025, https://www.researchgate.net/publication/26304765_Modified_ADM1_disintegrationhydrolysis_structures_for_modeling_batch_thermophilic_anaerobic_digestion_of_thermally_pretreated_waste_activated_sludge *(cited)*
- Hydrolysis kinetics in anaerobic degradation of particulate organic material: an overview - PubMed, consulté le décembre 21, 2025, https://pubmed.ncbi.nlm.nih.gov/17544638/ *(cited)*
- Development and validation of a kinetic model for enzymatic hydrolysis of lignocellulosic biomass | Request PDF - ResearchGate, consulté le décembre 21, 2025, https://www.researchgate.net/publication/8529759_Development_and_validation_of_a_kinetic_model_for_enzymatic_hydrolysis_of_lignocellulosic_biomass *(cited)*
- (PDF) Chitin Analysis in Insect-Based Feed Ingredients and Mixed Feed: Development of a Cost-Effective and Practical Method - ResearchGate, consulté le décembre 21, 2025, https://www.researchgate.net/publication/388105314_Chitin_Analysis_in_Insect-Based_Feed_Ingredients_and_Mixed_Feed_Development_of_a_Cost-Effective_and_Practical_Method *(cited)*
- Biogas Production from Residues of Industrial Insect Protein Production from Black Soldier Fly Larvae Hermetia illucens (L.): An Evaluation of Different Insect Frass Samples - MDPI, consulté le décembre 21, 2025, https://www.mdpi.com/2227-9717/11/2/362 *(cited)*
- Explosive property and combustion kinetics of grain dust with different particle sizes - NIH, consulté le décembre 21, 2025, https://pmc.ncbi.nlm.nih.gov/articles/PMC7057223/ *(cited)*
- Modelling of food waste digestion using ADM1 integrated with Aspen Plus - ePrints Soton, consulté le décembre 21, 2025, https://eprints.soton.ac.uk/375082/2/HHN_Thesis_FINAL_Feb_2017_rechecked.pdf *(cited)*
- Improving ADM1 model to simulate anaerobic digestion start-up with inhibition phase based on cattle slurry | Request PDF - ResearchGate, consulté le décembre 21, 2025, https://www.researchgate.net/publication/278049670_Improving_ADM1_model_to_simulate_anaerobic_digestion_start-up_with_inhibition_phase_based_on_cattle_slurry *(cited)*
- Current state and open problems in universal differential equations for systems biology, consulté le décembre 21, 2025, https://pmc.ncbi.nlm.nih.gov/articles/PMC12398592/ *(cited)*
- Physiology-informed regularisation enables training of universal differential equation systems for biological applications - Research journals - PLOS, consulté le décembre 21, 2025, https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1012198 *(cited)*
- MIT Open Access Articles Stiff neural ordinary differential equations, consulté le décembre 21, 2025, https://dspace.mit.edu/bitstream/handle/1721.1/138719/2103.15341.pdf?sequence=2&isAllowed=y *(cited)*
- Training stiff neural ordinary differential equations with implicit single-step methods - NIH, consulté le décembre 21, 2025, https://pmc.ncbi.nlm.nih.gov/articles/PMC11646139/ *(cited)*
- Experimental and numerical assessment of the hydraulic behavior of a pilot-scale Periodic Anaerobic Baffled Reactor (PABR) | Request PDF - ResearchGate, consulté le décembre 21, 2025, https://www.researchgate.net/publication/322840772_Experimental_and_numerical_assessment_of_the_hydraulic_behavior_of_a_pilot-scale_Periodic_Anaerobic_Baffled_Reactor_PABR *(cited)*
- The Tanks-in-Series Model - THE PULSAR Engineering, consulté le décembre 21, 2025, https://www.thepulsar.be/article/the-tanks-in-series-model/ *(cited)*
- Universal Differential Equations Applied to Bioprocesses, consulté le décembre 21, 2025, https://uwaterloo.ca/computational-mathematics/sites/default/files/uploads/documents/menard_jyler_0.pdf *(cited)*

## 🏷️ Classification
The content primarily focuses on the development and architectural choices for a hybrid digital twin using advanced data science techniques (Universal Differential Equations, Neural ODEs, specific solvers for stiff systems) to model a complex industrial bioprocess.
