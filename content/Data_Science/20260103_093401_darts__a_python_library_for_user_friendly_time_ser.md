---
title: "Darts: A Python Library for User-Friendly Time Series Forecasting and Anomaly Detection"
date: 2026-01-03
category: Data_Science
confidence: 1.00
tags: ['python', 'time-series', 'forecasting', 'anomaly-detection', 'machine-learning', 'deep-learning', 'statistical-modeling', 'predictive-analytics', 'data-science-library', 'pytorch-lightning', 'scikit-learn-like-api', 'multivariate-time-series', 'probabilistic-forecasting', 'covariates']
source: "https://github.com/unit8co/darts"
type: Article
source_type: Article
hash: 093401
---

### 🎯 Relevance
This library offers significant ROI by enabling accurate forecasting for predictive maintenance, resource optimization, and demand planning, as well as early anomaly detection to prevent costly downtimes in industrial processes. It provides a valuable learning opportunity for applying advanced machine learning and statistical methods to real-world industrial time series data.

### 📝 Summary
- **Key Message:** Darts is a comprehensive Python library designed to simplify time series forecasting and anomaly detection, offering a unified API for a wide range of models.
- **Data/Statistics Mentioned:** Supports univariate and multivariate time series, probabilistic forecasting (samples, distributions, quantiles), and integration of past, future, and static covariates. It includes classical statistical models (ARIMA, Exponential Smoothing, Prophet) and deep learning models (RNN, N-BEATS, Transformer, TFT, DLinear, NLinear, TiDE, TSMixer, Chronos2), along with wrappers for scikit-learn, CatBoost, LightGBM, and XGBoost.
- **Insights:** The library streamlines the entire time series workflow from data preparation and model training to backtesting and evaluation, making advanced techniques accessible. Its modular design allows for flexible combination of models and robust anomaly detection capabilities.
- **Actionable Takeaways:** Data scientists and engineers can leverage Darts to rapidly develop and deploy predictive models for industrial applications, enhance process monitoring with anomaly detection, and gain deeper insights into time-dependent data using its diverse model suite and user-friendly interface.

### 📄 Extracted Content
Darts is a Python library for user-friendly forecasting and anomaly detection on time series. It contains a variety of models, from classics such as ARIMA to deep neural networks. The forecasting models can all be used in the same way, using `fit()` and `predict()` functions, similar to scikit-learn. The library also makes it easy to backtest models, combine the predictions of several models, and take external data into account. Darts supports both univariate and multivariate time series and models. The ML-based models can be trained on potentially large datasets containing multiple time series, and some of the models offer a rich support for probabilistic forecasting.
Darts also offers extensive anomaly detection capabilities. For instance, it is trivial to apply PyOD models on time series to obtain anomaly scores, or to wrap any of Darts forecasting or filtering models to obtain fully fledged anomaly detection models.

Forecasting Models: A large collection of forecasting models for regression as well as classification tasks; from statistical models (such as ARIMA) to deep learning models (such as N-BEATS).
Anomaly Detection: The `darts.ad` module contains a collection of anomaly scorers, detectors and aggregators.
Multivariate Support: `TimeSeries` can be multivariate.
Multiple Series Training (Global Models): All machine learning based models support being trained on multiple series.
Probabilistic Support: `TimeSeries` objects can represent stochastic time series; used to get confidence intervals.
Conformal Prediction Support: Generate probabilistic forecasts with calibrated quantile intervals.
Past and Future Covariates Support: Many models support past-observed and/or future-known covariate time series.
Static Covariates Support: `TimeSeries` can also contain static data.
Hierarchical Reconciliation: Transformers to perform reconciliation.
Regression Models: Plug-in any scikit-learn compatible model.
Training with Sample Weights: All global models support being trained with sample weights.
Forecast Start Shifting: All global models support training and prediction on a shifted output window.
Explainability: Ability to explain some forecasting models using Shap values.
Data Processing: Tools to easily apply (and revert) common transformations.
Metrics: A variety of metrics for evaluating time series' goodness of fit.
Backtesting: Utilities for simulating historical forecasts.
PyTorch Lightning Support: All deep learning models are implemented using PyTorch Lightning.
Filtering Models: `KalmanFilter`, `GaussianProcessFilter`, and `MovingAverageFilter`.
Datasets: `darts.datasets` submodule contains popular time series datasets.
Compatibility with Multiple Backends: `TimeSeries` objects can be created from and exported to pandas, polars, numpy, pyarrow, xarray.

### 🏷️ Classification Reason
The content describes a Python library focused on machine learning, statistical modeling, and deep learning techniques for time series forecasting and anomaly detection, which are core components of data science.
