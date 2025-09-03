# 🏅 **Olympic-Data-Analytics-Azure-End-To-End-Data-Engineering-Project**

## 📌 **Overview**
This project demonstrates an **end-to-end data engineering pipeline on Microsoft Azure**, built around **Olympic Games datasets**.  

The solution ingests raw data, transforms it into structured formats, and enables advanced analytics and dashboarding.  

It follows a **modern data lakehouse architecture** using:  
- **Azure Data Factory**  
- **Azure Databricks**  
- **Azure Data Lake Storage Gen2**  
- **Azure Synapse Analytics**  
- **Power BI**  

---

## 🏗️ **Architecture**
<!-- Replace with your diagram path -->

### 🔹 **Data Source**
Olympic datasets (CSV files such as **Athletes, Coaches, Medals, Teams, EntriesGender**) are used as input.  

### 🔹 **Data Ingestion (Azure Data Factory)**
- Ingests raw CSV datasets from the source (e.g., GitHub or public repository).  
- Stores them in the **Raw Zone** of Azure Data Lake Storage Gen2.  

### 🔹 **Raw Data Store (ADLS Gen2)**
- Serves as the **Bronze Layer** in the medallion architecture.  
- Holds unprocessed, raw CSV files.  

### 🔹 **Transformation (Azure Databricks)**
- Performs **data cleaning** (missing values, schema fixes).  
- Applies **business logic transformations**.  
- Writes curated data to the **Transformed Zone (Silver/Gold layers)** in ADLS Gen2.  

### 🔹 **Transformed Data (ADLS Gen2)**
- Stores **Delta tables** ready for analytics.  
- Acts as the **single source of truth** for downstream consumption.  

### 🔹 **Analytics (Azure Synapse Analytics)**
- Connects to **transformed Delta tables** stored in ADLS Gen2.  
- Provides a **SQL analytics layer** for BI tools.  

### 🔹 **Dashboards (Power BI)**
- Visualizes Olympic data insights such as:  
  - **Medal tallies per country**  
  - **Gender distribution in events**  
  - **Athlete participation trends**  

---

## ⚙️ **Technologies Used**
- **Azure Data Factory (ADF)** → Data ingestion pipelines  
- **Azure Data Lake Storage Gen2 (ADLS)** → Raw & transformed zones  
- **Azure Databricks (Delta Lake)** → Cleaning & transformations  
- **Azure Synapse Analytics** → SQL analytics layer  
- **Power BI** → Interactive dashboards & reports  

---

## 🚀 **Getting Started**

### ✅ **Prerequisites**
- Azure subscription (**Free Trial** or **Pay-As-You-Go**)  
- Resource group with:  
  - **Data Factory**  
  - **Data Lake Storage Gen2**  
  - **Databricks Workspace**  
  - **Synapse Workspace**  
  - **Power BI Desktop** installed locally  

---

### ⚡ **Steps**

#### 1. **Ingest Data**
- Use **ADF pipelines** to copy raw CSVs from source (GitHub/raw link).  
- Store in **ADLS raw/** zone.  

#### 2. **Transform Data**
- Run **Databricks notebooks** to process raw data.  
- Save results in **Delta format** to ADLS **transformed/** zone.  

#### 3. **Analytics Layer**
- Connect **Synapse** to ADLS Delta tables.  
- Expose **views/tables** for reporting.  

#### 4. **Visualize Insights**
- Import **Synapse datasets** into Power BI.  
- Build **interactive dashboards**.  

---

## 📚 **References**
- [**Azure Data Factory Documentation**](https://learn.microsoft.com/en-us/azure/data-factory/)  
- [**Azure Databricks Documentation**](https://learn.microsoft.com/en-us/azure/databricks/)  
- [**Azure Synapse Analytics Documentation**](https://learn.microsoft.com/en-us/azure/synapse-analytics/)  
- [**Power BI Documentation**](https://learn.microsoft.com/en-us/power-bi/)  
