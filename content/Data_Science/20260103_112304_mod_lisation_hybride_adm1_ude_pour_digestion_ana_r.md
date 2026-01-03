---
title: "Modélisation Hybride ADM1/UDE pour Digestion Anaérobie Industrielle - État de l'Art 2018-2024"
date: 2026-01-03
category: Data_Science
confidence: 0.95
tags: ['ADM1', 'Universal Differential Equations', 'UDE', 'Neural ODE', 'Anaerobic Digestion', 'Biogas', 'Methanization', 'Hybrid Modeling', 'Kinetic Modeling', 'Scale-up', 'BMP test', 'CSTR', 'Julia SciML', 'Black Soldier Fly', 'Frass', 'Enzyme kinetics', 'Inhibition modeling', 'Process simulation', 'Digital Twin', 'Industrial Data Science', 'sector:anaerobic-digestion', 'sector:biogas', 'sector:methanization']
source: "Telegram Document (.md)"
type: Article
source_type: Article
hash: 112304
---

## 🎯 Relevance
This content is highly useful for optimizing industrial anaerobic digestion processes, improving biogas production efficiency, and managing complex or novel substrates like insect frass. It provides a roadmap for developing robust digital twins, enhancing predictive capabilities, mitigating operational risks (e.g., inhibition), and ultimately increasing the ROI of methanization plants through better process control and stability.

## 📖 Content
# Modélisation Hybride ADM1/UDE pour Digestion Anaérobie Industrielle
## État de l'Art 2018-2024

---

L'intégration d'enzymes exogènes et de réseaux de neurones dans le modèle ADM1 constitue une frontière de recherche active, mais **les applications spécifiques au frass d'insectes et aux Universal Differential Equations pour la digestion anaérobie restent largement inexplorées**. Cette synthèse révèle trois constats majeurs : (1) le modèle de Contois s'impose comme alternative validée à la cinétique de premier ordre pour substrats complexes [1], (2) les paramètres k_hyd issus de tests BMP sous-estiment systématiquement les valeurs CSTR d'un facteur **10 à 30** [2], et (3) l'écosystème Julia SciML offre la stabilité numérique indispensable pour les systèmes raides ADM1 hybrides [3][4]. Pour le frass BSF, la littérature fournit désormais des données BMP exploitables [5], mais aucun fractionnement ADM1 validé n'existe — la chitine devant être classifiée comme inerte (X_I) en conditions mésophiles [6].

---

## 1. Résumé exécutif : stratégies optimales par axe

### Modélisation enzymatique dans ADM1

La cinétique d'hydrolyse de premier ordre standard (dX/dt = -k_hyd·X) montre ses limites pour les substrats prétraités enzymatiquement [7]. **Le modèle de Contois** émerge comme l'alternative la plus validée, capturant la relation sigmoïde biomasse-substrat observée expérimentalement [1][8]. Pour les particules solides, la **cinétique de surface d'Esposito** (k_hyd = k_dis* × A_sp) relie directement la constante d'hydrolyse à la surface spécifique disponible, pertinent pour les prétraitements mécaniques [9]. Les cocktails enzymatiques sur lignocellulose augmentent k_hyd de **2 à 5 fois**, avec des valeurs atteignant **0.4-1.5 j⁻¹** contre 0.1-0.3 j⁻¹ sans prétraitement [10][11].

### Paramètres cinétiques des substrats atypiques

Le frass de Black Soldier Fly présente un potentiel méthanogène de **201-287 mL CH₄/gVS** selon le substrat d'alimentation larvaire, avec des constantes k_hyd de premier ordre entre **0.13 et 0.38 j⁻¹** [5]. La problématique majeure réside dans la teneur protéique élevée (20-30% TS) générant un risque d'inhibition ammoniacale [5][12]. **La chitine doit être classifiée X_I** (inerte) car sa dégradation est négligeable en conditions anaérobies mésophiles [6][13]. Pour la pulpe de betterave, les polysaccharides dominent (f_ch ≈ 0.75-0.85), avec des BMP atteignant **898 mL biogaz/gVS** après prétraitement combiné [10].

### Architectures hybrides Neural ODE/UDE

