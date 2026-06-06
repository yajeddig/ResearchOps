---
title: "Ce que scipy ne vous dit pas sur l’ajustement de GEV non stationnaire à grande échelle"
date: 2026-06-06
category: Data_Science
confidence: 0.98
tags: ['GEV', 'Extreme Value Theory', 'Non-stationary modeling', 'Optimization', 'Numerical stability', 'Maximum Likelihood Estimation', 'Climate modeling', 'Environmental data science', 'Python', 'Scipy', 'Statistical modeling', 'Big data', 'Data pipeline', 'Warm-starting', 'Solver cascade']
source: "https://ncsdecoopman.github.io/articles/extremeprecipit_gev_optimization.html"
type: Article
source_type: Article
hash: 073206
---

## 🎯 Relevance
This content is highly useful for industrial data scientists and process engineers working with large-scale environmental or climate data. It provides a robust methodology to overcome numerical challenges in complex statistical modeling (GEV non-stationary fitting), leading to reliable and physically consistent results. The ROI comes from achieving 100% convergence, significantly reducing processing time, and ensuring data quality for critical applications like climate risk assessment. It offers a learning opportunity in advanced optimization strategies, pipeline design for robustness, and handling non-convex problems in real-world industrial data science.

## 📖 Content
L’estimation d’une loi de valeurs extrêmes généralisées (GEV) non stationnaire sur un maillage de milliers de points géographiques (ici, 10 milliards de points de données climatiques) se heurte à une instabilité numérique chronique. Les solveurs d’optimisation non linéaire classiques (ex. BFGS, L-BFGS-B de `scipy.optimize`) échouent fréquemment à converger ou s’arrêtent sur des minima locaux aberrants (écart-type négatif, paramètre de forme instable) lorsque tous les paramètres temporels sont optimisés simultanément à froid.

En production, cela engendre des échecs d’exécution en cascade ou des artefacts incohérents dans les cartes de temps de retour. La solution mise en œuvre dans `ExtremePrecipit` consiste en une stratégie d’initialisation séquentielle et incrémentale par transfert de paramètres : on estime d’abord un modèle stationnaire simplifié (`s_gev`) à l’aide de moments empiriques inversés pour ancrer les variables, avant d’ajuster les modèles intermédiaires à dérive unique, puis le modèle complet à double dérive temporelle (`ns_gev_m3`) initialisé à chaud.

## Introduction

Dans les projets de modélisation du risque climatique et d’ingénierie des données environnementales, caractériser l’évolution des événements extrêmes (comme les précipitations horaires torrentielles) implique d’abandonner l’hypothèse de stationnarité. Le réchauffement climatique induit une dérive des paramètres de distribution dans le temps. C’est ici qu’intervient la théorie des valeurs extrêmes (EVT) et en particulier la loi GEV (Generalized Extreme Value) non stationnaire, où la position $\mu$ et l’échelle $\sigma$ deviennent des fonctions linéaires du temps : $\mu(t) = \mu_0 + \mu_1 t$ et $\sigma(t) = \sigma_0 + \sigma_1 t$.

Cependant, le passage d’une modélisation ponctuelle (sur une station météo unique) à un traitement spatialisé massif (sur les points de grille d’un modèle de climat haute résolution comme CNRM-AROME à 2,5 km de résolution) pose un défi de scalabilité et de robustesse numérique majeur. L’optimisation par maximum de vraisemblance (MLE) sur des modèles GEV non stationnaires est hautement non convexe. Sans garde-fous, les solveurs classiques s’effondrent sous le poids de non-convergences numériques locales, ruinant la fiabilité de l’ensemble de la chaîne de traitement.

## Étapes techniques / Pipeline

Le dépôt `ExtremePrecipit` implémente un pipeline d’ajustement statistique robuste orchestré au sein de `pipeline_stats_to_gev.py`. La chaîne de traitement structure l’optimisation en plusieurs étapes clés pour neutraliser l’instabilité numérique.

## Initialisation par moments empiriques

Pour éviter d’ajuster une GEV “à l’aveugle”, la fonction `init_gev_params_from_moments` calcule des paramètres initiaux théoriques à partir de la moyenne et de l’écart-type de la série brute des maxima annuels de la station, tout en gelant temporairement le paramètre de forme $\xi$ à une valeur réaliste de 0.1 :

