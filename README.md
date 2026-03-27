# 🏦 NitroBank: Automated Microcredit Pipeline


## Executive Summary
NitroBank is expanding its services across LATAM by introducing **Nitro Reserve**—contextual microcredit offerings in Brazil, Mexico, and Colombia. Initial analysis of over **145k regional transactions** revealed a massive opportunity: of the **15.3k declined transactions**, a staggering **89.2%** failed strictly due to Insufficient Funds. By bridging these liquidity gaps with real-time micro-loans, we transform moments of customer friction into loyalty-building events.

However, while reacting to checkout failures is highly profitable, scaling a true credit product requires evaluating the financial health of the *entire* customer base. To launch this responsibly, I engineered a **fully automated pipeline** and a **K-Means clustering model** to evaluate all **450k+** customers. This architecture delivers massive business impact: it safely isolates our vast "Prime" user base for proactive credit offers while mathematically filtering out over **330k** ghost accounts and high-risk profiles. Furthermore, the pipeline orchestrates its own reporting, delivering self-updating dashboards directly to the credit and product teams.


## Data Pipeline Architecture 
![NitroBank Pipeline Architecture](Images/Data_pipeline_architecture.png)

---


## Technical Implementation & Business Value

### Phase 1 & 2: Cross-Cloud Ingestion & Dockerized Automation
To ensure the ML model evaluates customers based on accurate, real-time economic conditions, the ingestion engine was packaged into a **Docker container deployed via Google Cloud Run**. 
* **Event-Driven Automation:** Orchestrated the end-to-end pipeline using Databricks Workflows, triggered immediately upon new `.parquet` data arriving in GCS.
* **Secure Cross-Cloud Integration:** Built a programmatic bridge extracting data from Google Cloud Storage into a Databricks environment without exposing sensitive credentials.
* **Data Integrity & Schema Validation:** Enforced strict API contracts using Pydantic, causing the pipeline to "fail fast" on invalid API payloads to prevent corrupted data from entering the bank's ecosystem.

### Phase 3: Distributed Feature Engineering (Silver Layer)
Raw transaction data was refined into a unified Machine Learning Feature Store, utilizing **Spark's distributed query engine** for high-speed processing.
* **Temporal Accuracy:** Applied deduplication logic to incoming FX payloads to ensure the ML model evaluates credit limits using only the **absolute latest daily exchange rates** (Row Number = 1), preventing stale data from affecting loan calculations.
* **Behavioral Trust Signals:** Transformed raw timestamps into actionable ML features to mathematically gauge user intent and platform reliance before offering credit.
* **Optimized Compute:** Replaced heavy conditional logic with high-performance PySpark filtering, drastically reducing the cluster compute costs required to process hundreds of thousands of rows.

### Phase 4: K-Means Clustering & Strategic Value (Gold Layer)
Relying solely on historical transaction declines leaves massive revenue on the table. I applied an unsupervised **K-Means model (k=4)** to segment the entire customer base, identifying both immediate recovery targets and high-value candidates for credit expansion.

* **Risk Mitigation (The Shield):** The algorithm successfully walled off high-risk profiles, protecting the bank's capital from:
    * **Tier 4: Watchlist (325,676 Ghost Accounts):** Effectively identifying dormant users.
    * **Tier 3: Watchlist (8,088 High Risk/Fraud):** Flagging suspicious behavioral patterns.
* **Credit Expansion (Prime Wallet):** The model unlocked **115,327 "Prime Wallet" users**. These are highly active "Whales" with healthy financial signals. Instead of waiting for a transaction failure, this segment is now targeted for proactive, higher-limit credit products.
* **Checkout Recovery (Nitro Reserve):** Pinpointed **1,533 "Nitro Reserve" candidates**. These users possess the highest intent but frequently hit "Liquidity Walls," making them the primary targets for instant, point-of-sale micro-loans.

### Phase 5: Production Orchestration & Delivery
Packaged the analytical models into a hands-off, production-grade data product.
* **Algorithmic Fairness:** Utilized scaling techniques within the pipeline to ensure that users with massive Total Payment Volumes did not mathematically overpower vital behavioral metrics, ensuring fair credit evaluation across all income brackets.
* **The NitroBank Reserve:** The final ML outputs feed directly into a production-ready Databricks dashboard that provides the product and credit teams with a daily, actionable VIP list of both Prime users and immediate Micro-Loan candidates.
