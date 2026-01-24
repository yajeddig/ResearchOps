---
title: "AI-Driven Predictive Control for Condensate Stabilization – IntelliDynamics"
date: 2026-01-24
category: Process_Engineering
confidence: 0.95
tags: ['AI-driven control', 'Predictive control', 'Machine learning', 'Neural networks', 'Distillation control', 'NGL stabilization', 'Process optimization', 'Reid Vapor Pressure (RVP)', 'DCS integration', 'OSIsoft PI', 'Industrial AI', 'Advanced Process Control (APC)', 'sector:petrochem']
source: "https://intellidynamics.net/case-studies/ai-driven-predictive-control-for-condensate-stabilization/"
type: Article
source_type: Article
hash: 083655
---

## 🎯 Relevance
This case study demonstrates a high ROI through significant product quality improvement and cost savings in a critical petrochemical process. It serves as an excellent industrial application example of advanced process control leveraging machine learning, offering valuable learning opportunities for implementing similar AI-driven optimization solutions in complex industrial settings.

## 📖 Content
Executive Summary
-----------------

IntelliDynamics implemented an intelligent predictive control system for a major integrated gas processing facility implemented to optimize Natural Gas Liquids (NGL) stabilization across four distillation towers. The system reduced product quality losses by 44% and increased on-specification product from 18% to 58%, delivering annual savings of $250,000-$750,000 USD while maintaining 99% prediction accuracy despite challenging operational conditions.

The Challenge
-------------

The Process Problem
-------------------

Natural gas liquids stabilization is a critical step in gas processing where lighter hydrocarbons are separated from heavier ones through distillation. The product specification requires Reid Vapor Pressure (RVP) to fall within a narrow range of 11.5-12.0 psig. Products below specification (over-stabilized) represent lost revenue because valuable liquid hydrocarbons have been converted to less-valuable gas. Products above specification (under-stabilized) create serious safety and storage problems.

### The situation before automation:

– **68% of product was over-stabilized** (RVP < 11.5 psig)

– **Only 18% met specification** (11.5-12.0 psig)

– **14% was under-stabilized** (RVP > 12.0 psig)

– **Product variance was extremely high** (σ = 3.21 psi)

Operational Challenges
----------------------

Operators faced multiple complicating factors:

1. **Delayed and Inaccurate Feedback**: The RVP analyzer provided readings with a 15-30 minute delay and ±5% accuracy, making manual control reactive rather than proactive

2. **Uncontrolled Feed Variations**: Liquid slugs from offshore platforms created sudden, unpredictable changes in feed rate and composition, frequently flooding the towers

3. **Unstable Temperature Control**: The tower temperature control loop exhibited 5:1 overshoot with poor damping, amplifying disturbances

4.**Competing Constraints**: Managing RVP while simultaneously keeping True Vapor Pressure (TVP) below storage limits created a narrow operating window

5. **Manual Adjustment Inefficiency**: Operators adjusted reboiler heat through trial-and-error, meaning off-spec product continued flowing to storage during the adjustment period

The Solution: Model-Predictive Machine Learning Control
-------------------------------------------------------

System Architecture
-------------------

IntelliDynamics’ intelligent RVP (I-RVP) system combined several technologies:

### Data Infrastructure:

– Integrated with an existing OSIsoft PI historian for real-time and historical data collection

– OPC interface to an existing Yokogawa DCS

– 1-minute data sampling from 12+ process variables per tower

### Predictive Modeling:

– Neural network models trained on historical operating data, to predict RVP using feed and tower conditions

– 15-minute prediction horizon to match process response time

– Inputs included tower temperatures, pressures, flows, and current RVP readings

### Optimization & Control:

– IntelliDynamics’ real-time optimizer calculated optimal reboiler temperature setpoints

– Automated setpoint were sent to the Yokogawa DCS for application 

– Built-in safety interlocks and operating envelope constraints were implemented

Why Neural Networks?
--------------------

Traditional first-principles models struggle with this application because:

– Feed composition data isn’t available in real-time

– Complex interactions between 12+ variables are difficult to model mathematically

– Process dynamics change with operating conditions

Neural networks excel at:

– Learning complex, non-linear relationships from data

– Adapting to changing feed conditions

– Making accurate predictions despite unmeasured disturbances

The Prediction Challenge
------------------------

**Original goal:** Predict RVP 1-2 hours ahead

**Reality:** Process response time analysis revealed that temperature changes affect RVP in approximately 15-20 minutes. A 1-hour prediction would be too late for effective control.

**Solution implemented:** 15-minute predictive model updating every 5 seconds, providing:

– Enough lead time to adjust before problems occur

– Fast enough response to handle feed disturbances

