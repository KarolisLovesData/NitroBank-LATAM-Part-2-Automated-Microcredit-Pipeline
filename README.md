# 🏦 NitroBank: Automated Microcredit Pipeline

## 📌 Project Overview
As NitroBank expands its microcredit offerings across LATAM, financial integrity is paramount. This project replaces a manual SQL-based currency reconciliation process with a fully automated, cloud-native data pipeline. 

By orchestrating the ingestion of daily exchange rates, enforcing strict data contracts, and leveraging a Medallion Architecture, this pipeline ensures downstream K-Means clustering models are fed with audit-grade, chronologically accurate financial data.

## 🏗️ Architecture Flow
*(Note: GitHub natively supports this Mermaid diagram)*

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "darkMode": true,
    "background": "#0B0D17",
    "primaryColor": "#5D3FD3",
    "primaryTextColor": "#E0B0FF",
    "lineColor": "#00F5FF",
    "secondaryColor": "#FF3366",
    "tertiaryColor": "#0B0D17"
  }
}}%%
graph LR
    A[Exchange API] -->|Python| B(Docker Ingestion)
    B -->|Parquet| C[(Google Cloud Storage)]
    C -->|Trigger| D{Databricks Engine}
    
    subgraph Databricks_Logic [Processing Layer]
    D --> D1[SQL Feature Engineering]
    D1 --> D2[K-Means Clustering]
    end
    
    D2 -->|Identified Leads| E[Stakeholder Email]

    %% Styling
    style B fill:#5D3FD3,stroke:#00F5FF,stroke-width:2px
    style D fill:#00F5FF,stroke:#5D3FD3,color:#0B0D17
    style E fill:#FF3366,stroke:#E0B0FF,stroke-width:2px
