---
title: "Reliable Feature Importance for Random Forests: Addressing Bias with Permutation and Drop-Column Methods"
date: 2026-01-18
category: Data_Science
confidence: 1.00
tags: ['Random Forest', 'Feature Importance', 'Permutation Importance', 'Drop-column Importance', 'Model Interpretation', 'Machine Learning', 'Scikit-learn', 'R', 'Bias', 'Gini Importance', 'Mean Decrease in Impurity', 'OOB Score', 'Collinearity']
source: "https://explained.ai/rf-importance/"
type: Article
source_type: Article
hash: 082823
---

## 🎯 Relevance
In process engineering and industrial data science, accurate model interpretation is crucial for understanding process drivers, optimizing operations, and making informed decisions. Misleading feature importances can lead to incorrect conclusions about which process parameters are most influential, resulting in suboptimal control strategies, inefficient resource allocation, or failed troubleshooting efforts. This article provides critical knowledge for building reliable and interpretable machine learning models in industrial contexts, directly impacting ROI through better process understanding and optimization.

## 📖 Content
Beware Default Random Forest Importances
===============

Beware Default Random Forest Importances
========================================

_Brought to you by [explained.ai](http://explained.ai/)_

[Terence Parr](https://www.linkedin.com/in/terence-parr/), [Kerem Turgutlu](https://www.linkedin.com/in/kerem-turgutlu-12906b65/), [Christopher Csiszar](https://www.linkedin.com/in/cpcsiszar/), and [Jeremy Howard](http://www.fast.ai/about/#jeremy)

 March 26, 2018.

(Terence is a tech lead at Google and ex-Professor of computer/data science; both he and Jeremy teach in University of San Francisco's [MS in Data Science program](https://www.usfca.edu/arts-sciences/graduate-programs/data-science). You might know Terence as the creator of the [ANTLR parser generator](http://www.antlr.org/). For more material, see Jeremy's [fast.ai courses](http://course.fast.ai/). Kerem and Christopher are current MS Data Science students.)

**Update June 8, 2020**. Terence (with James D. Wilson and Jeff Hamrick) just released [Nonparametric Feature Impact and Importance](https://arxiv.org/abs/2006.04750) that doesn't require a user's fitted model to compute impact. It's based upon a technique that computes [Partial Dependence through Stratification](https://arxiv.org/abs/1907.06698).

**Update July 18, 2019**. scikit-learn just merged an [implementation of permutation importance](https://github.com/scikit-learn/scikit-learn/pull/13146).

**Update October 20, 2018** to show better feature importance plot and a new feature dependence heatmap. Updated all plots and section [Dealing with collinear features](https://explained.ai/rf-importance/#corr_collinear). See new section [Breast cancer data set multi-collinearities](https://explained.ai/rf-importance/#cancer).

**Updated April 19, 2018** to include new rfpimp package features to handle collinear dataframe columns in [Dealing with collinear features](https://explained.ai/rf-importance/#corr_collinear) section.

**Updated April 4, 2018** to include many more experiments in the [Experimental results](https://explained.ai/rf-importance/#experimental) section.

### TL;DR

The scikit-learn Random Forest feature importance and R's default Random Forest feature importance strategies are biased. To get reliable results in Python, use permutation importance, provided here and in our [rfpimp](https://github.com/parrt/random-forest-importances/tree/master/src) package (via pip). For R, use importance=T in the Random Forest constructor then type=1 in R's importance() function. In addition, your feature importance measures will only be reliable if your model is trained with suitable hyper-parameters.

Contents

*   [Introduction to feature importances](https://explained.ai/rf-importance/#intro)
*   [Trouble in paradise](https://explained.ai/rf-importance/#2)
*   [Default feature importance mechanism](https://explained.ai/rf-importance/#3)
*   [Permutation importance](https://explained.ai/rf-importance/#4)
*   [Drop-column importance](https://explained.ai/rf-importance/#5)
*   [Comparing R to scikit-learn importances](https://explained.ai/rf-importance/#6)

    *   [R mean-decrease-in-impurity importance](https://explained.ai/rf-importance/#6.1)
    *   [R permutation importance](https://explained.ai/rf-importance/#6.2)
    *   [R drop-column importance](https://explained.ai/rf-importance/#6.3)

*   [Experimental results](https://explained.ai/rf-importance/#experimental)
    *   [Model-neutral permutation importance](https://explained.ai/rf-importance/#neutral)
    *   [Performance considerations](https://explained.ai/rf-importance/#perf)
    *   [The effect of validation set size on importance](https://explained.ai/rf-importance/#size)
    *   [The effect of collinear features on importance](https://explained.ai/rf-importance/#collinear)

*   [Dealing with collinear features](https://explained.ai/rf-importance/#corr_collinear)
    *   [Breast cancer data set multi-collinearities](https://explained.ai/rf-importance/#cancer)

*   [Summary](https://explained.ai/rf-importance/#7)
*   [Resources and sample code](https://explained.ai/rf-importance/#8)

    *   [Python](https://explained.ai/rf-importance/#8.1)
    *   [R](https://explained.ai/rf-importance/#8.2)
    *   [Sample Kaggle apartment data](https://explained.ai/rf-importance/#8.3)

*   [Epilogue: Explanations and Further Possibilities](https://explained.ai/rf-importance/#9)

[](https://explained.ai/rf-importance/)
### Introduction to Feature Importance

Training a model that accurately predicts outcomes is great, but most of the time you don't just need predictions, you want to be able to _interpret_ your model. For example, if you build a model of house prices, knowing which features are most predictive of price tells us which features people are willing to pay for. Feature importance is the most useful interpretation tool, and data scientists regularly examine model parameters (such as the coefficients of linear models), to identify important features.

Feature importance is available for more than just linear models. Most random Forest (RF) implementations also provide measures of feature importance. In fact, the RF importance technique we'll introduce here (_permutation importance_) is applicable to any model, though few machine learning practitioners seem to realize this. Permutation importance is a common, reasonably efficient, and very reliable technique. It directly measures variable importance by observing the effect on model accuracy of randomly shuffling each predictor variable. This technique is broadly-applicable because it doesn't rely on internal model parameters, such as linear regression coefficients (which are really just poor proxies for feature importance).

We recommend using permutation importance for all models, including linear models, because we can largely avoid any issues with model parameter interpretation. Interpreting regression coefficients requires great care and expertise; landmines include not normalizing input data, properly interpreting coefficients when using Lasso or Ridge regularization, and avoiding highly-correlated variables (such as country and country_name). To learn more about the difficulties of interpreting regression coefficients, see [Statistical Modeling: The Two Cultures](https://projecteuclid.org/euclid.ss/1009213726) (2001) by Leo Breiman (co-creator of Random Forests).

One of Breiman's issues involves the accuracy of models. The more accurate our model, the more we can trust the importance measures and other interpretations. Measuring linear model goodness-of-fit is typically a matter of residual analysis. (A residual is the difference between predicted and expected outcomes). The problem is that residual analysis does not always tell us when the model is biased. Breiman quotes William Cleveland, “_one of the fathers of residual analysis,_” as saying residual analysis is an unreliable goodness-of-fit measure beyond four or five variables.

If a feature importance technique well-known to Random Forest implementers gives direct and reliable results, why have we written an article entitled “Beware Default Random Forest Importances?” [](https://explained.ai/rf-importance/)
### Trouble in paradise
 Have you ever noticed that the feature importances provided by [scikit-learn](http://scikit-learn.org/)'s Random Forests™ seem a bit off, perhaps not jiving with your domain knowledge? We've got some bad news—you can't always trust them. It's time to revisit any business or marketing decisions you've made based upon the default feature importances (e.g., which customer attributes are most predictive of sales). This is not a bug in the implementation, but rather an inappropriate algorithm choice for many data sets, as we discuss below. First, let's take a look at how we stumbled across this problem. 
To prepare educational material on regression and classification with Random Forests (RFs), we pulled data from Kaggle's [Two Sigma Connect: Rental Listing Inquiries](https://www.kaggle.com/c/two-sigma-connect-rental-listing-inquiries) competition and selected a few columns. Here are the first three rows of data in our data frame, df, loaded from data file [rent.csv](https://github.com/parrt/random-forest-importances/blob/master/notebooks/data/rent.csv) (interest_level is the number of inquiries on the website):

| bath | bed | | longi | lati | interest_ |
| --- | --- | --- | --- | --- | --- |
| rooms | rooms | price | tude | tude | level |
| 1.5 | 3 | 3000 | -73.942 | 40.714 | 2 |
| 1.0 | 2 | 5465 | -73.966 | 40.794 | 1 |
| 1.0 | 1 | 2850 | -74.001 | 40.738 | 3 |

We trained a regressor to predict New York City apartment rent prices using four apartment features in the usual scikit way:

```python
features = ['bathrooms', 'bedrooms', 'longitude', 'latitude', 'price']
dfr = df[features]
X_train, y_train = dfr.drop('price',axis=1), dfr['price']
X_train['random'] = np.random.random(size=len(X_train))
rf = RandomForestRegressor(
 n_estimators=100, min_samples_leaf=1, n_jobs=-1, oob_score=True)
rf.fit(X_train, y_train)
```

In order to explain feature selection, we added a column of random numbers. (Any feature less important than a random column is junk and should be tossed out.)

After training, we plotted the rf.feature_importances_ as shown in **Figure 1(a)**. Wow! New Yorkers really care about bathrooms. The number of bathrooms is the strongest predictor of rent price. That's weird but interesting.

![Image 1](https://explained.ai/rf-importance/images/regr_dflt_random_annotated.png)
**Figure 1(a)**. scikit-learn default importances for Random Forest **regressor** predicting apartment rental price from 4 features + a column of random numbers. Random column is last, as we would expect but the importance of the number of bathrooms for predicting price is highly suspicious.

![Image 2](https://explained.ai/rf-importance/images/cls_dflt_random_annotated.png)
**Figure 1(b)**. scikit-learn default importances for Random Forest **classifier** predicting apartment interest level (low, medium, high) using 5 features + a column of random numbers. Highly suspicious that random column is much more important than the number of bedrooms.

As expected, **Figure 1(a)** shows the random column as the least important.

Next, we built an RF classifier that predicts interest_level using the other five features and plotted the importances, again with a random column:

```python
features = ['bathrooms', 'bedrooms', 'price', 'longitude', 'latitude', 'interest_level']
dfc = df[features]
X_train, y_train = dfc.drop('interest_level',axis=1), dfc['interest_level']
X_train['random'] = np.random.random(size=len(X_train))
rf = RandomForestClassifier(
 n_estimators=100, # better generality with 5
 min_samples_leaf=5, n_jobs=-1, oob_score=True)
rf.fit(X_train, y_train)
```

**Figure 1(b)** shows that the RF classifier thinks that the random column is more predictive of the interest level than the number of bedrooms and bathrooms. What the hell? Ok, something is definitely wrong. [](https://explained.ai/rf-importance/)
### Default feature importance mechanism

The most common mechanism to compute feature importances, and the one used in scikit-learn's [RandomForestClassifier](http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html) and [RandomForestRegressor](http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html), is the _mean decrease in impurity_ (or _gini importance_) mechanism (check out the [Stack Overflow conversation](https://stackoverflow.com/questions/15810339/how-are-feature-importances-in-randomforestclassifier-determined)). The mean decrease in impurity importance of a feature is computed by measuring how effective the feature is at reducing uncertainty (classifiers) or variance (regressors) when creating decision trees within RFs. The problem is that this mechanism, while fast, does not always give an accurate picture of importance. Breiman and Cutler, the inventors of RFs, [indicate](https://www.stat.berkeley.edu/~breiman/RandomForests/cc_home.htm#varimp) that this method of “_adding up the gini decreases for each individual variable over all trees in the forest gives a **fast** variable importance that is **often very consistent** with the permutation importance measure._” (Emphasis ours and we'll get to permutation importance shortly.)

We've known for years that this common mechanism for computing feature importance is biased; i.e. it tends to inflate the importance of continuous or high-cardinality categorical variables For example, in 2007 Strobl _et al_ pointed out in [Bias in random forest variable importance measures: Illustrations, sources and a solution](https://link.springer.com/article/10.1186%2F1471-2105-8-25) that “_the variable importance measures of Breiman's original Random Forest method ... are not reliable in situations where potential predictor variables vary in their scale of measurement or their number of categories_.” That's unfortunate because not having to normalize or otherwise futz with predictor variables for Random Forests is very convenient. [](https://explained.ai/rf-importance/)

### Permutation importance

Breiman and Cutler also described _permutation importance_, which measures the importance of a feature as follows. Record a baseline accuracy (classifier) or R $^2$ score (regressor) by passing a validation set or the out-of-bag (OOB) samples through the Random Forest. Permute the column values of a single predictor feature and then pass all test samples back through the Random Forest and recompute the accuracy or R $^2$. The importance of that feature is the difference between the baseline and the drop in overall accuracy or R $^2$ caused by permuting the column. The permutation mechanism is much more computationally expensive than the mean decrease in impurity mechanism, but the results are more reliable. The permutation importance strategy does not require retraining the model after permuting each column; we just have to re-run the perturbed test samples through the already-trained model.

Any machine learning model can use the strategy of permuting columns to compute feature importances. This fact is under-appreciated in academia and industry. Most software packages calculate feature importance using model parameters if possible (e.g., the coefficients in linear regression as discussed above). A single importance function could cover all models. The advantage of Random Forests, of course, is that they provide OOB samples by construction so users don't have to extract their own validation set and pass it to the feature importance function.

As well as being broadly applicable, the implementation of permutation importance is simple—here is a complete working function:

```python
def permutation_importances(rf, X_train, y_train, metric):
 baseline = metric(rf, X_train, y_train)
 imp = []
 for col in X_train.columns:
 save = X_train[col].copy()
 X_train[col] = np.random.permutation(X_train[col])
 m = metric(rf, X_train, y_train)
 X_train[col] = save
 imp.append(baseline - m)
 return np.array(imp)
```

Notice that the function does not normalize the importance values, such as dividing by the standard deviation. According to [Conditional variable importance for random forests](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-9-307), “_the raw [permutation] importance… has better statistical properties_.” Those importance values will not sum up to one and it's important to remember that we don't care what the values are _per se_. What we care about is the relative predictive strengths of the features. (When using the importances() function in R, make sure to use scale=F to to prevent this normalization.)

The key to this “baseline minus drop in performance metric” computation is to use a validation set or the OOB samples, not the training set (for the same reason we measure model generality with a validation set or OOB samples). Our permutation_importances() function expects the metric argument (a function) to use out-of-bag samples when computing accuracy or R $^2$ because there is no validation set argument. (We figured out how to grab the OOB samples from the scikit RF source code.) You can check out our functions that compute the [OOB classifier accuracy](https://github.com/parrt/random-forest-importances/blob/master/src/rfpimp.py#L237) and [OOB regression R $^2$ score](https://github.com/parrt/random-forest-importances/blob/master/src/rfpimp.py#L263) (without altering the RF model state). Here are two code snippets that call the permutation importance function for regressors and classifiers:

```python
rf = RandomForestRegressor(...)
rf.fit(X_train, y_train) # rf must be pre-trained
imp = permutation_importances(rf, X_train, y_train, oob_regression_r2_score)
```

```python
rf = RandomForestClassifier(...)
imp = permutation_importances(rf, X_train, y_train, oob_classifier_accuracy)
```

To test permutation importances, we plotted the regressor and classifier importances, as shown in **Figure 2(a)** and **Figure 2(b)**, using the same models from above. Both models included a random column, which correctly show up as the least important feature. The regressor in **Figure 1(a)** also had the random column last, but it showed the number of bathrooms as the strongest predictor of apartment rent price. The permutation importance in **Figure 2(a)** places bathrooms more reasonably as the least important feature, other than the random column.

![Image 3](https://explained.ai/rf-importance/images/regr_permute_random.svg)
**Figure 2(a)**. Importances derived by permuting each column and computing change in out-of-bag R $^2$ using scikit-learn**regressor**. Predicting apartment rental price from 4 features + a column of random numbers.

![Image 4](https://explained.ai/rf-importance/images/cls_permute_random.svg)
**Figure 2(b)**. Importances derived by permuting each column and computing change in out-of-bag accuracy using scikit-learn Random Forest **classifier**.

The classifier default importances in **Figure 1(b)** are plausible, because price and location matter in real estate market. Unfortunately, the importance of the random column is in the middle of the pack, which makes no sense. **Figure 2(b)** places the permutation importance of the random column last, as it should be. One could also argue that the number of bedrooms is a key indicator of interest in an apartment, but the default mean-decrease-in-impurity gives the bedrooms feature little weight. The permutation importance in **Figure 2(b)**, however, gives a better picture of relative importance.

Permutation importance is pretty efficient and generally works well, but Strobl _et al_ show that “_permutation importance over-estimates the importance of correlated predictor variables._” in [Conditional variable importance for random forests](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-9-307). It's unclear just how big the bias towards correlated predictor variables is, but there's a way to check. [](https://explained.ai/rf-importance/)

### Drop-column importance

Permutation importance does not require the retraining of the underlying model in order to measure the effect of shuffling variables on overall model accuracy. Because training the model can be extremely expensive and even take days, this is a big performance win. The risk is a potential bias towards correlated predictive variables.

If we ignore the computation cost of retraining the model, we can get the most accurate feature importance using a brute force _drop-column importance_ mechanism. The idea is to get a baseline performance score as with permutation importance but then drop a column entirely, retrain the model, and recompute the performance score. The importance value of a feature is the difference between the baseline and the score from the model missing that feature. This strategy answers the question of how important a feature is to overall model performance even more directly than the permutation importance strategy.

If we had infinite computing power, the drop-column mechanism would be the default for all RF implementations because it gives us a “ground truth” for feature importance. We can mitigate the cost by using a subset of the training data, but drop-column importance is still extremely expensive to compute because of repeated model training. Nonetheless, it's an excellent technique to know about and is a way to test our permutation importance implementation. The importance values could be different between the two strategies, but the order of feature importances should be roughly the same.

The implementation of drop-column is a straightforward loop like the permutation implementation and works with any model. For Random Forests, we don't need a validation set, nor do we need to directly capture OOB samples for performance measurement. In this case, we are retraining the model and so we can directly use the OOB score computed by the model itself. Here is the complete [implementation](https://github.com/parrt/random-forest-importances/blob/master/src/rfpimp.py#L57):

```python
def dropcol_importances(rf, X_train, y_train):
 rf_ = clone(rf)
 rf_.random_state = 999
 rf_.fit(X_train, y_train)
 baseline = rf_.oob_score_
 imp = []
 for col in X_train.columns:
 X = X_train.drop(col, axis=1)
 rf_ = clone(rf)
 rf_.random_state = 999
 rf_.fit(X, y_train)
 o = rf_.oob_score_
 imp.append(baseline - o)
 imp = np.array(imp)
 I = pd.DataFrame(
 data={'Feature':X_train.columns, 'Importance':imp})
 I = I.set_index('Feature')
 I = I.sort_values('Importance', ascending=True)
 return I
```

Notice that we force the random_state of each model to be the same. For the purposes of creating a general model, it's generally not a good idea to set the random state, except for debugging to get reproducible results. In this case, however, we are specifically looking at changes to the performance of a model after removing a feature. By controlling the random state, we are controlling a source of variability. Any change in performance should be due specifically to the drop of a feature.

**Figure 3(a)** and **Figure 3(b)** plot the feature importances for the same RF regressor and classifier from above, again with a column of random numbers. These results fit nicely with our understanding of real estate markets. Also notice that the random feature has negative importance in both cases, meaning that removing it improves model performance.

![Image 5](https://explained.ai/rf-importance/images/regr_dropcol_random.svg)
**Figure 3(a)**. Importances derived by dropping each column, retraining scikit-learn Random Forest **regressor**, and computing change in out-of-bag R $^2$. Predicting apartment rental price from 4 features + a column of random numbers. The importance of the random column is at the bottom as it should be.

![Image 6](https://explained.ai/rf-importance/images/cls_dropcol_random.svg)
**Figure 3(b)**. Importances derived by dropping each column, retraining scikit-learn Random Forest **classifier**, and computing change in out-of-bag accuracy. Predicting apartment interest level (low, medium, high) using 5 features + a column of random numbers. The importance of the random column is at the bottom as it should be.

That settles it for Python, so let's take a look at R, another popular language used for machine learning. [](https://explained.ai/rf-importance/)

### Comparing R to scikit-learn importances

Unfortunately, R's default importance strategy is mean-decrease-in-impurity, just like scikit, and so results are again unreliable. The reason for this default is that permutation importance is slower to compute than mean-decrease-in-impurity. For example, here's a code snippet (mirroring our Python code) to create a Random Forest and get the feature importances that traps the unwary:

```R
# Warning! default is mean-decrease-in-impurity!
rf <- randomForest(price~., data = df[, 1:5], mtry=4, ntree = 40)
imp <- importance(rf)
```

To get reliable results, we have to turn on importance=T in the Random Forest constructor function, which then computes both mean-decrease-in-impurity and permutation importances. After that, we have to use type=1 (not type=2) in the importances() function call:

```R
rf <- randomForest(price~., data = df, mtry = 4, ntree = 40, importance=T)
imp <- importance(rf, type=1, scale = F) # permutation importances
```

Make sure that you don't use the MeanDecreaseGini column in the importance data frame; you want column MeanDecreaseAccuracy.

It's worth comparing R and scikit in detail. It not only gives us another opportunity to verify the results of our homebrewed permutation implementation, but we can also demonstrate that R's default type=2 importances have the same issues as scikit's only importance implementation. [](https://explained.ai/rf-importance/)

#### R mean-decrease-in-impurity importance

R's mean-decrease-in-impurity importance (type=2) gives the same implausible results as we saw with scikit. To demonstrate this, we trained an RF regressor and classifier in R using the same data set and generated the importance graphs in **Figure 4**, which mirror the scikit graphs in **Figure 1**.

![Image 7](https://explained.ai/rf-importance/images/regr_dflt_random_R_annotated.png)
**Figure 4(a)**. R's type=2 importances for Random Forest **regressor** predicting apartment rental price from 4 features + a column of random numbers. Random column is last, as we would expect but the importance of the number of bathrooms for predicting price is highly suspicious.

![Image 8](https://explained.ai/rf-importance/images/cls_dflt_random_R_annotated.png)
**Figure 4(b)**. R's type=2 importances for Random Forest **classifier** predicting apartment interest level (low, medium, high) using 5 features + a column of random numbers. Highly suspicious that random column is much more important than the number of bedrooms.
[](https://explained.ai/rf-importance/)
#### R permutation importance

As a means of checking our permutation implementation in Python, we plotted and compared our feature importances side-by-side with those of R, as shown in **Figure 5** for regression and **Figure 6** for classification. The importance values themselves are different, but the feature order and relative levels are very similar, which is what we care about.

![Image 9](https://explained.ai/rf-importance/images/regr_permute_random_R.svg)
**Figure 5(a)**. R's type=1 permutation importance for RF **regressor**.

![Image 10](https://explained.ai/rf-importance/images/regr_permute_random.svg)
**Figure 5(b)**. Python permutation importance for RF **regressor**

![Image 11](https://explained.ai/rf-importance/images/cls_permute_random_R.svg)
**Figure 6(a)**. R's type=1 permutation importance for RF **classifier**.

![Image 12](https://explained.ai/rf-importance/images/cls_permute_random.svg)
**Figure 6(b)**. Python permutation importance for RF **classifier**.
[](https://explained.ai/rf-importance/)
#### R drop-column importance

For completeness, we implemented drop-column importance in R and compared it to our Python implementation, as shown in **Figure 8** for regression and **Figure 9** for classification.

![Image 13](https://explained.ai/rf-importance/images/regr_drop_random_R.svg)
**Figure 8(a)**. Importances derived by dropping each column, retraining an RF **regressor** in R, and computing the change in out-of-bag R $^2$.

![Image 14](https://explained.ai/rf-importance/images/regr_dropcol_random.svg)
**Figure 8(b)**. Importances derived by dropping each column, retraining a scikit RF **regressor**, and computing the change in out-of-bag R $^2$.

![Image 15](https://explained.ai/rf-importance/images/cls_drop_random_R.svg)
**Figure 9(a)**. Importances derived by dropping each column, retraining an RF **classifier** in R, and computing the change in out-of-bag accuracy.

![Image 16](https://explained.ai/rf-importance/images/cls_dropcol_random.svg)
**Figure 9(b)**. Importances derived by dropping each column, retraining a scikit RF **classifier**, and computing the change in out-of-bag accuracy.
[](https://explained.ai/rf-importance/)
### Experimental results

[](https://explained.ai/rf-importance/)
#### Model-neutral permutation importance

The permutation importance code shown above uses out-of-bag (OOB) samples as validation samples, which limits its use to RFs. If we rely on the standard scikit score() function on models, it's a simple matter to alter the permutation importance to work on any model. Also, instead of passing in the training data, from which OOB samples are drawn, we have to pass in a validation set. (Don't pass in your test set, which should only used as a final step to measure final model generality; the validation set is used to tune and probe a model.) Here's the core of the model-neutral version:

```python
baseline = model.score(X_valid, y_valid)
imp = []
for col in X_valid.columns:
 save = X_valid[col].copy()
 X_valid[col] = np.random.permutation(X_valid[col])
 m = model.score(X_valid, y_valid)
 X_valid[col] = save
 imp.append(baseline - m)
```

 See our function [importances()](https://github.com/parrt/random-forest-importances/blob/master/src/rfpimp.py#L23) in the rfpimp package. [](https://explained.ai/rf-importance/)
#### Performance considerations

The use of OOB samples for permutation importance computation also has strongly negative performance implications. Using OOB samples means iterating through the trees with a Python loop rather than using the highly vectorized code inside scikit/numpy for making predictions. For even data sets of modest size, the permutation function described in the main body of this article based upon OOB samples is extremely slow.

On a (confidential) data set we have laying around with 452,122 training records and 36 features, OOB-based permutat

## 💡 Key Insights
- Default Random Forest feature importance (mean decrease in impurity or Gini importance) in scikit-learn and R is biased, tending to inflate the importance of continuous or high-cardinality categorical variables.
- Permutation importance is a more reliable, model-agnostic technique that measures feature importance by observing the drop in model accuracy (or R^2 score) when a feature's values are randomly shuffled.
- Drop-column importance, while computationally expensive due to requiring model retraining for each dropped feature, provides the most accurate 'ground truth' for feature importance.
- For reliable results in Python, use permutation importance (e.g., via the `rfpimp` package). In R, enable `importance=T` in the `randomForest` constructor and use `type=1` and `scale=F` in the `importance()` function.
- Accurate feature importance is crucial for model interpretation, understanding predictive drivers, and making informed decisions, especially when default methods yield counter-intuitive or misleading results.

## 📚 References
- Terence Parr, Kerem Turgutlu, Christopher Csiszar, and Jeremy Howard, "Beware Default Random Forest Importances", explained.ai, March 26, 2018 (updated June 8, 2020), https://explained.ai/rf-importance/ *(source)*
- Leo Breiman, "Statistical Modeling: The Two Cultures", Statistical Science, 2001, https://projecteuclid.org/euclid.ss/1009213726 *(cited)*
- Strobl, C., Boulesteix, A.-L., Zeileis, A. et al., "Bias in random forest variable importance measures: Illustrations, sources and a solution", BMC Bioinformatics, 2007, https://link.springer.com/article/10.1186%2F1471-2105-8-25 *(cited)*
- Strobl, C., Boulesteix, A.-L., Kneib, T. et al., "Conditional variable importance for random forests", BMC Bioinformatics, 2008, https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-9-307 *(cited)*
- Terence Parr, James D. Wilson, Jeff Hamrick, "Nonparametric Feature Impact and Importance", arXiv preprint arXiv:2006.04750, 2020, https://arxiv.org/abs/2006.04750 *(cited)*
- Terence Parr, Jeremy Howard, "Partial Dependence through Stratification", arXiv preprint arXiv:1907.06698, 2019, https://arxiv.org/abs/1907.06698 *(cited)*
- scikit-learn, "ENH Add permutation importance", GitHub Pull Request #13146, 2019, https://github.com/scikit-learn/scikit-learn/pull/13146 *(cited)*
- Terence Parr, "rfpimp package", GitHub, https://github.com/parrt/random-forest-importances/tree/master/src *(cited)*
- Terence Parr, "ANTLR parser generator", http://www.antlr.org/ *(cited)*
- Jeremy Howard, "fast.ai courses", http://course.fast.ai/ *(cited)*
- University of San Francisco, "MS in Data Science program", https://www.usfca.edu/arts-sciences/graduate-programs/data-science *(cited)*
- Stack Overflow, "How are feature importances in RandomForestClassifier determined?", https://stackoverflow.com/questions/15810339/how-are-feature-importances-in-randomforestclassifier-determined *(cited)*
- Breiman, L., Cutler, A., "Random Forests: Variable Importance", https://www.stat.berkeley.edu/~breiman/RandomForests/cc_home.htm#varimp *(cited)*
- Kaggle, "Two Sigma Connect: Rental Listing Inquiries competition", https://www.kaggle.com/c/two-sigma-connect-rental-listing-inquiries *(cited)*
- Terence Parr, "rent.csv data file", GitHub, https://github.com/parrt/random-forest-importances/blob/master/notebooks/data/rent.csv *(cited)*
- Terence Parr, "OOB classifier accuracy function", GitHub, https://github.com/parrt/random-forest-importances/blob/master/src/rfpimp.py#L237 *(cited)*
- Terence Parr, "OOB regression R2 score function", GitHub, https://github.com/parrt/random-forest-importances/blob/master/src/rfpimp.py#L263 *(cited)*
- Terence Parr, "dropcol_importances implementation", GitHub, https://github.com/parrt/random-forest-importances/blob/master/src/rfpimp.py#L57 *(cited)*
- Terence Parr, "model-neutral importances() function", GitHub, https://github.com/parrt/random-forest-importances/blob/master/src/rfpimp.py#L23 *(cited)*

## 🏷️ Classification
The content focuses on advanced techniques and best practices for interpreting machine learning models (specifically Random Forests) by addressing biases in feature importance calculations, which is a core topic in Data Science.