– Continuous adaptation to current conditions

Implementation Approach
-----------------------

Single Tower Proof-of-Concept
-----------------------------

The project focused initial implementation on one of four stabilization units:

1. **Model Development**

– Data collection and cleaning from historical operations

– Variable selection based on process knowledge

– Model training and offline validation achieving 99% accuracy

2. **System Integration**

– PI/OPC communication setup

– DCS screen and control logic development

– Safety interlock programming

3. **Field Validation**

– Offline testing with live data

– Operator training

– Gradual transition from monitoring to control

4. **Performance Monitoring**

– System ran in automatic mode 64% of the time

– Operators maintained manual override capability

Operating Modes
---------------

**Manual Mode**: Operators control temperature setpoint directly

– Used during anticipated instabilities

– During major feed rate changes

– When analyzer is offline for maintenance

**Automatic Mode:** I-RVP system controls temperature setpoint

– Predicts RVP every 5 seconds

– Optimizes setpoint when prediction falls outside 11.5-12.0 range

– Implements changes gradually to avoid temperature control loop oscillations

Safety Features
---------------

1. **Operating Envelope Limits**

– System only operates when feed flow 50-300 m³/hr of liquid

– All variables within trained model range

2. **Prediction Quality Checks**

– Automatic switch to manual if predicted RVP deviates >10% from actual

– Continuous accuracy monitoring

3. **Setpoint Change Limits**

– Maximum 0.5°C per step

– 15-minute minimum between changes

– Prevents exciting temperature control instabilities

4. **Communication Monitoring**

– Heartbeat signal confirms system health

– Automatic manual mode if communication fails

Results
-------

Performance Metrics (Auto Mode)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Metric Before With I-RVP Improvement

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
---------------------------------------------------------------------------------------------------------------------------------------------

In-Specification 18%58%223%

Over-Stabilized 68%38%44%

Under-Stabilized 14%4%71%

Product Variance 3.21 psi 0.28 psi 91%

Prediction Accuracy N/A 99%—

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Economic Impact
---------------

**Annual Value:** $250,000 – $750,000 USD per tower

– Based on liquid-gas price differential

– Reduction in over-stabilization losses

– Improved product consistency

Operational Performance
-----------------------

**System Availability**: 98%

– 2% downtime primarily from network communication issues

– Most interruptions brief (<10 minutes)

**Time in Automatic Mode:** 64%

– Operators chose manual mode 33% of the time

– Primarily during anticipated disturbances (tower flooding) or maintenance

– Increased operator confidence over monitoring period

Performance Under Varying Conditions
------------------------------------

**High vs. Low Feed Rates**: 

– High flow (228-275 m³/hr): 46% in-spec vs. 18% baseline

– Low flow (95-168 m³/hr): 62% in-spec vs. 18% baseline

– System maintained 99% accuracy at both flow regimes

**Varying Feed Compositions:**

– Composition changed significantly (methane: 80-84%, ethane: 6-8%)

– RVP control maintained despite no composition measurements

– Accuracy remained at 99% across all compositions tested

Technical Insights
------------------

Why 15 Minutes, Not Hours?
--------------------------

Lead/lag correlation analysis between tower temperature and RVP showed:

– Maximum correlation at 1 hour with hourly data

– But maximum correlation at 15-20 minutes with minute-interval data

– Process response time ≈ 15-20 minutes

This is why the 15-minute model proved essential for control, while a separately developed 1-hour model was accurate but not useful for optimization.

Model Inputs (12 Variables)
---------------------------

The neural network used readily available process measurements:

– Tower temperatures (bottom, reboiler, controlled)

– Feed flows (total, HP, MP, tray split)

– Tower pressure and level

– Gas flows

– Current RVP reading (critical for compensating unmeasured disturbances)

Handling the RVP Measurement Challenge
--------------------------------------

The ±5% analyzer accuracy (±0.3 psig) presented a unique challenge:

**The workaround:**

– Use current RVP reading as a model input

– Model predicts 15 minutes ahead from current reading

– Effectively makes model predict the _change_ in RVP

– Compensates for analyzer bias and unmeasured disturbances

**Trade-off:**

– System depends on having a working analyzer

– But gains robustness to feed composition changes

– Virtual RVP analyzer developed as backup

**Temperature Control Loop Issues**

The under-damped temperature controller was a limiting factor:

– 5:1 overshoot ratio (well above the ideal 4:1)

– Decay ratio of 0.25 (should be closer to 0.1)

**I-RVP compensated by:**

– Ramping setpoint changes (0.5°C max, 15-min intervals)

– Avoiding exciting controller oscillations

– Still achieving variance reduction of 91%

