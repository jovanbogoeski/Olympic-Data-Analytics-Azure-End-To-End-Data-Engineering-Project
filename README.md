🏅 Olympic-Data-Analytics-Azure-End-To-End-Data-Engineering-Project
📌 Overview

This project demonstrates an end-to-end data engineering pipeline on Microsoft Azure using Olympic Games datasets.
Raw CSVs are ingested, transformed into Delta tables, and served for analytics and dashboards following a modern lakehouse design.

It uses:
Azure Data Factory · Azure Databricks · Azure Data Lake Storage Gen2 · Azure Synapse Analytics · Power BI

🔹 Data Source

CSV datasets (e.g., Athletes, Coaches, Medals, Teams, EntriesGender).

🔹 Data Ingestion (Azure Data Factory)

Copy raw CSVs from source (e.g., GitHub) into ADLS Gen2 → raw/ zone.

🔹 Raw Data Store (ADLS Gen2)

Bronze layer holding unprocessed CSV files.

🔹 Transformation (Azure Databricks)

Clean data, apply business rules, and write Delta outputs to ADLS → transformed/ (Silver/Gold).

🔹 Transformed Data (ADLS Gen2)

Curated Delta tables as the single source of truth.

🔹 Analytics (Azure Synapse Analytics)

Query Delta directly (serverless SQL via OPENROWSET ... FORMAT='DELTA') and expose views for BI.

🔹 Dashboards (Power BI)

Build visuals such as medal tallies, gender distribution, and athlete participation.

⚙️ Technologies Used

Azure Data Factory (ADF) – ingestion

Azure Data Lake Storage Gen2 (ADLS) – raw & transformed zones

Azure Databricks (Delta Lake) – cleaning & transforms

Azure Synapse Analytics (serverless SQL) – analytics layer

Power BI – dashboards & reporting

🚀 Getting Started
✅ Prerequisites

Azure subscription (Free Trial or Pay-As-You-Go)

Resource group with: ADF, ADLS Gen2, Databricks, Synapse, and Power BI Desktop

⚡ Steps

Ingest Data
Use ADF to copy CSVs to ADLS raw/.

Transform Data
Run Databricks notebooks; write Delta to ADLS transformed/.

Analytics Layer
In Synapse (serverless), create views over Delta (via OPENROWSET ... FORMAT='DELTA').

Visualize Insights
Connect Power BI to Synapse views and build dashboards.

📚 References

Azure Data Factory

Azure Databricks

Azure Synapse Analytics

Power BI
