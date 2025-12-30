---
title: "OpenFloData: Real-Time Simulation & Streaming of Volve Oil & Gas Production Data for Data Engineering & Surveillance"
date: 2025-12-30
category: Data_Engineering
confidence: 0.95
tags: ['real-time streaming', 'production data', 'oil & gas', 'PostgreSQL', 'REST API', 'Docker', 'FastAPI', 'data pipeline', 'reservoir surveillance', 'data simulation', 'Volve dataset', 'decline curve analysis', 'productivity index', 'sector:petrochem']
source: "https://github.com/FloLabsAI/OpenFloData"
type: Article
source_type: Article
hash: 180116
---

### 🎯 Relevance
This project is highly valuable for industrial data scientists and process engineers looking to develop, test, or learn about real-time data pipelines and analytics for industrial applications, particularly in oil & gas. It provides a realistic, accessible environment to practice data engineering, build monitoring dashboards, and prototype data science models without needing access to live, sensitive production data. This accelerates learning and development cycles, reducing time-to-value for industrial data solutions.

### 📝 Summary
- **Key Message**: OpenFloData provides a real-time, clock-synchronized streaming simulation of oil & gas production data, addressing the lack of realistic data for prototyping and learning industrial data systems.
- **Data/Statistics**: Uses the Equinor Volve field dataset (2007-2016, daily resolution), synthetically upsampled to hourly intervals while preserving statistical distribution and physical constraints. Includes metrics like oil/gas/water rates, pressures, temperatures, choke settings.
- **Insights**: The project demonstrates a practical architecture for handling real-time industrial data streams using Docker, PostgreSQL, FastAPI, and Python, enabling realistic development and testing of monitoring and surveillance applications.
- **Actionable Takeaways**: Users can deploy a full-stack data streaming system locally with Docker Compose, access data via PostgreSQL or a REST API, and perform basic production surveillance (decline curve analysis, PI calculation) using provided SQL and Python examples.

### 📄 Extracted Content
One of the biggest challenges in learning, prototyping or building reservoir surveillance and production monitoring systems is the lack of access to realistic production data streams. OpenFloData addresses this gap by providing a simulated real-world system for oil & gas production monitoring. It demonstrates **Real-time data streaming** in PostgreSQL (and REST API) and **Clock-synchronized streaming** - streams historical data as if it's happening "now". OpenFloData creates a realistic simulation of a production monitoring system: Source Data (DuckDB) → Streaming Service → Time Synchronization → API Service (FastAPI REST API for querying the streaming data). Services: PostgreSQL (target DB), API Service (FastAPI REST API), Streamer Service (reads from DuckDB, writes to PostgreSQL, clock-synchronized streaming). Performs **Arps exponential decline curve analysis** to estimate decline parameters and remaining reserves. Calculates well **Productivity Index (PI)** from flowing bottomhole pressure (BHP) and production rates.

### 🏷️ Classification Reason
The content details the architecture, implementation, and usage of a data streaming and storage system for industrial production data, which directly falls under the scope of Data Engineering.