But: Re-tuning the temperature controller was recommended to unlock further improvements

Lessons Learned
---------------

What Worked Well
----------------

1. **Incremental Implementation**

– Starting with one tower reduced risk

– Allowed operator training and confidence building

– Proved concept before full deployment

2. **Operator Control Retention**

– Manual override capability maintained operator buy-in

– Operators used manual mode strategically

– Trust in system grew over monitoring period

3. **Conservative Setpoint Changes**

– Slow ramping avoided controller instabilities

– Prevented system from fighting with DCS

– Sometimes less aggressive control is more effective

4. **Real-time Adaptation**

– Using current RVP as input enabled robust performance

– System handled unmeasured feed disturbances

– No need for online composition analyzers

Recommendations for Similar Projects
------------------------------------

1. **Understand Process Dynamics First**

– Don’t assume prediction horizon requirements

– Perform correlation analysis on actual data

– Match control timing to process response

2. **Start Simple, Build Complexity**

– Prove basic concept before adding features

– Single-input-single-output before multi-variable

– Demonstrate value early and often

3. **Design for Operations**

– Maintain manual override

– Gain Operator buy-in

– Clear visual indicators of system state

– Comprehensive operator training

4. **Plan for Imperfect Measurements**

– Work with existing instrumentation

– Use advance IntelliDynamics genetically optimized neural network modeling

– Quantify improvement potential from better sensors

5. **Set Realistic Expectations**

– Understand physical and equipment limitations

– Document assumptions and constraints

Technical Specifications
------------------------

Software Platform:
------------------

IntelliDynamics’ Intellect Suite of Industrial AI software:

*   Intellect Server (runtime), Server Console (operations)
*   Expert (data schema, data access, data cleansing, predictive modeling)
*   iImprove (model inversion for control setpoints)

OSIsoft PI Universal Data Server

PI-OPC Interface

Hardware:
---------

Windows server for PI and Intellect

Windows desktop for OPC interface

Existing Yokogawa Centum DCS

Model Performance:
------------------

**Offline accuracy**: 99% (validated on 880 data points)

**Online accuracy**: 99% (averaged over 5 months)

**Prediction frequency**: Every 5 seconds

**Data extraction**: 1-minute intervals

**Prediction horizon:** 15 minutes ahead

Conclusion
----------

This project demonstrated that AI-based predictive control using IntelliDynamics’ technologies delivers substantial operational and economic benefits even with challenging conditions:

– Delayed, inaccurate measurements (30-minute lag, ±5% error)

– Uncontrolled disturbances (offshore platform slugs)

– Equipment limitations (under-damped temperature control)

– Competing constraints (RVP vs. TVP)

The key success factors were:

1. Understanding actual process response times through data analysis

2. Designing the system to work with existing infrastructure

3. Maintaining operator control and building confidence gradually

4. Using neural networks to handle complex, non-linear behavior

5. Implementing robust safety interlocks and operating envelopes

The 223% increase in on-specification product and 99% prediction accuracy proved that model-predictive control is viable for complex distillation operations, providing a foundation for broader deployment and continuous improvement.

* * *

For more information…
---------------------

… about implementing predictive control systems in your operations, or to discuss how AI-driven optimization could benefit your process, please contact us at [info@intellidynamics.net](mailto:info@intellidynamics.net)

## 💡 Key Insights
- Implemented an AI-driven predictive control system using neural networks for NGL stabilization across distillation towers, significantly improving product quality and reducing losses.
- Achieved a 223% increase in on-specification product (from 18% to 58%) and a 91% reduction in product variance, leading to annual savings of $250,000-$750,000 USD per tower.
- The system effectively addressed critical operational challenges including delayed/inaccurate RVP feedback, uncontrolled feed variations (liquid slugs), unstable temperature control loops, and competing process constraints.
- A crucial technical insight was identifying the optimal 15-minute prediction horizon through process dynamics analysis, which was essential for effective control rather than longer horizons.
- Robustness was achieved by incorporating the current RVP reading as a model input, allowing the system to compensate for analyzer inaccuracies and unmeasured feed disturbances without requiring online composition analyzers.
- Key success factors included incremental implementation on a single tower, maintaining operator manual override capability to build trust, and conservative setpoint changes to avoid exciting existing control loop instabilities.

## 📚 References
- IntelliDynamics, AI-Driven Predictive Control for Condensate Stabilization, https://intellidynamics.net/case-studies/ai-driven-predictive-control-for-condensate-stabilization/ *(source)*

## 🏷️ Classification
The content details the design, implementation, and results of an advanced control system for a distillation process, directly aligning with the 'contrôle' aspect of Process Engineering.
