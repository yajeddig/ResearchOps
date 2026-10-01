# 🔬 Rapport de Veille Mensuel — septembre 2026

**Période couverte :** septembre 2026
**Documents internes analysés :** 14
**Publications externes :** 0
**Date de génération :** 2026-10-01

---

## 📋 Synthèse Exécutive

1. **Cadrage méthodologique du ML industriel : deux captures convergentes et structurantes.** La note sur l'analyse rétrospective pose une position explicite — sur des historiques labo de quelques centaines d'observations avec moins de 10 événements de natures différentes, l'apprentissage supervisé est exclu et le livrable doit être descriptif, pas prédictif [I1]. En complément, la note de classification des variables montre que la dichotomie « pilotable / non pilotable » est insuffisante et propose quatre catégories (exogène, consigne-levier, pilotée endogène, sortie) avec un principe directeur : « on agit toujours sur la gauche de la chaîne » [I10]. Ces deux notes forment l'ossature d'une méthode ML industrielle interne.

2. **La prévision de séries temporelles se structure autour de deux paradigmes opposés et complémentaires.** D'un côté, TAM (EDF-Lab / Sorbonne Université) propose une architecture « glass-box » additive, interprétable, capable d'intégrer des lois physiques (ODE/PDE) comme régularisation analytique, avec gestion de la dérive de concept (`AdaptiveTAM`) et quantification d'incertitude (Conformal Prediction, EVT) [I4]. De l'autre, TimesFM 3.0 de Google Research offre un modèle de fondation pré-entraîné, zero-shot, avec support natif du multivarié et des covariables, classé #1 sur fev-bench, TIME Benchmark et GIFT-Eval [I8].

3. **Déploiement local de LLM : la quantification ternaire franchit un seuil pratique.** Bonsai 2 27B tient dans 6,7 Gio à 1,72 bit/poids (≈ 9× moins que le FP16 à ~54 Go) tout en conservant, selon les chiffres annoncés par l'éditeur et non vérifiés indépendamment, un niveau proche du modèle de référence là où les quantifications 2 bits classiques s'effondrent (72,59 vs 86,32 de score moyen) [I6][I7]. Contexte de 262 144 tokens, licence Apache 2.0, fonctionnement entièrement hors ligne [I6].

4. **Le domaine eaux usées est bien doté en ressources ouvertes et traçables.** KinetiRO Sim publie l'intégralité de son arithmétique (ASM3 / IWA STR n°9, Metcalf & Eddy 5e éd.) ainsi que son registre de vérification — douze erreurs identifiées et corrigées, trois items restant à compléter [I11]. En parallèle, la série de 18 cours ouverts IHE Delft / GSGS (90 h de vidéo, 9 manuels en accès libre) [I12] et le simulateur Python open-source PooPyLab [I13] complètent un socle de montée en compétence et de simulation à coût nul.

5. **Aucune publication académique captée ce mois-ci.** La section B est vide : la veille externe formelle est à zéro sur septembre 2026, ce qui constitue en soi une lacune à corriger (voir § Analyse croisée).

---

## 🧠 Base de Connaissances Interne

### Méthodologie d'analyse et de modélisation ML en contexte industriel