Les Universal Differential Equations [3] représentent l'approche la plus prometteuse pour ADM1 hybride, permettant de remplacer des termes cinétiques inconnus par des réseaux de neurones tout en conservant la structure mécanistique. **Julia SciML surpasse Python** pour les systèmes raides : stabilité des gradients avec le solveur KenCarp4, méthode adjointe discrète avec checkpointing [4][14]. L'entraînement requiert impérativement une optimisation multi-start (>1000 départs) et une régularisation L2 (λ ∈ [0.1, 10]) [4].

### Scale-up BMP vers CSTR industriel

Le transfert direct des paramètres BMP vers un modèle CSTR constitue une erreur méthodologique majeure. **Les k_hyd batch sont typiquement 10 à 30 fois inférieurs aux valeurs CSTR** [2]. Le protocole de scale-up exige des tests RTD (traceurs lithium ou rhodamine) pour quantifier les volumes morts (3-50% selon la géométrie) et calibrer un modèle tanks-in-series équivalent [15][16]. Seule la fraction dégradable f(d) se transfère directement du batch au continu [17].

---

## 2. Tableaux de paramètres numériques

### Fractionnement ADM1 et cinétiques pour substrats prioritaires

| Substrat | f_ch | f_pr | f_li | f_I | k_hyd (j⁻¹) | BMP (mL CH₄/gVS) | C/N | Réf. |
|----------|------|------|------|-----|-------------|------------------|-----|------|
| **BSF Frass (céréales)** | 0.42 | 0.23 | 0.03 | 0.20 | 0.25 ± 0.02 | 277 ± 1 | 8-15 | [5] |
| **BSF Frass (ensilage maïs)** | 0.35 | 0.23 | 0.03 | 0.10 | 0.22 ± 0.00 | 262 ± 17 | 10-20 | [5] |
| **BSF Frass (drêches)** | 0.31 | 0.22 | 0.04 | 0.49 | 0.13 ± 0.01 | 259 ± 27 | 15-27 | [5] |
| **Pulpe betterave (non traitée)** | 0.80 | 0.09 | 0.02 | 0.09 | 0.15-0.25 | 400-450 | 35-50 | [10] |
| **Pulpe betterave (enzymatique)** | 0.80 | 0.09 | 0.02 | 0.09 | 0.40-0.80 | 500-550 | 35-50 | [10] |
| **Poussières céréales*** | 0.75 | 0.12 | 0.03 | 0.10 | 0.30-0.50 | 300-400 | 20-40 | Est. |
| Ensilage maïs | 0.72 | 0.09 | 0.02 | 0.15 | 0.20-0.35 | 300-370 | 30-50 | [18] |
| Fumier bovin | 0.60 | 0.16 | 0.04 | 0.22 | 0.10-0.20 | 110-275 | 15-25 | [19] |

*Estimation basée sur composition analogue aux céréales — données ADM1 spécifiques non disponibles.

### Constantes k_hyd ADM1 par fraction (valeurs de référence)

| Fraction | k_hyd défaut ADM1 (j⁻¹) | Plage calibrée | Conditions | Réf. |
|----------|-------------------------|----------------|------------|------|
| Carbohydrates (k_hyd_ch) | 10 | 0.5-10 | Amidon rapide, cellulose lente | [20] |
| Protéines (k_hyd_pr) | 10 | 0.25-10 | Variable selon accessibilité | [20] |
| Lipides (k_hyd_li) | 10 | 0.1-10 | Souvent limitant (LCFA) | [20] |
| Désintégration (k_dis) | 0.5 | 0.1-1.0 | Substrats particulaires | [20] |

### Ratios de correction scale-up BMP → CSTR

| Substrat | k_hyd Batch (j⁻¹) | k_hyd CSTR (j⁻¹) | Facteur | Réf. |
|----------|-------------------|------------------|---------|------|
| Boues municipales | 0.15-0.25 | >5.0 | **×20-30** | [2] |
| Résidus agricoles | Variable | Variable | ×10-20 | [21] |
| Déchets alimentaires | 0.13-0.20 | 1.5-3.0 | ×10-15 | [17] |

---

## 3. Équations mathématiques pour couplage Enzyme/ADM1

### 3.1 Modèle de Contois pour hydrolyse enzymatique

Cette formulation capture la dépendance biomasse-substrat et la saturation observée à haute concentration [1][8] :

