**NOTE:** This is a comprehensive portfolio project utilizing a simulated enterprise dataset. The metrics, company names, and financial figures were constructed to demonstrate production-grade Analytics Engineering, Medallion Architecture, and business-focused data modeling.
# 🏦 NitroBank: Automated Microcredit Pipeline

[🌐 Click here to view the live Streamlit App](your-url-here)


### The Business Opportunity
NitroBank is expanding its services across LATAM by introducing **Nitro Reserve**—contextual microcredit offerings in Brazil, Mexico, and Colombia. Initial analysis of over **145k regional transactions** revealed a massive opportunity: of the **15.3k declined transactions**, a staggering **89.2%** failed strictly due to **Insufficient Funds**. By bridging these liquidity gaps with real-time micro-loans, we transform moments of customer friction into loyalty-building events.

### The Strategic Challenge
While reacting to checkout failures is highly profitable, scaling a true enterprise credit product requires evaluating the financial health of the **entire** customer base, not just reacting to drop-offs.

### The Engineering Solution and Business Impact
To enable safe, enterprise-scale credit expansion, I engineered a **fully automated Medallion data pipeline** to evaluate all **450k+ customers**. By processing over **1.62 million raw web events**, the pipeline feeds clean, point-in-time financial features into an unsupervised **K-Means Machine Learning model**. This enables the system to objectively segment the user base by evaluating multiple financial behaviors simultaneously, replacing the need for rigid, manual SQL rules.

This **Machine Learning-driven architecture** safely isolates our top **~124k High-Value users** (spanning both 'Prime' and 'Apex' tiers) for proactive credit offers, while mathematically filtering out over **313k ghost accounts** and protecting against anomalous high-risk profiles. Furthermore, the pipeline orchestrates its own reporting, delivering self-updating dashboards directly to the credit and product teams, completely **eliminating the manual toil** of risk assessments.

---
### Phase 4: K-Means Clustering & Business ROI (Gold Layer)
Deployed a distributed **PySpark K-Means model** to autonomously segment the 450k+ customer base. Because unsupervised ML outputs non-deterministic cluster IDs that can shift between runs, I engineered a deterministic SQL profiling layer using dynamic centroid evaluation. This automatically translates the ML clusters into **five stable, business-ready product tiers** designed to maximize revenue while protecting bank capital:

*   **Tier 1: Apex Wallet (Whales & VIPs) | ~56.6k Users**
    *   **Profile:** High-volume spenders mathematically isolated by an average Total Payment Volume (TPV) of $500+.
    *   **Business ROI:** Maximizes Customer Lifetime Value (LTV) by proactively unlocking premium, high-limit credit lines for the platform's most lucrative demographic before they look to competitors.
*   **Prime Wallet (Healthy Base) | ~67.4k Users**
    *   **Profile:** The reliable, standard-spend user base captured safely beneath the Apex threshold but above the high-risk guardrails. 
    *   **Business ROI:** Serves as the core profit engine for standard credit offerings, driving consistent, predictable transaction volume and top-line growth.
*   **Tier 2: Nitro Reserve (Micro-Loan Candidates) | ~13.4k Users**
    *   **Profile:** High-intent users hitting "liquidity walls," identified by a high decline-to-transaction ratio (averaging >= 0.5 declines).
    *   **Business ROI:** Deploying instant, point-of-sale micro-loans to this specific cohort directly recovers abandoned checkout revenue and bridges temporary liquidity gaps.
*   **Tier 3: Watchlist (High Risk/Fraud) | Future-Proofing Guardrail**
    *   **Profile:** A protective trap designed to catch anomalous, slow-moving accounts (Time-to-Value > 150 hours) that suddenly spike in volume.
    *   **Business ROI:** Capital protection. Ensuring these accounts do not slip into the Prime or Apex tiers shields the bank from high-impact fraud, organized defaults, and chargebacks.
*   **Tier 4: Watchlist (Ghost Accounts) | ~313.1k Users**
    *   **Profile:** Dormant users with an absolute zero financial footprint ($0 TPV).
    *   **Business ROI:** OpEx reduction. Deprecating these massive, inactive cohorts optimizes downstream database compute costs and eliminates wasted targeted marketing spend.
![NitroBank Pipeline Architecture](Images/Data_pipeline_architecture.png)

---


## Technical Implementation & Business Value

### Phase 1 & 2: Automated Cross-Cloud Ingestion Pipeline
To ensure the ML model evaluates customers based on up-to-date economic conditions, I architected a decoupled, two-stage ingestion pipeline bridging Google Cloud and Databricks.
* **Scheduled Containerized Ingestion:** Utilized **GCP Cloud Scheduler** to trigger a **Dockerized Google Cloud Run** instance, routinely fetching and writing fresh financial payloads to Cloud Storage as compressed `.parquet` files.
* **Event-Driven Orchestration:** Built a Python-triggered job that automatically wakes the **Databricks Engine** the moment new Parquet data arrives in GCS, ensuring seamless cross-cloud integration with zero idle compute time.
* **Data Integrity & Schema Validation:** Enforced strict API contracts at the Cloud Run layer using **Pydantic**, causing the ingestion to "fail fast" on invalid payloads before they could enter the downstream Databricks environment.

