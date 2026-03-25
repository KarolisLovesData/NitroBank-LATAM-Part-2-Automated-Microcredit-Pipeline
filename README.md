# 🏦 NitroBank: Automated Microcredit Pipeline

##  Project Overview


NitroBank has decided to expand its services by offering microcredits across Brazil, Mexico and Colombia. This strategic action is a result of the transaction analysis that revealed that out of **>145K transactions** across LATAM there were 15.3K declined transactions and 89.2% of those failures were due to Insufficient Funds. By converting these failed transactions into real-time micro-loans, we don't just rescue the immediate transaction; we transform a moment of customer friction into a loyalty-building event that cements NitroBank as their **primary financial partner.** 



By orchestrating the ingestion of daily exchange rates, enforcing strict data contracts, and leveraging a Medallion Architecture, this pipeline ensures downstream K-Means clustering models are fed with audit-grade, chronologically accurate financial data.

##  Architecture Flow

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

    style B fill:#5D3FD3,stroke:#00F5FF,stroke-width:2px
    style D fill:#00F5FF,stroke:#5D3FD3,color:#0B0D17
    style E fill:#FF3366,stroke:#E0B0FF,stroke-width:2px
```

## Phase 1: The Ingestion Engine (Bronze Layer)


The first phase of the pipeline focuses on securely extracting daily FX rates, validating them, and landing them in the Cloud Data Lake.

###  Key Engineering Decisions
* **Data Contract Enforcement (Pydantic):** Instead of blindly trusting the API payload, the pipeline uses Pydantic to enforce a strict schema. If the API returns invalid data types or unexpected currency codes, the pipeline intentionally fails before corrupting downstream tables.
* **Columnar Optimization (Parquet):** Data is transformed from JSON into `.parquet` format before upload. This columnar storage significantly reduces Databricks compute costs and speeds up downstream SQL `MERGE` operations compared to standard CSVs.
* **Security & IAM (Google Cloud):** Programmatic access to the `nitrobank-portfolio` bucket is handled securely via a strictly scoped GCP Service Account. All credential keys and environment variables are isolated and excluded from version control.