$$\rho_{hyd} = \frac{\mu_{max,hyd} \cdot X_{substrat}}{K_X \cdot X_{biomasse} + X_{substrat}} \cdot X_{biomasse}$$

| Paramètre | Symbole | Valeur typique | Unité |
|-----------|---------|----------------|-------|
| Taux maximal hydrolyse | μ_max,hyd | 0.1-0.5 | j⁻¹ |
| Constante demi-saturation Contois | K_X | 0.1-1.0 | g COD/g COD |

Validé par Ramirez et al. [1] pour boues prétraitées et Greses et al. [8] pour microalgues avec fonctions d'inhibition VFA.

### 3.2 Cinétique de surface (Esposito) pour prétraitements mécaniques

Pour substrats particulaires où la taille affecte l'accessibilité enzymatique [9] :

$$\frac{dX_c}{dt} = -k_{dis}^* \cdot A_{sp} \cdot X_c$$

Surface spécifique pour particules sphériques :

$$A_{sp} = \frac{6}{\rho \cdot d_p}$$

| Paramètre | Symbole | Unité |
|-----------|---------|-------|
| Constante de surface | k_dis* | m/d |
| Diamètre particule | d_p | m |
| Densité | ρ | kg/m³ |

**Relation directe** : k_hyd = k_dis* × A_sp

### 3.3 Inhibition par produits (VFA et ammoniac)

Fonctions d'inhibition à intégrer pour substrats riches en azote (frass) [12][20] :

$$I_{VFA} = \frac{1}{1 + S_{VFA}/K_{I,VFA}}$$

$$I_{NH3} = \frac{K_{I,N}}{K_{I,N} + [NH_3]}$$

| Paramètre | Symbole | Valeur | Source |
|-----------|---------|--------|--------|
| Inhibition acétate | K_I,VFA | ≈ 9600 mg/L | [20] |
| Inhibition ammoniac | K_I,N | 1.5-3.0 g N-NH₄/L | [12] |

⚠️ **Critique pour frass** : teneur protéique élevée → risque inhibition NH₃

### 3.4 Michaelis-Menten modifié avec désactivation enzymatique

Pour modéliser la perte d'activité enzymatique au cours du temps [11] :

$$\frac{dS}{dt} = \frac{V_{max} \cdot E_0 \cdot S}{K_m + S} \cdot e^{-k_d \cdot t}$$

| Paramètre | Description |
|-----------|-------------|
| E_0 | Concentration enzyme initiale |
| k_d | Constante de désactivation (j⁻¹) |
| V_max | Vitesse maximale de réaction |
| K_m | Constante de Michaelis |

### 3.5 Formulation UDE pour terme cinétique inconnu

Remplacement d'un terme cinétique par réseau de neurones dans ADM1 [3][4] :

$$\frac{dS_{ac}}{dt} = \sum_j \nu_{ac,j} \cdot \rho_j - \rho_{ac}(S_{ac}, X_{ac}, I_{NN})$$

où :

$$I_{NN} = NN(S_{ac}, S_{H2}, pH, [NH_3]; \theta)$$

Le réseau de neurones apprend la fonction d'inhibition combinée à partir des données.

**Architecture recommandée** [4][14] :
- MLP 2-3 couches cachées
- 10-50 neurones par couche
- Activation : tanh (garantit différentiabilité)
- Régularisation L2 : λ ∈ [0.1, 10]

### 3.6 Correction hydraulique tanks-in-series

Pour scale-up avec prise en compte des non-idéalités [15][16] :

$$HRT_{eff} = HRT_{nom} \times (1 - f_d)$$

$$k_{hyd,app} = k_{hyd,idéal} \times \frac{V_{actif}}{V_{total}} \times \eta_{mélange}$$

| Paramètre | Description | Plage typique |
|-----------|-------------|---------------|
| f_d | Fraction volume mort | 3-50% |
| N | Nombre équivalent CSTR (RTD) | 1-10 |
| η_mélange | Efficacité de mélange | 0.5-0.95 |

---

## 4. Recommandations techniques pour implémentation

### 4.1 Architecture hybride ADM1/UDE optimale