### Phase 3: Distributed Feature Engineering & ML Store (Silver Layer)

<img src="Images/data_lineage_graph.png" width="700">

To provide the PySpark K-Means algorithm with clean, one-row-per-user inputs, I pre-aggregated key financial and behavioral KPIs using SQL. 

* **Dynamic FX Normalization (`total_payment_volume_usd`):** Deduplicated incoming FX payloads and joined point-in-time exchange rates. This prevents stale data from skewing loan caps and ensures cross-border credit is evaluated equitably.
* **Risk vs. Liquidity Profiling (`insufficient_funds_count` & `high_risk_decline_count`):** Utilized Databricks high-performance `COUNT_IF` to efficiently separate users who need liquidity bridging from those exhibiting fraudulent decline patterns.
* **Behavioral Trust Signals (`time_to_value_hours`):** Converted raw timestamps into a continuous metric (hours from account creation to first payment) to mathematically proxy user intent and platform reliance.
* **Algorithmic Fairness (Feature Scaling):** Scaled inputs before modeling so massive transaction volumes couldn't geometrically overpower nuanced behavioral signals (like decline velocity), guaranteeing fair credit evaluation across all income brackets.

### Phase 4: K-Means Clustering & Business ROI (Gold Layer)
Deployed a distributed **PySpark K-Means model (k=4)** to autonomously segment the 450k+ customer base. By evaluating complex behavioral signals, the pipeline transformed the user base into a **four-tiered** strategy designed to maximize revenue generation while protecting bank capital:

* **Revenue Generation (Prime Wallet):** Unlocked **~123k** highly active users averaging $476 TPV. Proactively offering this core profit engine higher-limit credit *before* a failure occurs drives massive top-line growth and Customer Lifetime Value (LTV).
* **Immediate ROI (Nitro Reserve):** Pinpointed **~13.3k** high-intent users hitting "liquidity walls" (~$20 TPV, ~1.0 decline/user). Deploying instant, point-of-sale micro-loans to this cohort directly recovers abandoned checkout revenue.
* **Capital Protection (High-Risk):** Isolated **~1.5k** profiles attempting large transfers (averaging $579 TPV) with anomalous, delayed Time-To-Value metrics. Proactively flagging these accounts shields the bank from high-impact fraud, defaults, and chargebacks.
* **OpEx Reduction (Ghost Accounts):** Identified **~312k** dormant users with zero financial footprint ($0 TPV). Deprecating these inactive cohorts optimizes database compute costs and eliminates wasted marketing spend.

### Phase 5: Real-Time BI & Executive Serving Layer
* **Deployed a Real-Time BI Application:** Built an interactive serving layer using **Streamlit** and **Plotly** to democratize K-Means ML outputs for non-technical stakeholders.
* **Eliminated Data Silos:** Connected the application directly to **Databricks Delta Gold** tables, providing credit and product teams with a live visual pulse of portfolio tier distributions.
* **Operationalized ML Intelligence:** Engineered a real-time **Credit Advisor Simulator** that instantly evaluates new customer eligibility, bridging the gap between backend analytics and frontend business decisions.




### Challenges & Roadblocks

#### 1. Translating Non-Deterministic ML Outputs into Business Logic
* **The Challenge:** Unsupervised K-Means outputs arbitrary, non-deterministic cluster IDs (0, 1, 2) that shuffle between runs, breaking downstream BI dashboards and automated credit logic.
* **The Solution:** Engineered a dynamic SQL profiling step in the Gold Layer to calculate the mathematical centroid of each cluster (Avg TPV, declines, TTV). By evaluating these centroids against business guardrails using `CASE WHEN` logic, the pipeline automatically translates random ML outputs into deterministic, stable labels (e.g., "Prime Wallet") for the reporting layer.

#### 2. Mitigating Economic Volatility in Credit Risk Models

* **The Challenge (Business Risk):** Operating in LATAM requires managing rapid **macroeconomic volatility**. Because the current clustering model evaluates users on absolute **Total Payment Volume (TPV)**, a sudden inflation spike artificially inflates nominal spend. This **concept drift** risks incorrectly promoting standard users to the **"Prime" credit tier**, exposing the bank to **underpriced credit risk** and capital loss.
* **Proposed Architectural Update:** To protect bank capital, I propose integrating a **rolling 30-day macroeconomic index** directly into the **Silver Layer**. By **normalizing absolute TPV** against this index *before* it reaches the ML algorithms or BI dashboards, the segmentation will dynamically adapt to market realities. This ensures the model maintains **accurate risk profiles** and prevents drift, regardless of economic turbulence.

#### 3. Compute Bottlenecks & The Cartesian "Fan-Out"
* **The Challenge:** Joining our core `users` table with high-velocity `transactions` and `events` tables simultaneously created a Cartesian multiplier, inflating financial metrics and skyrocketing ML compute costs.
* **The Solution:** Refactored the SQL architecture using CTEs to pre-aggregate the tables individually. I decoupled this into a daily scheduled job that materializes a static `user_ml_features` table, eliminating the fan-out bug and slashing enterprise compute costs.