**Connaissances mobilisables :**
- Contexte-type documenté : quelques centaines de paramètres × quelques centaines d'observations journalières (1 à 2 ans), mélange de prélèvements composites asservis au débit et de prélèvements ponctuels, latence analytique J+1 à J+3 [I1].
- Tableau de contraintes excluant le prédictif : faible nombre d'événements (<10) ⇒ sur-apprentissage garanti ; événements de natures différentes ⇒ pas de signature commune mais N signatures indépendantes ; latence J+1/J+3 ⇒ alerte temps réel impossible ; ratio p/n défavorable ⇒ réduction de dimension et pré-sélection métier obligatoires ; prélèvements hétérogènes ⇒ structures de variance à segmenter [I1].
- Approche graduée : un **socle** (indicateurs métier F/M, âge des boues, DCO/N/P, MVS, rendements ; profils temporels avant/pendant/après ; analyse bivariée ciblée normal vs dégradé) et une **option haute** MSPC light (PCA sur période normale segmentée, T² de Hotelling et Q/SPE rétroactifs, contribution plots) [I1].
- Principe affiché : la valeur opérationnelle vient du socle métier, pas de la sophistication statistique ; la MSPC documente des signatures multivariées *a posteriori* et ne constitue pas un système d'alerte automatique [I1].
- Classification des variables en quatre catégories avec critère de test opérationnel pour chacune : exogène (« personne sur le site ne peut la changer »), consigne/levier (« un opérateur la tape dans la supervision »), pilotée endogène (« elle bouge toute seule quand la charge ou le débit bougent »), sortie (« elle se calcule avec Y », donc exclue des entrées pour fuite d'information) [I10].
- Chaîne causale explicitée : consigne (humain) → régulation (automate) → grandeur pilotée → procédé ← exogène (débit, charge) → sortie Y [I10].

**Outils & ressources identifiés :** la note [I1] est une méthodologie, non un outil logiciel ; la note [I10] est un référentiel de *feature engineering* destiné à devenir une brique de la méthode ML industrielle interne [I10].

**Applications potentielles :** utiliser [I1] comme trame de cadrage pour toute demande exploitant formulée en « détecter les événements », afin de reformuler vers un diagnostic rétrospectif et des règles d'exploitation actionnables [I1] ; appliquer la grille [I10] en amont de toute sélection de variables pour éviter de traiter une grandeur pilotée comme un levier de what-if et pour éliminer les fuites d'information par les variables de sortie [I10].

### Prévision de séries temporelles et modélisation réduite

**Connaissances mobilisables :**
- TAM résout un problème d'optimisation convexe global strictement dans l'espace primal, combinant GAM classiques et algèbre tensorielle sur PyTorch ; modules `StaticTAM` (ajustement du λ ridge par GCV et descente de coordonnées multi-start), `AdaptiveTAM` (correction de résidus en temps réel par fenêtres glissantes parallèles pour la dérive de concept), `OperaTAM` (agrégation d'experts avec bornes de regret), `BenchmarkTracker`, et un module statistique couvrant cibles non gaussiennes (Poisson, Gamma, binomiale), mélanges EM, copules gaussiennes, Conformal Prediction (ACI) et théorie des valeurs extrêmes [I4]. Modules BETA/EXP : `UniversalPhysicsEffect` (lois physiques embarquées) et `KalmanTAM` (filtre de Kalman étendu) [I4].
- Passage à l'échelle de TAM : Group-Chunking pour volumes illimités, solveur gradient conjugué creux matrix-free, accélération GPU [I4].
- TimesFM 3.0 : modèle de fondation decoder-only (papier ICML 2024, arXiv 2310.10688), checkpoints Hugging Face, multivarié natif, covariables passées seules ou passées-et-futures sans tuning par tâche, disponible en production via BigQuery ML, Google Sheets et Vertex Model Garden ; version open non supportée officiellement par Google [I8].
- SPIN : ROM hyper-réduit en ligne pour EDP non linéaires dépendantes du temps, projection Least-Squares Petrov-Galerkin avec hyper-réduction QDEIM ; concept d'*in-span learning* — les prédictions du ROM, passées dans une SVD incrémentale avec oubli, font tourner et repondèrent la base à l'intérieur du sous-espace pour mieux absorber la correction externe suivante [I5]. Code compagnon d'un article de Hedayat, Balzano et Duraisamy (arXiv:2607.02937) [I5].
- micro-ml : bibliothèque Rust/WASM pour JavaScript, ~56 Ko gzippés, 8 algorithmes ML plus régression et statistiques, couvrant lissage, détection d'anomalies, prévision, clustering et réduction de dimension [I9].

**Outils & ressources identifiés :** TAM (github.com/EDF-Lab/tam) [I4] ; TimesFM (github.com/google-research/timesfm) [I8] ; SPIN (github.com/APHedayat/SPIN) [I5] ; micro-ml (github.com/AdamPerlinski/micro-ml) [I9].

**Applications potentielles :** TAM est le candidat naturel lorsque l'interprétabilité et la contrainte physique sont exigées par l'exploitant, en cohérence avec l'exigence de lisibilité posée dans [I1][I4] ; TimesFM offre un point de comparaison zero-shot rapide pour évaluer le gain réel d'un modèle sur mesure [I8] ; SPIN relève du jumeau numérique et du contrôle prédictif sur systèmes régis par EDP [I5] ; micro-ml permet d'embarquer lissage et détection d'anomalies directement dans un tableau de bord web ou un équipement edge sans dépendance lourde [I9].

### LLM locaux et IA embarquée

**Connaissances mobilisables :**
- Bonsai 2 27B dérive de Qwen3.8-27B dont il conserve l'architecture ; seul le stockage des poids change — trois valeurs possibles (−1, 0, +1) avec facteur d'échelle partagé par groupe de 128, soit 1,72 bit/poids effectif [I6][I7].
- Argument technique central : les méthodes de compression classiques s'effondrent sous 4 bits, conservant l'apparence de compétence sur la culture générale mais perdant la capacité à tenir une chaîne de raisonnement longue ; Bonsai est construit pour éviter cet effondrement [I6][I7].
- Comparatif annoncé par Prism ML sur 14 jeux d'évaluation en mode raisonnement : FP16 16,0 bits / 54 Go / 86,32 (100 %) ; UD-Q4_K_XL 5,2 bits / 17,6 Go / 85,18 (98,7 %) ; IQ2_XXS 2,8 bits / 9,4 Go / 72,59 (84,1 %) ; Bonsai 2 27B 1,72 bit — chiffres explicitement non vérifiés indépendamment dans la capture [I6][I7].
- Capacités fonctionnelles : trace de raisonnement séparée de la réponse finale dans l'API, contexte 262 144 tokens, lecture d'images via fichier `mmproj` optionnel, appel d'outils (agent), licence Apache 2.0 commercialement utilisable, fonctionnement entièrement hors ligne [I6][I7].
- Déploiement : binaires `llama-server` et `llama-cli` compilés avec le backend Metal pour Apple Silicon, format GGUF [I6][I7].

**Outils & ressources identifiés :** dépôt github.com/l0d0v1c/bonsai-apple-silicon [I6][I7]. *Remarque :* [I6] et [I7] pointent vers la même source et le même fichier source — il s'agit d'un doublon dans la base de captures.

**Applications potentielles :** traitement de documentation technique et dépannage assisté sans sortie de données du site, un atout pour les contextes industriels sous contrainte de confidentialité [I7] ; la capacité d'appel d'outils ouvre la voie à des agents locaux interrogeant des bases process [I6].

### Ingénierie des données et accès aux données

**Connaissances mobilisables :**
- Orca Telemetry Core : framework open-source (licence MIT) d'orchestration analytique pour télémétrie robotique et IoT, structuré autour d'un mécanisme de déclenchement par fenêtres temporelles, de dépendances entre analyses (une analyse en déclenche d'autres) et de fenêtres temporelles imbriquées [I2]. Stack Go, SQL avec `sqlc`, Docker, GitHub Actions, GoReleaser, scripts de migration de base [I2].
- ODRÉ (Open Data Réseaux Énergies) : console API v2.1 donnant un accès programmatique à des données ouvertes sur les réseaux d'énergie, portée par RTE, Natran, Storengy, Dunkerque LNG, Elengy, Teréga, AFGNV et Weathernews [I3].

**Outils & ressources identifiés :** github.com/orca-telemetry/core [I2] ; odre.opendatasoft.com/api-console/explore/v2.1/ [I3].

**Applications potentielles :** le modèle de fenêtres temporelles d'Orca correspond directement au besoin de « capturer des régions de temps et y lancer des analyses » [I2], ce qui recoupe la logique de profils avant/pendant/après des événements décrite dans [I1] ; ODRÉ fournit un jeu de données externe pour prototyper des pipelines de prévision énergétique [I3].

### Génie des procédés — traitement des eaux usées

**Connaissances mobilisables :**
- KinetiRO Sim : simulateur et outil de conception de STEU en navigateur, biologie ASM3 (IWA STR n°9), dimensionnement clarificateur / dégrilleur / filtre / anaérobie selon Metcalf & Eddy 5e éd. cité par numéro d'équation sur le bloc qui l'utilise, transport membranaire en solution–diffusion marché élément par élément [I11]. Registre de vérification public : douze équations et douze tableaux reproduisent exactement les références ; douze anomalies trouvées — trois modifiaient de vraies réponses, trois étaient des entrées saisissables ignorées par le calcul, le reste des citations erronées sur valeurs justes [I11]. Bibliothèque de 19 éléments membranaires commerciaux (Hydranautics, LG Chem, Veolia) sans classement ni marque par défaut, l'éditeur ne vendant pas d'équipement [I11]. Compte requis ; comptes bêta licenciés jusqu'au 1er novembre 2026, tous formats d'export, sans plafond de projets ni carte bancaire [I11].
- Série BWWT (GSGS / IHE Delft, soutenue par la Fondation Gates et l'IWA) : 18 cours en accès ouvert, 90 h de cours vidéo, 213 présentations / 4 230 diapositives, 9 manuels en accès libre, chaque cours autonome et téléchargeable [I12]. Couverture incluant caractérisation des eaux usées, élimination N et P, aération et mixage, bulking, boues granulaires aérobies, décantation finale, bioréacteurs à membranes et modélisation des boues activées [I12].
- PooPyLab : logiciel open-source (GPL-3.0) de simulation de traitement biologique, construction de PFD et résultats en régime permanent, installable par `pip3 install poopylab`, Python 92,7 % / C 7,3 % [I13].

**Outils & ressources identifiés :** kinetiro.com [I11] ; studybwwt.online [I12] ; github.com/toogad/PooPyLab_Project [I13].

**Applications potentielles :** KinetiRO pour des contre-calculs auditables d'offres et de dimensionnements, sa traçabilité réduisant le risque « boîte noire » [I11] ; PooPyLab pour générer des trajectoires de simulation en régime permanent exploitables comme référence lors d'un diagnostic rétrospectif [I13] ; les cours 14 (modélisation des boues activées) et 9 (aération et mixage) sont directement alignés avec les indicateurs métier du socle de [I1][I12].

### Durabilité, ACV et analyse technico-économique

**Connaissances mobilisables :** le groupe QSD développe des outils open-source de conception durable quantitative appliqués à l'assainissement et à la récupération de ressources, intégrant ACV (LCA) et analyse technico-économique (TEA) [I14]. Dépôts principaux : QSDsan (Python, 45 étoiles, 30 forks, dernière mise à jour 16 sept. 2026), EXPOsan (Python, 23 étoiles, 19 forks, 15 sept. 2026), QSDsan-env (Binder/Dockerfile), ainsi qu'une application bioénergie NJ (frontend JavaScript, backend Python) [I14]. Langages dominants : Python, MATLAB, Jupyter Notebook, JavaScript, Dockerfile [I14].

**Outils & ressources identifiés :** github.com/QSD-Group (QSDsan, EXPOsan) [I14].

**Applications potentielles :** coupler une simulation procédé à une évaluation ACV/TEA pour arbitrer des scénarios d'exploitation sur critère environnemental et économique, les deux familles d'outils étant en Python [I13][I14].

---

## 🌍 Veille Externe — Frontière Académique

Aucune publication académique n'a été collectée pour septembre 2026 (section B des données : « Aucune nouvelle publication trouvée ce mois-ci »). Cette section est donc vide ; aucune référence [P n] n'existe dans la bibliographie de ce mois.

Deux références d'articles sont toutefois mentionnées *à l'intérieur* de captures internes, sans que les articles eux-mêmes aient été analysés : le papier TimesFM « A decoder-only foundation model for time-series forecasting », ICML 2024, arXiv:2310.10688 [I8], et le papier compagnon de SPIN, « In-span learning: adapting reduced-order models using their own predictions », Hedayat, Balzano & Duraisamy, arXiv:2607.02937 [I5]. Ils constituent des cibles de lecture prioritaires mais ne peuvent pas être commentés ici sur la base des captures disponibles.

---

## 🔗 Analyse Croisée

**Connexions internes fortes.**
- *Cadrage méthodologique ↔ outillage.* La contrainte « ratio p/n défavorable, réduction de dimension et pré-sélection métier obligatoires » de [I1] trouve une réponse directe dans la grille de classification de [I10] : exclure les variables de sortie (fuite d'information) et les grandeurs pilotées est précisément une pré-sélection métier, antérieure à toute PCA. Les deux notes gagneraient à être fusionnées en une méthode unique [I1][I10].
- *Interprétabilité ↔ TAM.* Le principe de [I1] selon lequel la valeur vient du socle métier lisible par l'exploitant est cohérent avec l'architecture glass-box et les composants isolés interprétables de TAM [I4]. Inversement, un modèle de fondation zero-shot comme TimesFM [I8] n'apporte pas cette lisibilité : les deux approches répondent à des besoins distincts et ne sont pas substituables.
- *Fenêtres temporelles ↔ profils d'événements.* Le mécanisme de déclenchement par fenêtres temporelles, dépendances entre analyses et fenêtres imbriquées d'Orca [I2] est structurellement adapté à la production automatisée des profils « avant / pendant / après par événement » préconisés dans [I1].
- *Simulation ↔ données.* KinetiRO [I11], PooPyLab [I13] et les cours BWWT [I12] couvrent le même domaine (boues activées, ASM) avec trois registres complémentaires : outil web traçable, bibliothèque Python ouverte, formation. Associés à QSDsan [I14], ils permettent d'enchaîner conception, simulation et évaluation ACV/TEA.
- *Edge AI.* micro-ml (WASM, ~56 Ko) [I9] et Bonsai 2 27B (6,7 Gio, hors ligne) [I6] relèvent de la même logique d'exécution locale, à deux ordres de grandeur de ressources différents.

**Confirmations.** Deux captures indépendantes dans leur formulation mais issues du même dépôt [I6][I7] convergent sur les chiffres de la quantification ternaire ; cette convergence n'est cependant **pas** une validation indépendante, puisque la source est unique et que les captures précisent elles-mêmes que les scores annoncés par Prism ML ne sont pas vérifiés indépendamment [I6][I7].

**Contradictions / tensions.**
- Tension de posture entre [I1], qui exclut le prédictif en contexte de données labo rares et hétérogènes, et l'enthousiasme affiché des notices de [I8] et [I4] sur la réduction du temps de développement et la précision prédictive. Il ne s'agit pas d'une contradiction factuelle mais d'une différence de régime de données : les captures ne fournissent aucune information sur les performances de TimesFM ou TAM sur des historiques de quelques centaines d'observations avec moins de 10 événements. Ce point reste **non documenté** et ne doit pas être extrapolé.
- KinetiRO publie son registre de vérification en signalant trois items « worth completing and not yet completed » et des livrables `.eaqua` encore en construction [I11] : la transparence est réelle mais l'outil est explicitement incomplet.

**Lacunes de ma veille.**
1. **Zéro publication académique ce mois** : aucune confrontation possible entre les outils captés et la littérature évaluée par les pairs.
2. **Aucune capture sur la détection d'anomalies multivariée appliquée au procédé**, alors que [I1] en pose le besoin (T², Q/SPE, contribution plots) — aucune ressource outillée correspondante n'a été collectée.
3. **Aucune donnée de benchmark indépendante** sur Bonsai 2 27B [I6][I7] ni sur TAM [I4].
4. **Doublon non dédupliqué** [I6]/[I7] dans la base, qui gonfle artificiellement le compte de captures.
5. **ODRÉ [I3] est capté à l'état de page d'accueil** : la capture ne contient aucun détail sur les jeux de données réellement disponibles, leurs schémas ou leurs fréquences. Information manquante.

---

## 💡 Recommandations Actionnables

| Priorité | Action | Justification | Refs |
|---|---|---|---|
| Haute | Fusionner [I1] et [I10] en une note méthodologique unique « cadrage d'un projet ML process » (contraintes d'exclusion du prédictif + grille de classification des variables) | Les deux notes traitent de phases successives du même cadrage ; la pré-sélection métier exigée par [I1] est opérationnalisée par la grille à quatre catégories de [I10] | [I1][I10] |
| Haute | Dédupliquer [I6] et [I7] dans la base de captures | Même source, même fichier, contenu identique — biais de comptage | [I6][I7] |
| Haute | Rétablir un flux de veille académique (aucune publication captée en septembre) | Section B vide : aucune validation externe des outils collectés n'est possible | — |
| Haute | Lire et fiche-r les deux articles cités dans les captures : arXiv:2310.10688 (TimesFM) et arXiv:2607.02937 (in-span learning) | Seules références académiques identifiées ce mois, non encore analysées | [I5][I8] |
| Moyenne | Monter un banc d'essai comparatif TAM vs TimesFM sur un jeu de séries process interne, avec critère d'interprétabilité explicite | Les deux outils relèvent de paradigmes opposés (glass-box contraint par la physique vs fondation zero-shot) et leur domaine de pertinence respectif n'est pas documenté dans les captures | [I4][I8] |
| Moyenne | Évaluer Orca Telemetry Core comme orchestrateur des analyses par fenêtres d'événements | Le triptyque fenêtres temporelles / dépendances / imbrication correspond au besoin de profils avant-pendant-après de [I1] ; MIT, Go, containerisé | [I1][I2] |
| Moyenne | Ouvrir un compte bêta KinetiRO avant l'échéance de licence du 1er novembre 2026 et confronter l'outil à un cas de dimensionnement connu | Accès gratuit à tous les formats d'export limité dans le temps ; traçabilité ASM3 / Metcalf & Eddy auditable équation par équation | [I11] |
| Moyenne | Tester un déploiement local de Bonsai 2 27B sur poste Apple Silicon et produire un benchmark interne | Les scores publiés sont ceux de l'éditeur et ne sont pas vérifiés indépendamment ; la licence Apache 2.0 et le fonctionnement hors ligne justifient l'évaluation | [I6][I7] |
| Moyenne | Suivre les cours BWWT n°14 (modélisation boues activées) et n°9 (aération et mixage) | Alignement direct avec les indicateurs métier du socle de [I1] ; accès ouvert, autonome, téléchargeable | [I1][I12] |
| Basse | Prototyper une chaîne PooPyLab → QSDsan sur un cas de récupération de ressources | Les deux écosystèmes sont en Python et couvrent respectivement la simulation procédé et l'évaluation ACV/TEA | [I13][I14] |
| Basse | Approfondir la capture ODRÉ : inventorier les jeux de données, schémas et fréquences | La capture actuelle se limite à la page d'accueil et ne contient aucune information exploitable sur le contenu des données | [I3] |
| Basse | Évaluer micro-ml pour le lissage et la détection d'anomalies côté tableau de bord web | ~56 Ko gzippés, Rust/WASM, alternative légère aux frameworks ML lourds pour des besoins de trendline et de lissage de capteurs | [I9] |
| Basse | Veiller SPIN comme brique potentielle de jumeau numérique sur systèmes EDP | Applicabilité à nos procédés non établie par la capture ; à instruire avant tout investissement | [I5] |

---

## 📚 Bibliographie

[I1] Méthodologie d'analyse rétrospective d'événements process sur données laboratoire peu volumineuses — `content/Data_Analytics/20260925_b76b8ca0_m_thodologie_d_analyse_r_trospective_d__v_nements_.md`
[I2] Orca Telemetry Core: Analytics Orchestration Framework for AI on Robotics and IoT Data — `content/Data_Engineering/20260917_52972fec_orca_telemetry_core__analytics_orchestration_frame.md`
[I3] API Console for Open Data Energy Networks (ODRÉ) — `content/Data_Engineering/20260922_d7e3e9cf_api_console_for_open_data_energy_networks__odr__.md`
[I4] TAM (Time series Additive Model): A Unified Framework for Interpretable, Physics-Informed, and High-Performance Time Series Forecasting — `content/Data_Science/20260917_bd368f63_tam__time_series_additive_model___a_unified_framew.md`
[I5] SPIN: Spectral Preconditioning via IN-span Learning for Adaptive Reduced-Order Models — `content/Data_Science/20260917_c6e0f9b7_spin__spectral_preconditioning_via_in_span_learnin.md`
[I6] Bonsai 2 27B Ternary LLM Local Deployment and Performance on Apple Silicon with Custom llama.cpp Binaries — `content/Data_Science/20260919_6de0f97b_bonsai_2_27b_ternary_llm_local_deployment_and_perf.md`
[I7] Deployment and Optimization of Ternary-Bonsai-2-27B LLM on Apple Silicon with Custom llama.cpp Binaries — `content/Data_Science/20260919_6de0f97b_deployment_and_optimization_of_ternary_bonsai_2_27.md`
[I8] TimesFM (Time Series Foundation Model) by Google Research for Time-Series Forecasting — `content/Data_Science/20260922_8615300f_timesfm__time_series_foundation_model__by_google_r.md`
[I9] micro-ml: Lightweight Machine Learning & Statistics Library for JavaScript (Rust/WASM) — `content/Data_Science/20260922_9eb7e59a_micro_ml__lightweight_machine_learning___statistic.md`
[I10] Advanced Variable Classification for Industrial Machine Learning Models — `content/Data_Science/20260924_09b611bb_advanced_variable_classification_for_industrial_ma.md`
[I11] KinetiRO Sim — a wastewater plant simulator whose arithmetic is published — `content/Process_Engineering/20260920_71a6a306_kinetiro_sim___a_wastewater_plant_simulator_whose_.md`
[I12] Biological Wastewater Treatment Open-Access Online Course Series by IHE Delft and GSGS — `content/Process_Engineering/20260922_2c79dcae_biological_wastewater_treatment_open_access_online.md`
[I13] PooPyLab: Open Source Biological Wastewater Treatment Simulation Software — `content/Process_Engineering/20260922_41655a02_poopylab__open_source_biological_wastewater_treatm.md`
[I14] Quantitative Sustainable Design (QSD) Group: Tools for Sustainable Sanitation and Resource Recovery Systems — `content/Sustainability/20260922_e617a51f_quantitative_sustainable_design__qsd__group__tools.md`