L'implémentation recommandée utilise Julia SciML avec le solveur KenCarp4 pour la stabilité sur systèmes raides [3][4]. La structure conserve les équations mécanistiques ADM1 pour les processus bien caractérisés (acidogénèse, méthanogénèse) tout en substituant les termes cinétiques incertains par des réseaux de neurones — typiquement l'hydrolyse de substrats complexes ou les fonctions d'inhibition combinées.

```
┌─────────────────────────────────────────────────────────────┐
│                    ADM1 HYBRIDE / UDE                       │
├─────────────────────────────────────────────────────────────┤
│  MÉCANISTIQUE (conservé)    │    NEURAL (substitué)        │
│  ─────────────────────────  │    ────────────────────      │
│  • Acidogénèse              │    • k_hyd substrats         │
│  • Acétogénèse              │      complexes               │
│  • Méthanogénèse            │    • Fonctions inhibition    │
│  • Bilans de masse          │      combinées               │
│  • Équilibres acide-base    │    • Cinétiques enzymatiques │
└─────────────────────────────────────────────────────────────┘
```

**Protocole d'entraînement** [4] :

1.  **Multi-start** : minimum 1000 initialisations aléatoires (paysage non-convexe)
2.  **Séquence optimisation** : Adam (lr=0.001, 1000 epochs) → BFGS (convergence fine)
3.  **Régularisation L2** : λ ∈ [0.1, 10] pour équilibre mécanistique/neural
4.  **Solveur** : KenCarp4 (systèmes raides) + méthode adjointe discrète

### 4.2 Protocole de calibration industrielle

Séquence de scale-up validée [2][17][21] :

```
┌──────────────────────────────────────────────────────────────┐
│  ÉTAPE 1: BMP Labo (VDI 4630)                                │
│  ─────────────────────────────                               │
│  • Déterminer f(d) fraction dégradable                       │
│  • Obtenir k_hyd,batch initial                               │
│  • Durée : 30-60 jours                                       │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  ÉTAPE 2: CSTR Pilote (5-10 L)                               │
│  ─────────────────────────────                               │
│  • Ajuster k_hyd : facteur ×10-30                            │
│  • Valider cinétiques sous alimentation continue             │
│  • Durée : 3-6 HRT                                           │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  ÉTAPE 3: Tests RTD Industriel                               │
│  ─────────────────────────────                               │
│  • Traceur : LiCl 2-5 mg/kg TS                               │
│  • Quantifier volumes morts (3-50%)                          │
│  • Calibrer modèle tanks-in-series                           │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  ÉTAPE 4: Calibration ADM1                                   │
│  ─────────────────────────────                               │
│  • Priorité : k_dis, k_hyd fractions dominantes              │
│  • Données réelles : CH4, VFA, pH, NH4                       │
│  • Méthode : estimation paramétrique bayésienne              │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  ÉTAPE 5: Validation Opérationnelle                          │
│  ─────────────────────────────────                           │
│  • Minimum 3 HRT en conditions normales                      │
│  • Tests perturbation (surcharge, changement ration)         │
│  • Critère : RMSE < 10% sur production CH4                   │
└──────────────────────────────────────────────────────────────┘
```

---

## 5. Lacunes critiques et perspectives de recherche

La synthèse de la littérature 2018-2024 révèle des **gaps majeurs** pour l'application industrielle visée :

| Gap identifié | Impact | Priorité |
|---------------|--------|----------|
| Aucun fractionnement ADM1 validé pour frass insectes | Estimations incertaines | **Haute** |
| Effet inhibiteur chitine non quantifié (chitosan : 80 mg/g [22]) | Risque sous-estimation X_I | Moyenne |
| Aucune application UDE publiée ciblant ADM1 | Transfert non validé | **Haute** |
| Poussières céréales absentes de la littérature | Pas de données | Moyenne |
| Facteurs k_hyd(batch)/k_hyd(CSTR) très variables (×10-30) | Incertitude scale-up | **Haute** |

**Recommandations pour les travaux futurs** :
1.  Caractérisation ADM1 expérimentale du frass BSF (fractionnement + cinétiques)
2.  Validation UDE sur système AD simplifié avant application ADM1 complet
3.  Établissement de corrélations substrat-spécifiques pour facteurs scale-up

---

## 6. Bibliographie

