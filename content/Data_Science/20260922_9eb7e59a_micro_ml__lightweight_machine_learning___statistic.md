---
title: 'micro-ml: Lightweight Machine Learning & Statistics Library for JavaScript
  (Rust/WASM)'
date: '2026-09-22'
category: Data_Science
confidence: 0.95
tags: [machine learning, statistics, javascript, rust, webassembly, wasm, lightweight,
  regression, classification, clustering, forecasting, smoothing, anomaly detection,
  dimensionality reduction, time series analysis, data analysis, edge computing, iot]
source: https://github.com/AdamPerlinski/micro-ml
type: Article
source_type: GitHub Repository
hash: 9eb7e59a5f95
---
## 🎯 Relevance
This library is highly relevant for process engineering and industrial data science as it provides a lightweight, high-performance solution for embedding machine learning and statistical analysis directly into industrial applications, edge devices, or web-based dashboards. Its capabilities for sensor data smoothing, anomaly detection, forecasting process variables, and analyzing growth rates are directly applicable to real-time process monitoring, predictive maintenance, and operational optimization, offering a low-overhead alternative to larger ML frameworks.

## 📖 Content
[![Image 1: micro-ml](https://raw.githubusercontent.com/AdamPerlinski/micro-ml/main/docs/logo.svg)](https://raw.githubusercontent.com/AdamPerlinski/micro-ml/main/docs/logo.svg)

[![Image 2: npm version](https://camo.githubusercontent.com/eafadb3f64e6e6e5d499d66a2660887d198e8259b9cd3e4504bba190d6d99c82/68747470733a2f2f696d672e736869656c64732e696f2f6e706d2f762f6d6963726f2d6d6c3f636f6c6f723d636230303030)](https://www.npmjs.com/package/micro-ml)[![Image 3: npm downloads](https://camo.githubusercontent.com/fd8c49a474fd7567dd30e3c7069bcfa9d268b7392db1c3448b29f94c0e13ff0f/68747470733a2f2f696d672e736869656c64732e696f2f6e706d2f646d2f6d2f6d6963726f2d6d6c3f636f6c6f723d636230303030)](https://www.npmjs.com/package/micro-ml)[![Image 4: bundle size](https://camo.githubusercontent.com/b4b79ecf55f02ab251f3722b0b4e2194f4f24b9abe623a57168f8e8dc853e894/6874747070733a2f2f696d672e736869656c64732e696f2f62756e646c6570686f6269612f6d696e7a69702f6d6963726f2d6d6c3f636f6c6f723d636230303030266c6162656c3d73697a65)](https://bundlephobia.com/package/micro-ml)[![Image 5: license](https://camo.githubusercontent.com/5bf12ec7e805cd7121d48d731cce337f549829c8ef9133dcd71e2549501591ab/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6963656e73652f4164616d5065726c696e736b692f6d6963726f2d6d6c3f636f6c6f723d636230303030)](https://github.com/AdamPerlinski/micro-ml/blob/main/LICENSE)[![Image 6: GitHub stars](https://camo.githubusercontent.com/db1b65e0d4b4d21cfd795ee94ac74f84778174f7e1715bf065fbcd5e2a09efa3/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f73746172732f4164616d5065726c696e736b692f6d6963726f2d6d6c3f7374796c653d736f6369616c)](https://github.com/AdamPerlinski/micro-ml)

[![Image 7: Live Docs & Demos](https://camo.githubusercontent.com/bfa79ddfb9fab90768982ee5c5c4b69186423d523aad8e9d2b135a01d8411185/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2545322539362542362532304c697665253230446f637325323025323625323044656d6f732d5669736974253230536974652d3633363666313f7374796c653d666f722d7468652d6261646765266c6f676f436f6c6f723d7768697465)](https://adamperlinski.github.io/micro-ml/)

**You don't need TensorFlow.js for a trendline.**

Most apps just need simple predictions: forecast next month's sales, add a trendline to a chart, smooth noisy sensor data. You don't need a 500KB neural network library for that.

micro-ml is **~56KB gzipped** — 8 ML algorithms + regression + smoothing + forecasting. All in WASM. Sub-millisecond on typical datasets.

```bash
npm install micro-ml
```

* * *

## What Can You Do With It?

### Predict Future Values
Got historical data? Predict what comes next.

```javascript
// You have: sales data for 12 months
const sales = [10, 12, 15, 18, 22, 25, 28, 32, 35, 40, 45, 50];

// You want: forecast for next 3 months
const forecast = await trendForecast(sales, 3);
console.log(forecast.getForecast()); // [55, 60, 65]
console.log(forecast.direction);      // "up"
```

### Find Trends in Data
Is your data going up, down, or flat? How strong is the trend?

```javascript
const model = await linearRegressionSimple(sales);
console.log(model.slope);     // 3.7 (growing by ~3.7 per month)
console.log(model.rSquared);  // 0.98 (98% confidence - strong trend)
```

### Smooth Noisy Data
Sensor readings jumping around? Stock prices too volatile? Smooth them out.

```javascript
// Raw sensor data (noisy)
const readings = [22.1, 25.3, 21.8, 24.9, 23.2, 26.1, 22.5, ...];

// Smoothed (removes noise, shows real trend)
const smooth = await ema(readings, 5);
```

### Fit Curves to Data
Data doesn't follow a straight line? Fit a curve instead.

```javascript
// Exponential growth (bacteria, viral spread, compound interest)
const expModel = await exponentialRegression(time, population);
console.log(expModel.doublingTime()); // "Population doubles every 3.2 days"

// Polynomial curve (projectile motion, diminishing returns)
const polyModel = await polynomialRegression(x, y, { degree: 2 });
```

### Classify Data
Got labelled data? Train a classifier.

```javascript
import { knnClassifier, logisticRegression } from 'micro-ml';

// kNN — simple, no training
const knn = await knnClassifier(trainingData, labels, { k: 5 });
knn.predict([[1.5, 2.0]]); // [0] or [1]

// Logistic Regression — fast, probabilistic
const lr = await logisticRegression(data, labels, { maxIterations: 200 });
lr.predictProba([[1.5, 2.0]]); // [0.87]
```

### Cluster Data
Find natural groups without labels.

```javascript
import { kmeans, dbscan } from 'micro-ml';

// k-Means — you know how many clusters
const km = await kmeans(points, { k: 3 });
km.getCentroids();    // [[x,y], [x,y], [x,y]]
km.getAssignments();  // [0, 1, 2, 0, 1, ...]

// DBSCAN — discovers clusters + noise automatically
const db = await dbscan(points, { eps: 0.5, minPoints: 4 });
db.nClusters; // 3
db.nNoise;    // 12
```

### Reduce Dimensions
Visualise high-dimensional data in 2D.

```javascript
import { pca } from 'micro-ml';

// 50-dimensional data → 2 components
const result = await pca(data, { nComponents: 2 });
result.getExplainedVarianceRatio(); // [0.85, 0.10] (95% variance kept)
result.getTransformed();            // [[x,y], [x,y], ...]
```

* * *

## When to Use Which Function?

| Your Data Looks Like | Use This | Example |
| --- | --- | --- |
| Straight line trend | `linearRegression` | Stock price over time |
| Curved line | `polynomialRegression` | Ball trajectory, learning curves |
| Exponential growth | `exponentialRegression` | Bacteria growth, viral spread |
| Logarithmic (fast then slow) | `logarithmicRegression` | Learning a skill, diminishing returns |
| Noisy/jumpy data | `ema` or `sma` | Sensor readings, stock prices |
| Need future predictions | `trendForecast` | Sales forecast, weight loss goal |
| Find peaks/valleys | `findPeaks` / `findTroughs` | Detect anomalies, buy/sell signals |
| Group similar items | `kmeans` | Customer segments, image colours |
| Classify new items | `knnClassifier` | Spam detection, image recognition |
| Binary yes/no | `logisticRegression` | Churn prediction, fraud detection |
| Find clusters + outliers | `dbscan` | Anomaly detection, geo clustering |
| Decision rules | `decisionTree` | Loan approval, feature importance |
| Reduce dimensions | `pca` | Visualisation, feature extraction |
| Seasonal patterns | `detectSeasonality` | Monthly sales cycles, weekly patterns |

* * *

## Real-World Use Cases

### 1. Sales Forecasting
**Problem:** "How much will we sell next quarter?"

```javascript
import { trendForecast, linearRegressionSimple } from 'micro-ml';

const monthlySales = [42000, 45000, 48000, 52000, 55000, 58000];

// Analyze trend
const model = await linearRegressionSimple(monthlySales);
console.log(`Growing by $${model.slope.toFixed(0)}/month`);

// Forecast next 3 months
const forecast = await trendForecast(monthlySales, 3);
console.log('Next 3 months:', forecast.getForecast());
// → [61000, 64000, 67000]
```

### 2. Stock/Crypto Trendlines
**Problem:** "Is this stock trending up or down? Add a trendline to my chart."

```javascript
import { linearRegression, ema } from 'micro-ml';

const days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
const prices = [150, 152, 149, 155, 158, 156, 160, 163, 161, 165];

// Fit trendline
const trend = await linearRegression(days, prices);
const trendlinePoints = trend.predict(days);
// → Draw this as a line on your chart

// Add moving average (smoothed price)
const smoothPrices = await ema(prices, 3);
// → Draw this as another line
```

### 3. Weight Loss Prediction
**Problem:** "When will I reach my goal weight?"

```javascript
import { linearRegressionSimple } from 'micro-ml';

const weeklyWeights = [200, 198, 196.5, 195, 193, 191.5]; // lbs
const goalWeight = 175;

const model = await linearRegressionSimple(weeklyWeights);
const lossPerWeek = Math.abs(model.slope); // 1.5 lbs/week

const currentWeight = weeklyWeights[weeklyWeights.length - 1];
const weeksToGoal = (currentWeight - goalWeight) / lossPerWeek;

console.log(`Losing ${lossPerWeek.toFixed(1)} lbs/week`);
console.log(`Goal in ${Math.ceil(weeksToGoal)} weeks`);
// → "Losing 1.5 lbs/week, Goal in 11 weeks"
```

### 4. IoT Sensor Smoothing
**Problem:** "Temperature sensor is noisy, I want a stable reading."

```javascript
import { ema, exponentialSmoothing } from 'micro-ml';

// Raw readings jump around: 22.1, 25.3, 21.8, 24.9, ...
const rawTemperature = getSensorReadings();

// Smoothed readings: 22.5, 23.1, 22.8, 23.2, ...
const smoothed = await ema(rawTemperature, 5);

// Display the last smoothed value
displayTemperature(smoothed[smoothed.length - 1]);
```

### 5. Growth Rate Analysis
**Problem:** "How fast is our user base growing? When will we hit 1 million?"

```javascript
import { exponentialRegression } from 'micro-ml';

const months = [1, 2, 3, 4, 5, 6];
const users = [1000, 1500, 2200, 3300, 5000, 7500];

const model = await exponentialRegression(months, users);

console.log(`Doubling every ${model.doublingTime().toFixed(1)} months`);
// → "Doubling every 1.4 months"

// When will we hit 1 million?
// Solve: 1000000 = a * e^(b*t)
const monthsToMillion = Math.log(1000000 / model.a) / model.b;
console.log(`1M users in ${monthsToMillion.toFixed(0)} months`);
```

### 6. Detecting Anomalies
**Problem:** "Alert me when sensor readings spike."

```javascript
import { findPeaks, ema } from 'micro-ml';

const readings = [...sensorData];

// Find all spike indices
const spikes = await findPeaks(readings);

// Alert if recent spike
if (spikes.includes(readings.length - 1)) {
  alert('Anomaly detected!');
}
```

* * *

## Installation

```bash
npm install micro-ml
```

## Quick Start

```javascript
import { linearRegression, trendForecast, ema } from 'micro-ml';

// Fit a line to data
const model = await linearRegression([1,2,3,4,5], [2,4,6,8,10]);
console.log(model.slope);        // 2
console.log(model.predict([6])); // [12]

// Forecast future values
const forecast = await trendForecast([10,20,30,40,50], 3);
console.log(forecast.getForecast()); // [60, 70, 80]

// Smooth noisy data
const smooth = await ema([10,15,12,18,14,20], 3);
```

## Browser Usage

```html
<script type="module">
  import { linearRegression } from 'https://esm.sh/micro-ml';

  const model = await linearRegression([1,2,3], [2,4,6]);
  console.log(model.slope); // 2
</script>
```

* * *

## API Reference
### Regression (Find Patterns)

| Function | What It Does | When to Use |
| --- | --- | --- |
| `linearRegression(x, y)` | Fits straight line: y = mx + b | Steady growth/decline |
| `linearRegressionSimple(y)` | Same but x = [0,1,2,...] | Time series data |
| `polynomialRegression(x, y, {degree})` | Fits curve | Curved patterns |
| `exponentialRegression(x, y)` | Fits y = a × e^(bx) | Growth/decay |
| `logarithmicRegression(x, y)` | Fits y = a + b × ln(x) | Diminishing returns |
| `powerRegression(x, y)` | Fits y = a × x^b | Power laws |

### Smoothing (Remove Noise)

| Function | What It Does | When to Use |
| --- | --- | --- |
| `sma(data, window)` | Simple Moving Average | General smoothing |
| `ema(data, window)` | Exponential Moving Average | Recent values matter more |
| `wma(data, window)` | Weighted Moving Average | Balance of both |
| `exponentialSmoothing(data, {alpha})` | Single exponential smooth | Quick smoothing |

### Forecasting (Predict Future)

| Function | What It Does | When to Use |
| --- | --- | --- |
| `trendForecast(data, periods)` | Analyze trend + predict | Future predictions |
| `predict(xTrain, yTrain, xNew)` | One-liner predict | Quick predictions |
| `trendLine(data, periods)` | Get model + predictions | When you need both |

### Analysis (Understand Data)

| Function | What It Does | When to Use |
| --- | --- | --- |
| `findPeaks(data)` | Find local maxima | Detect spikes |
| `findTroughs(data)` | Find local minima | Detect dips |
| `rateOfChange(data, periods)` | % change from n ago | Growth rate |
| `momentum(data, periods)` | Difference from n ago | Trend strength |

### Classification (Label Data)

| Function | What It Does | When to Use |
| --- | --- | --- |
| `knnClassifier(data, labels, {k})` | k-Nearest Neighbours | Simple classification |
| `logisticRegression(data, labels, opts)` | Logistic regression | Binary classification |
| `naiveBayes(data, labels)` | Gaussian Naive Bayes | Text/feature classification |
| `decisionTree(data, labels, {maxDepth})` | CART decision tree | Interpretable rules |
| `perceptron(data, labels, opts)` | Single-layer perceptron | Linear separability |

### Clustering (Find Groups)

| Function | What It Does | When to Use |
| --- | --- | --- |
| `kmeans(data, {k})` | k-Means clustering | Known number of groups |
| `dbscan(data, {eps, minPoints})` | Density-based clustering | Unknown clusters + noise |

### Dimensionality Reduction

| Function | What It Does | When to Use |
| --- | --- | --- |
| `pca(data, {nComponents})` | Principal Component Analysis | Reduce dimensions, visualise |

### Seasonality

| Function | What It Does | When to Use |
| --- | --- | --- |
| `seasonalDecompose(data, period)` | Decompose trend + seasonal + residual | Understand patterns |
| `autocorrelation(data, maxLag)` | Autocorrelation function | Find repeating patterns |
| `detectSeasonality(data)` | Auto-detect period + strength | Unknown periodicity |

* * *

## Model Properties
All regression models return:

```javascript
model.rSquared   // 0-1, how well the model fits (1 = perfect)
model.n          // Number of data points used
model.predict(x) // Predict y values for new x values
model.toString() // Human-readable equation
```

Linear models also have:

```javascript
model.slope      // Rate of change
model.intercept  // Y-intercept
```

Exponential models also have:

```javascript
model.a          // Initial value
model.b          // Growth rate
model.doublingTime() // Time to double
```

* * *

## Performance
Benchmarked in Node.js (median of 3 runs):

| Algorithm | Data Size | Time |
| --- | --- | --- |
| Linear Regression | 100,000 pts | 0.9ms |
| k-Means | 10,000 pts, k=5 | 2ms |
| kNN | 5,000 train, predict 20 | 3.4ms |
| Logistic Regression | 5,000 pts | 11ms |
| DBSCAN | 2,000 pts | 12ms |
| Naive Bayes | 10,000 pts | 0.2ms |
| PCA | 5,000 × 50 → 2 | 13ms |
| Perceptron | 10,000 pts | 0.1ms |
| Seasonal Decompose | 1,000 pts | 0.02ms |
| SMA/EMA/WMA | 100,000 pts | 3ms |

For very large datasets, use Web Workers:

```javascript
import { createWorker } from 'micro-ml/worker';

const ml = createWorker();
const model = await ml.linearRegression(hugeX, hugeY); // Non-blocking
ml.terminate();
```

* * *

## Comparison

| Library | Size (gzip) | Speed |
| --- | --- | --- |
| **micro-ml** | ~56KB | Fastest (WASM) |
| TensorFlow.js | 500KB+ | Slow |
| ml.js | 150KB | Medium |
| simple-statistics | 30KB | Pure JS, slower |

* * *

## Links
*   [Documentation & Live Demos](https://adamperlinski.github.io/micro-ml/)
*   [npm package](https://www.npmjs.com/package/micro-ml)
*   [GitHub](https://github.com/AdamPerlinski/micro-ml)

## License
MIT

## 💡 Key Insights
- micro-ml is a lightweight (~56KB gzipped) machine learning and statistics library for JavaScript, built with Rust/WASM for high performance and zero dependencies.
- It provides 16 common algorithms including various regression models (linear, polynomial, exponential, logarithmic, power), smoothing techniques (SMA, EMA, WMA, exponential smoothing), forecasting, classification (kNN, Logistic Regression, Naive Bayes, Decision Tree, Perceptron), clustering (k-Means, DBSCAN), dimensionality reduction (PCA), and seasonality analysis.
- The library is optimized for simple predictions, trend analysis, and data smoothing, making it suitable for resource-constrained environments like IoT edge devices or client-side web applications.
- Benchmarks demonstrate sub-millisecond to tens of milliseconds execution times for typical datasets, with support for Web Workers to handle larger datasets asynchronously.
- It offers a significantly smaller footprint and faster execution compared to alternatives like TensorFlow.js or ml.js, making it ideal for applications where bundle size and performance are critical.

## 📚 References
- AdamPerlinski/micro-ml: Tiny ML & statistics library for JS — 16 algorithms in ~56KB gzipped. Rust/WASM, zero dependencies., GitHub, https://github.com/AdamPerlinski/micro-ml *(source)*
- TensorFlow.js *(cited)*
- ml.js *(cited)*
- simple-statistics *(cited)*

## 🏷️ Classification
The content describes a software library implementing various machine learning and statistical algorithms, which directly falls under the 'Data_Science' category.