```python
# Fichier : src/pipelines/pipeline_stats_to_gev.py
def init_gev_params_from_moments(mean_emp: float, std_emp: float, xi: float) -> Tuple[float, float]:
    """
    mean_emp = moyenne empirique
    std_emp = écart-type empirique
    xi = paramètre de forme (fixé à 0.1)
    Returns: (mu, sigma) - paramètres initiaux GEV estimés
    """
    gamma1 = gamma(1 - xi)                                  # g1 = Gamma(1 - xi)
    gamma2 = gamma(1 - 2*xi)                                # g2 = Gamma(1 - 2*xi)
    sigma = std_emp * xi / np.sqrt(gamma2 - gamma1**2)      # sigma = STD * xi / sqrt(g2 - g1^2)
    mu = mean_emp - sigma / xi * (gamma1 - 1)               # mu = E(X) - (sigma / xi) * (g1 - 1)
    return mu, sigma
```

## Ajustement contraint du modèle stationnaire

Le modèle stationnaire `s_gev` est optimisé en fixant la dérive temporelle de position $\mu_1$ à 0 grâce à des bornes d’optimisation strictes. Le solveur cherche uniquement à ajuster le triplet $(\mu_0, \sigma_0, \xi)$ en partant de l’initialisation par moments empiriques calculée à l’étape précédente.

```python
# Fichier : src/pipelines/pipeline_stats_to_gev.py
if model_name == "s_gev":
    # Force mu1 à 0 via les bornes de l'optimiseur
    bounds = [
        (0, 0) if param == "mu1" else PARAM_DEFAULTS[param]["bounds"]
        for param in param_names
    ]
```

## Ajustements intermédiaires mono-covariable

Les modèles non stationnaires intermédiaires `ns_gev_m1` (tendance sur $\mu$) et `ns_gev_m2` (tendance sur $\sigma$) sont ensuite lancés. Leurs paramètres de départ $(\mu_0, \sigma_0, \xi)$ proviennent des estimations stabilisées issues du modèle stationnaire stockées sur disque. Les dérives temporelles $\mu_1$ et $\sigma_1$ sont initialisées à 0.

## Initialisation à chaud du modèle complet

Pour le modèle complet `ns_gev_m3` (qui modélise conjointement $\mu(t)$ et $\sigma(t)$), une initialisation à froid échouerait presque systématiquement. Le pipeline résout ce problème en lisant les résultats de `ns_gev_m1` et `ns_gev_m2` et en sélectionnant la configuration du modèle ayant obtenu la meilleure log-vraisemblance comme socle de départ :

```python
# Fichier : src/pipelines/pipeline_stats_to_gev.py
if model_name in ["ns_gev_m3", "ns_gev_m3_break_year"]:
    if path_m1.exists() and path_m2.exists():
        df_m1 = pd.read_parquet(path_m1).set_index("NUM_POSTE")
        df_m2 = pd.read_parquet(path_m2).set_index("NUM_POSTE")

        for poste in init_params_by_poste:
            row_m1 = df_m1.loc[poste] if poste in df_m1.index else None
            row_m2 = df_m2.loc[poste] if poste in df_m2.index else None

            if row_m1 is not None and row_m2 is not None:
                # Sélection à chaud basée sur la log-vraisemblance maximale
                if row_m1["log_likelihood"] >= row_m2["log_likelihood"]:
                    init_params_by_poste[poste]["mu0"] = row_m1["mu0"]
                    init_params_by_poste[poste]["mu1"] = row_m1["mu1"]
                    init_params_by_poste[poste]["sigma0"] = row_m1["sigma0"]
                    init_params_by_poste[poste]["xi"] = row_m1["xi"]
                    init_params_by_poste[poste]["sigma1"] = 0.0
                else:
                    init_params_by_poste[poste]["mu0"] = row_m2["mu0"]
                    init_params_by_poste[poste]["mu1"] = 0.0
                    init_params_by_poste[poste]["sigma0"] = row_m2["sigma0"]
                    init_params_by_poste[poste]["sigma1"] = row_m2["sigma1"]
                    init_params_by_poste[poste]["xi"] = row_m2["xi"]
```

## Optimisation robuste multi-méthodes en cascade

Si un solveur échoue (ex. `BFGS`), la fonction `gev_non_stationnaire` ne lève pas d’exception. Elle tente une cascade d’algorithmes alternatifs dotés de contraintes physiques (bounds) : `L-BFGS-B`, `TNC`, `SLSQP`, `Powell`, puis `Nelder-Mead`. Seule la meilleure vraisemblance finale est retenue.

## Stratégie d’adoption

Pour répliquer ce pattern dans une équipe d’ingénierie de données ou de science des données :

1.  **Établir des primitives d’inversion analytique** : Avant de laisser un solveur itérer sur une loi de probabilité complexe, implémentez systématiquement l’estimation des moments (comme fait dans `init_gev_params_from_moments`) pour caler le point de départ au plus proche de la réalité physique des données.
2.  **Implémenter la persistance des étapes d’optimisation** : Structurez vos pipelines d’entraînement de façon à sauvegarder les paramètres intermédiaires dans un format portable et rapide (ex. Parquet).
3.  **Mettre en place la cascade de solveurs** : Écrivez une fonction d’ajustement générique capable de catcher les échecs de convergence et de basculer de manière transparente vers d’autres solveurs avec des contraintes physiques larges.