### A. Références citées dans le texte

| # | Auteur(s) | Année | Titre | Journal | DOI/URL |
|---|-----------|-------|-------|---------|---------|
| [1] | Ramirez I. et al. | 2009 | Modified ADM1 disintegration/hydrolysis structures for modeling batch thermophilic anaerobic digestion of thermally pretreated waste activated sludge | *Water Research* 43(14):3479-92 | [PubMed](https://pubmed.ncbi.nlm.nih.gov/19539974/) |
| [2] | Batstone D.J. et al. | 2009 | Estimation of hydrolysis parameters in full-scale anaerobic digesters | *Biotechnol. Bioeng.* 102(5):1513-20 | [PubMed](https://pubmed.ncbi.nlm.nih.gov/18988267/) |
| [3] | Rackauckas C. et al. | 2020 | Universal Differential Equations for Scientific Machine Learning | *arXiv* 2001.04385 | [arXiv](https://arxiv.org/abs/2001.04385) |
| [4] | Philipps F.L. et al. | 2025 | Current state and open problems in universal differential equations for systems biology | *npj Systems Biology and Applications* 11:24 | [Nature](https://www.nature.com/articles/s41540-025-00550-w) |
| [5] | Wedwitschka H. et al. | 2023 | Biogas Production from Residues of Industrial Insect Protein Production from Black Soldier Fly Larvae *Hermetia illucens* (L.): An Evaluation of Different Insect Frass Samples | *Processes* 11(2):362 | [MDPI](https://www.mdpi.com/2227-9717/11/2/362) |
| [6] | Beier S. & Ungerer S. | 2013 | Bacterial chitin degradation—mechanisms and ecophysiological strategies | *Frontiers in Microbiology* 4:149 | [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3682446/) |
| [7] | Vavilin V.A. et al. | 2008 | Hydrolysis kinetics in anaerobic degradation of particulate organic material: An overview | *Waste Management* 28(6):939-51 | [PubMed](https://pubmed.ncbi.nlm.nih.gov/17544638/) |
| [8] | Greses S. et al. | 2024 | Modelling anaerobic digestion of microalgae: Application of ADM1 with Contois kinetics and inhibition functions | *Bioresource Technology* | — |
| [9] | Esposito G. et al. | 2011 | Bio-methane potential tests to measure the biogas production from the digestion and co-digestion of complex organic substrates | *The Open Environmental Engineering Journal* 4:1-8 | — |
| [10] | Zieminski K. et al. | 2017 | Effect of Different Sugar Beet Pulp Pretreatments on Biogas Production Efficiency | *Applied Biochemistry and Biotechnology* 181:1211-1227 | [Springer](https://link.springer.com/article/10.1007/s12010-016-2279-1) |
| [11] | Parawira W. et al. | 2005 | Profile of hydrolases and biogas production during two-stage mesophilic anaerobic digestion of solid potato waste | *Process Biochemistry* 40(9):2945-2952 | — |
| [12] | Chen Y. et al. | 2008 | Inhibition of anaerobic digestion process: A review | *Bioresource Technology* 99(10):4044-4064 | — |
| [13] | Gooday G.W. | 1990 | The ecology of chitin degradation | *Advances in Microbial Ecology* 11:387-430 | — |
| [14] | Kim S. et al. | 2021 | Stiff Neural Ordinary Differential Equations | *Chaos* 31:093122 | — |
| [15] | Levenspiel O. | 1999 | *Chemical Reaction Engineering* (3rd ed.) | Wiley | ISBN: 978-0471254249 |
| [16] | Wastewater Management | 2024 | Mixing Efficiency Testing in Anaerobic Digesters | — | [Web](https://www.wastewatermanagement.co.uk/mixing-efficiency-testing.htm) |
| [17] | Koch K. et al. | 2020 | Power and Limitations of Biochemical Methane Potential (BMP) Tests | *Frontiers in Energy Research* 8:63 | [Frontiers](https://www.frontiersin.org/articles/10.3389/fenrg.2020.00063/full) |
| [18] | Lübken M. et al. | 2007 | Modelling the energy balance of an anaerobic digester fed with cattle manure and renewable energy crops | *Water Research* 41(18):4085-4096 | — |
| [19] | Biernacki P. et al. | 2013 | Application of Anaerobic Digestion Model No. 1 for describing anaerobic digestion of grass, maize, green weed silage, and industrial glycerine | *Bioresource Technology* 127:188-194 | — |
| [20] | Batstone D.J. et al. | 2002 | Anaerobic Digestion Model No. 1 (ADM1) | *IWA Scientific and Technical Report No. 13* | ISBN: 1900222787 |
| [21] | Weinrich S. & Nelles M. | 2021 | Systematic simplification of the Anaerobic Digestion Model No. 1 (ADM1) | *Bioresource Technology* 327:124779 | — |
| [22] | Li Y. et al. | 2024 | Dynamic responses of the inter-microbial synergism and thermodynamic conditions attribute to the inhibition-and-relief effects of chitosan towards anaerobic digestion | *Water Research* 267:122483 | [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0043135424014684) |

---

### B. Références consultées (non citées directement)

| Auteur(s) | Année | Titre | Journal/Source | Pertinence pour le projet |
|-----------|-------|-------|----------------|---------------------------|
| Yang J. et al. | 2023 | Modifications to Anaerobic Digestion Model No.1 (ADM1): A comprehensive review | *Water Research* 245:120596 | Revue exhaustive des modifications ADM1 depuis 2002 |
| Chen R.T.Q. et al. | 2018 | Neural Ordinary Differential Equations | *NeurIPS* | Fondements théoriques Neural ODEs |
| Kidawara F. et al. | 2025 | Graph-based deep learning for predictions on changes in microbiomes and biogas production in anaerobic digestion systems | *Water Research* | Approche ML + microbiome pour AD |
| Insect School | 2023 | Bio-Methane Potential of Insect Frass | [Web](https://www.insectschool.com/processing/bio-methane-potential-of-insect-frass/) | Synthèse vulgarisée BMP frass |
| BPC Instruments | 2024 | Biogas measurement systems | [Web](https://bpcinstruments.com/biogas/) | Méthodologie BMP instrumentale |
| Angelidaki I. et al. | 2009 | Defining the biomethane potential (BMP) of solid organic wastes and energy crops | *Water Science & Technology* 59(5):927-934 | Protocole BMP standardisé |
| Holliger C. et al. | 2016 | Towards a standardization of biomethane potential tests | *Water Science & Technology* 74(11):2515-2522 | Normalisation inter-laboratoires BMP |
| Donoso-Bravo A. et al. | 2011 | Model selection, identification and validation in anaerobic digestion: A review | *Water Research* 45(17):5347-5364 | Méthodologie calibration ADM1 |
| Pastor-Poquet V. et al. | 2019 | High-solids anaerobic digestion model for homogenized reactors | *Water Research* 142:501-511 | ADM1 adapté haute teneur MS |
| ScienceDirect Topics | 2024 | Hydrolysis Kinetics - Overview | [Web](https://www.sciencedirect.com/topics/immunology-and-microbiology/hydrolysis-kinetics) | Synthèse cinétiques hydrolyse AD |
| Mu Y. et al. | 2020 | The performance evaluation and kinetics response of advanced anaerobic digestion for sewage sludge under different SRT | *Bioresource Technology* 312:123483 | Cinétiques vs temps de séjour |
| Ma J. et al. | 2017 | Data-driven vs. model-driven approaches for predicting biogas production | *Renewable Energy* 107:324-331 | Comparaison approches ML vs mécanistiques |
| Derbal K. et al. | 2009 | Application of the IWA ADM1 model to simulate anaerobic co-digestion of organic waste with waste activated sludge in mesophilic condition | *Bioresource Technology* 100(4):1539-1543 | Calibration ADM1 co-digestion |
| Fezzani B. & Ben Cheikh R. | 2010 | Two-phase anaerobic co-digestion of olive mill wastes in semi-continuous digesters at mesophilic temperature | *Bioresource Technology* 101(6):1628-1634 | Cinétiques deux-phases |
| Fedorovich V. et al. | 2003 | Extension of Anaerobic Digestion Model No. 1 with processes of sulfate reduction | *Applied Biochemistry and Biotechnology* 109(1-3):33-45 | Extension ADM1 sulfato-réduction |

---

*Document généré le 21/12/2024 — État de l'art 2018-2024*
*Projet : Jumeau Numérique Méthanisation Industrielle — Chemin Du Roi*

## 💡 Key Insights
- Hybrid ADM1/UDE modeling, integrating neural networks for unknown kinetics (e.g., hydrolysis, inhibition), is a promising research frontier for industrial anaerobic digestion.
- The Contois model is a validated alternative to first-order kinetics for complex, enzymatically pretreated substrates, and Esposito's surface kinetics are relevant for mechanical pretreatments.
- Direct transfer of k_hyd parameters from BMP tests to CSTR models is erroneous, requiring a 10-30x correction factor and RTD tests for accurate industrial scale-up.
- Julia SciML, with solvers like KenCarp4 and discrete adjoint methods, offers superior numerical stability for stiff hybrid ADM1 systems compared to Python.
- Significant data gaps exist for specific substrates like Black Soldier Fly (BSF) frass, particularly regarding validated ADM1 fractionation and published UDE applications for ADM1.

## 📚 References
- Ramirez I. et al., Modified ADM1 disintegration/hydrolysis structures for modeling batch thermophilic anaerobic digestion of thermally pretreated waste activated sludge, Water Research 43(14):3479-92, 2009, [PubMed](https://pubmed.ncbi.nlm.nih.gov/19539974/) *(source)*
- Batstone D.J. et al., Estimation of hydrolysis parameters in full-scale anaerobic digesters, Biotechnol. Bioeng. 102(5):1513-20, 2009, [PubMed](https://pubmed.ncbi.nlm.nih.gov/18988267/) *(source)*
- Rackauckas C. et al., Universal Differential Equations for Scientific Machine Learning, arXiv 2001.04385, 2020, [arXiv](https://arxiv.org/abs/2001.04385) *(source)*
- Philipps F.L. et al., Current state and open problems in universal differential equations for systems biology, npj Systems Biology and Applications 11:24, 2025, [Nature](https://www.nature.com/articles/s41540-025-00550-w) *(source)*
- Wedwitschka H. et al., Biogas Production from Residues of Industrial Insect Protein Production from Black Soldier Fly Larvae Hermetia illucens (L.): An Evaluation of Different Insect Frass Samples, Processes 11(2):362, 2023, [MDPI](https://www.mdpi.com/2227-9717/11/2/362) *(source)*
- Beier S. & Ungerer S., Bacterial chitin degradation—mechanisms and ecophysiological strategies, Frontiers in Microbiology 4:149, 2013, [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3682446/) *(source)*
- Vavilin V.A. et al., Hydrolysis kinetics in anaerobic degradation of particulate organic material: An overview, Waste Management 28(6):939-51, 2008, [PubMed](https://pubmed.ncbi.nlm.nih.gov/17544638/) *(source)*
- Greses S. et al., Modelling anaerobic digestion of microalgae: Application of ADM1 with Contois kinetics and inhibition functions, Bioresource Technology, 2024, — *(source)*
- Esposito G. et al., Bio-methane potential tests to measure the biogas production from the digestion and co-digestion of complex organic substrates, The Open Environmental Engineering Journal 4:1-8, 2011, — *(source)*
- Zieminski K. et al., Effect of Different Sugar Beet Pulp Pretreatments on Biogas Production Efficiency, Applied Biochemistry and Biotechnology 181:1211-1227, 2017, [Springer](https://link.springer.com/article/10.1007/s12010-016-2279-1) *(source)*
- Parawira W. et al., Profile of hydrolases and biogas production during two-stage mesophilic anaerobic digestion of solid potato waste, Process Biochemistry 40(9):2945-2952, 2005, — *(source)*
- Chen Y. et al., Inhibition of anaerobic digestion process: A review, Bioresource Technology 99(10):4044-4064, 2008, — *(source)*
- Gooday G.W., The ecology of chitin degradation, Advances in Microbial Ecology 11:387-430, 1990, — *(source)*
- Kim S. et al., Stiff Neural Ordinary Differential Equations, Chaos 31:093122, 2021, — *(source)*
- Levenspiel O., Chemical Reaction Engineering (3rd ed.), Wiley, 1999, ISBN: 978-0471254249 *(source)*
- Wastewater Management, Mixing Efficiency Testing in Anaerobic Digesters, 2024, [Web](https://www.wastewatermanagement.co.uk/mixing-efficiency-testing.htm) *(source)*
- Koch K. et al., Power and Limitations of Biochemical Methane Potential (BMP) Tests, Frontiers in Energy Research 8:63, 2020, [Frontiers](https://www.frontiersin.org/articles/10.3389/fenrg.2020.00063/full) *(source)*
- Lübken M. et al., Modelling the energy balance of an anaerobic digester fed with cattle manure and renewable energy crops, Water Research 41(18):4085-4096, 2007, — *(source)*
- Biernacki P. et al., Application of Anaerobic Digestion Model No. 1 for describing anaerobic digestion of grass, maize, green weed silage, and industrial glycerine, Bioresource Technology 127:188-194, 2013, — *(source)*
- Batstone D.J. et al., Anaerobic Digestion Model No. 1 (ADM1), IWA Scientific and Technical Report No. 13, 2002, ISBN: 1900222787 *(source)*
- Weinrich S. & Nelles M., Systematic simplification of the Anaerobic Digestion Model No. 1 (ADM1), Bioresource Technology 327:124779, 2021, — *(source)*
- Li Y. et al., Dynamic responses of the inter-microbial synergism and thermodynamic conditions attribute to the inhibition-and-relief effects of chitosan towards anaerobic digestion, Water Research 267:122483, 2024, [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0043135424014684) *(source)*
- Yang J. et al., Modifications to Anaerobic Digestion Model No.1 (ADM1): A comprehensive review, Water Research 245:120596, 2023 *(cited)*
- Chen R.T.Q. et al., Neural Ordinary Differential Equations, NeurIPS, 2018 *(cited)*
- Kidawara F. et al., Graph-based deep learning for predictions on changes in microbiomes and biogas production in anaerobic digestion systems, Water Research, 2025 *(cited)*
- Insect School, Bio-Methane Potential of Insect Frass, 2023, [Web](https://www.insectschool.com/processing/bio-methane-potential-of-insect-frass/) *(cited)*
- BPC Instruments, Biogas measurement systems, 2024, [Web](https://bpcinstruments.com/biogas/) *(cited)*
- Angelidaki I. et al., Defining the biomethane potential (BMP) of solid organic wastes and energy crops, Water Science & Technology 59(5):927-934, 2009 *(cited)*
- Holliger C. et al., Towards a standardization of biomethane potential tests, Water Science & Technology 74(11):2515-2522, 2016 *(cited)*
- Donoso-Bravo A. et al., Model selection, identification and validation in anaerobic digestion: A review, Water Research 45(17):5347-5364, 2011 *(cited)*
- Pastor-Poquet V. et al., High-solids anaerobic digestion model for homogenized reactors, Water Research 142:501-511, 2019 *(cited)*
- ScienceDirect Topics, Hydrolysis Kinetics - Overview, 2024, [Web](https://www.sciencedirect.com/topics/immunology-and-microbiology/hydrolysis-kinetics) *(cited)*
- Mu Y. et al., The performance evaluation and kinetics response of advanced anaerobic digestion for sewage sludge under different SRT, Bioresource Technology 312:123483, 2020 *(cited)*
- Ma J. et al., Data-driven vs. model-driven approaches for predicting biogas production, Renewable Energy 107:324-331, 2017 *(cited)*
- Derbal K. et al., Application of the IWA ADM1 model to simulate anaerobic co-digestion of organic waste with waste activated sludge in mesophilic condition, Bioresource Technology 100(4):1539-1543, 2009 *(cited)*
- Fezzani B. & Ben Cheikh R., Two-phase anaerobic co-digestion of olive mill wastes in semi-continuous digesters at mesophilic temperature, Bioresource Technology 101(6):1628-1634, 2010 *(cited)*
- Fedorovich V. et al., Extension of Anaerobic Digestion Model No. 1 with processes of sulfate reduction, Applied Biochemistry and Biotechnology 109(1-3):33-45, 2003 *(cited)*

## 🏷️ Classification
The content focuses on advanced modeling techniques, including hybrid mechanistic-neural models (UDEs), machine learning for kinetics, and optimization for industrial anaerobic digestion processes, aligning with the Data Science category.
