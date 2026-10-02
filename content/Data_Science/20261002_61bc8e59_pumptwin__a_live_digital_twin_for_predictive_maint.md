---
title: 'PumpTwin: A Live Digital Twin for Predictive Maintenance of a Hydraulic Test
  Rig'
date: '2026-10-02'
category: Data_Science
confidence: 0.95
tags: [Digital Twin, Predictive Maintenance, Hydraulic Systems, System Modeler, Condition
    Monitoring, Hybrid Modeling, Sensor Data Analytics, Industrial IoT, Prognostics
    and Health Management]
source: https://www.systemsnotcode.com/labs/pumptwin/
type: Article
source_type: Article
hash: 61bc8e599d41
---
## 🎯 Relevance
This content is highly relevant for industrial applications, showcasing the practical implementation of digital twin technology for predictive maintenance. It demonstrates how hybrid modeling (physics-based models combined with sensor data) can be used to monitor component health, forecast potential issues, and reduce downtime, offering significant ROI through improved operational efficiency and reduced maintenance costs. It serves as an excellent learning opportunity for understanding digital twin architecture and its application in condition monitoring.

## 📖 Content
## PumpTwin · a live digital twin for predictive maintenance · ZeMA hydraulic test rig, Saarbrücken

connecting show what the rig's log says

——

**TWIN**Waiting for the first cycle…

## The rig, as the twin sees it _—_

white: measured blue: the twin's model component outline: the twin's reading (green healthy, amber degraded, red failed)

## Component health _read from the sensors, no labels_

## Oil temperature: the last 90 minutes and the next hour _—_

—

TS1 measured thermal model forecast, as is forecast if the cooler failed now

## This cycle, live _measured against the model synced to the twin's reading_

measured model

**What this is.** The ZeMA rig's published recording (2205 cycles of 60 s, 36.75 h), replayed from the Wolfram Cloud one cycle a minute, as if it were running now. The clock decides which cycle is on screen, so everyone sees the same moment; the recording loops every 36.75 hours. Each cycle the twin reads the components' condition from the sensors alone: the pump leak from the flow the pump is missing against the System Modeler model at the measured oil temperature; the switching valve V10 from when the pressure falls after it opens; the accumulator from how fast the pressure rises when V10 shuts; the cooler from its cooling efficiency; the load valve V11 from the pressure after V10 against the model. The oil-temperature forecast comes from the thermal model, started from the measured state.  
**Honest limits.** The model runs for each cycle were computed beforehand with System Modeler; this page replays them with the measurements. It is a replay of a recorded run, not a live machine. One rig, emulated faults. Data: UCI ML Repository 447, Helwig, Pignanelli, Schütze (ZeMA), CC BY 4.0. Model: HydraulicSensing.ZeMARig and ZeMAThermal, Wolfram System Modeler 15.1 + Hydraulic library 3.0. Data: `www.wolframcloud.com/obj/ankitn/PumpTwin/chunks/`.

## 💡 Key Insights
- Demonstrates a live digital twin for predictive maintenance of a hydraulic test rig (ZeMA).
- Utilizes a hybrid modeling approach, combining sensor measurements with a System Modeler-based physics model.
- Provides real-time (emulated) health monitoring and condition assessment of individual hydraulic components (pump, valves, accumulator, cooler) based solely on sensor data.
- Features forecasting capabilities, such as oil temperature prediction, including scenarios for component failure (e.g., cooler failure).
- The system infers component degradation (e.g., pump leak, valve switching issues, cooler efficiency) by comparing measured values against the digital twin's model predictions.

## 📚 References
- PumpTwin · a live digital twin for predictive maintenance · ZeMA hydraulic test rig, Saarbrücken, systemsnotcode.com/labs/pumptwin/ *(source)*
- Data: UCI ML Repository 447, Helwig, Pignanelli, Schütze (ZeMA), CC BY 4.0. *(cited)*
- Model: HydraulicSensing.ZeMARig and ZeMAThermal, Wolfram System Modeler 15.1 + Hydraulic library 3.0. *(cited)*
- Data: www.wolframcloud.com/obj/ankitn/PumpTwin/chunks/ *(cited)*

## 🏷️ Classification
The content describes the application of a digital twin for predictive maintenance, involving hybrid modeling (System Modeler + sensor data) and forecasting, which aligns directly with the 'ML, stats, modélisation hybride, optimisation' aspects of Data Science.