## Frictions et limites d’adoption

*   **Dette d’outillage** : La plupart des scientifiques utilisent les wrappers par défaut de `scipy.stats` ou de packages R (`extRemes`). Ces librairies n’exposent pas facilement l’initialisation fine des variables internes ou le contrôle fin des étapes. Il est parfois nécessaire de réécrire une couche d’abstraction (comme l’implémentation de la classe `FitNsDistribution` issue de la bibliothèque `hades_stats` exploitée ici).
*   **Temps de calcul de la cascade** : Tenter 5 solveurs différents en cas d’échec augmente drastiquement le temps de calcul sur les points difficiles. Cela requiert une architecture de parallélisation robuste (`ProcessPoolExecutor` ou Dask) et un filtrage en amont des séries temporelles trop creuses (via `cleaning_data_observed`).

## Conclusion

## Gains concrets

*   **Taux de convergence de 100%** : Élimination complète des échecs d’optimisation sur les points de grille atypiques (ex. zones montagneuses ou côtières à forte variabilité).
*   **Temps de traitement optimisé** : L’initialisation à chaud réduit le nombre d’itérations nécessaires aux solveurs d’un facteur 3 à 5 par rapport à une recherche “à froid”.
*   **Qualité des résultats** : L’optimisation ne converge plus vers des minima locaux aberrants et non physiques, garantissant des métriques spatialement cohérentes d’un point de grille à l’autre.

## Trade-offs

*   **Complexité du pipeline** : L’orchestration nécessite le maintien de plusieurs lancements successifs et dépendances de fichiers (l’ajustement de `ns_gev_m3` nécessite la présence physique préalable des fichiers parquets de `ns_gev_m1` et `ns_gev_m2`).
*   **Debugging** : Diagnostiquer quel solveur de la cascade a finalement réussi et pourquoi demande une journalisation fine, ce qui peut polluer les sorties de logs en cas d’exécution parallèle massive.

## Références code

*   `src/pipelines/pipeline_stats_to_gev.py`

 Orchestrateur principal réalisant l’ajustement GEV par point de grille avec la cascade de solveurs et la logique d’initialisation séquentielle.
*   `src/utils/data_utils.py`

 Fournit les fonctions de nettoyage, de chargement optimisé via Polars et de filtrage des séries temporelles insuffisantes pour garantir la viabilité de l’ajustement.

* * *

Une présentation plus large du projet est disponible dans la section [projets](https://ncsdecoopman.github.io/reports/extremeprecipit.html).

## 💡 Key Insights
- Fitting non-stationary GEV models at scale (thousands of geographical points, billions of data points) suffers from chronic numerical instability with standard non-linear optimizers (e.g., `scipy.optimize` BFGS, L-BFGS-B).
- The `ExtremePrecipit` solution employs a sequential and incremental initialization strategy with parameter transfer, starting from empirical moments for a stationary model, then intermediate single-drift models, and finally a warm-started full non-stationary model.
- Key techniques include: initialization from empirical moments (fixing shape parameter $\xi$), constrained optimization for stationary models, warm-starting the full model based on the best log-likelihood of intermediate models, and a robust multi-method solver cascade (L-BFGS-B, TNC, SLSQP, Powell, Nelder-Mead).
- This approach achieves 100% convergence rates, optimizes processing time (3-5x faster due to warm-starting), and ensures the quality and physical consistency of results by avoiding aberrant local minima.
- Adoption requires implementing analytical inversion primitives, persisting optimization steps, and building a solver cascade, but introduces trade-offs in pipeline complexity and debugging effort.

## 📚 References
- NCS Decoopman, Ce que scipy ne vous dit pas sur l’ajustement de GEV non stationnaire à grande échelle, URL: https://ncsdecoopman.github.io/articles/extremeprecipit_gev_optimization.html *(source)*
- scipy.optimize (BFGS, L-BFGS-B, TNC, SLSQP, Powell, Nelder-Mead) *(cited)*
- scipy.stats *(cited)*
- extRemes (R package) *(cited)*
- ExtremePrecipit (project/repository) *(cited)*
- CNRM-AROME (climate model) *(cited)*
- hades_stats (library, FitNsDistribution class) *(cited)*
- ProcessPoolExecutor *(cited)*
- Dask *(cited)*
- Polars *(cited)*

## 🏷️ Classification
The content focuses on advanced statistical modeling (GEV), optimization algorithms, and strategies to handle numerical instability and scalability issues for large datasets, which are core competencies of Data Science.
