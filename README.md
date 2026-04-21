# 🏦 NitroBank: Automated Microcredit Pipeline

[🌐 Click here to view the live Streamlit App](your-url-here)

#### Note: This is a comprehensive portfolio project utilizing a simulated enterprise dataset. The metrics, company names, and financial figures were constructed to demonstrate production-grade Analytics Engineering, Medallion Architecture, and business-focused data modeling.
### The Business Opportunity
NitroBank is expanding its services across LATAM by introducing **Nitro Reserve**—contextual microcredit offerings in Brazil, Mexico, and Colombia. Initial analysis of over **145k regional transactions** revealed a massive opportunity: of the **15.3k declined transactions**, a staggering **89.2%** failed strictly due to **Insufficient Funds**. By bridging these liquidity gaps with real-time micro-loans, we transform moments of customer friction into loyalty-building events.

### The Strategic Challenge
While reacting to checkout failures is highly profitable, scaling a true enterprise credit product requires evaluating the financial health of the **entire** customer base, not just reacting to drop-offs.

### The Engineering Solution and Business Impact
To enable safe, enterprise-scale credit expansion, I engineered a **fully automated pipeline** powered by **K-Means Clustering (an Unsupervised Machine Learning model)** to evaluate all **450k+ customers**. This enables the system to objectively segment the user base by evaluating multiple financial behaviors simultaneously, replacing the need for rigid, manual SQL rules.

This **Machine Learning-driven architecture** safely isolates our vast **123k "Prime"** user base for proactive credit offers while mathematically filtering out over **313k ghost accounts** and high-risk profiles. Furthermore, the pipeline orchestrates its own reporting, delivering self-updating dashboards directly to the credit and product teams, completely eliminating the manual toil of monthly risk assessments.
## Data Pipeline Architecture 
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

Raw transaction and event data were transformed into a materialized **Machine Learning Feature Store** using Spark SQL. Instead of feeding raw logs to the model, I pre-aggregated specific financial and behavioral KPIs to serve as objective inputs for the K-Means algorithm:
* **Dynamic FX Normalization (`total_payment_volume_usd`):** Applied deduplication logic to incoming FX payloads and joined point-in-time exchange rates. This ensures the ML model evaluates cross-border credit limits equitably, preventing stale data from skewing loan caps.
* **Risk vs. Liquidity Profiling (`insufficient_funds_count` & `high_risk_decline_count`):** Replaced heavy conditional logic with Spark's high-performance `COUNT_IF` function to strictly differentiate users who need micro-loans from those exhibiting fraudulent, high-risk decline patterns.
* **Behavioral Trust Signals (`time_to_value_hours`):** Transformed raw timestamps into a continuous metric measuring the hours between account creation and first successful payment. This acts as a mathematical proxy for user intent and platform reliance.
* **Algorithmic Fairness (Feature Scaling):** Applied strict mathematical scaling techniques before modeling to ensure users with massive transaction volumes did not geometrically overpower vital behavioral signals (like decline velocity), guaranteeing fair credit evaluation across all income brackets.

### Phase 4: K-Means Clustering & Business ROI (Gold Layer)
To translate raw data into direct financial impact, I deployed a distributed **PySpark K-Means model (k=4)** to autonomously segment the 450k+ customer base. By evaluating complex behavioral signals, the pipeline transformed the user base into a four-tiered strategy designed to maximize revenue generation while protecting bank capital:

* **Revenue Generation: Proactive Credit (Prime Wallet):** The model unlocked **~123k "Prime Wallet"** users. Averaging $476 in transaction volume with fast activation times, these highly active profiles represent the core profit engine. By proactively offering higher-limit credit products *before* a failure occurs, the business drives massive top-line growth and increased Customer Lifetime Value (LTV).
* **Immediate ROI: Checkout Recovery (Nitro Reserve):** Pinpointed **~13.3k "Nitro Reserve"** candidates. Averaging small basket sizes (~$20 TPV) but experiencing exactly ~1.0 decline per user, these profiles possess high intent but frequently hit "Liquidity Walls." Targeting them with instant, point-of-sale micro-loans directly recovers lost checkout revenue that would otherwise be permanently abandoned.
* **Capital Protection: Fraud & Risk Mitigation:** Safely walled off **~1.5k High-Risk** profiles. By flagging users attempting to move large volumes (averaging $579 TPV) but exhibiting anomalous, delayed Time-To-Value, the pipeline proactively shields the bank from high-impact fraud, defaults, and chargeback losses.
* **OpEx Reduction: Ghost Accounts:** Identified **~312k dormant users** with zero financial footprint ($0 TPV). Isolating these accounts allows the business to safely deprecate inactive cohorts, optimizing database compute costs and ensuring marketing spend is never wasted on non-viable users.

### Phase 5: Real-Time BI & Executive Serving Layer
* **Deployed a Real-Time BI Application:** Built an interactive serving layer using **Streamlit** and **Plotly** to democratize K-Means ML outputs for non-technical stakeholders.
* **Eliminated Data Silos:** Connected the application directly to **Databricks Delta Gold** tables, providing credit and product teams with a live visual pulse of portfolio tier distributions.
* **Operationalized ML Intelligence:** Engineered a real-time **Credit Advisor Simulator** that instantly evaluates new customer eligibility, bridging the gap between backend analytics and frontend business decisions.

### Challenges & Roadblocks

#### 1. Compute Bottlenecks & The Cartesian "Fan-Out"
* **The Challenge:** Joining our core `users` table with high-velocity `transactions` and `events` tables simultaneously created a Cartesian multiplier, inflating financial metrics and skyrocketing ML compute costs.
* **The Solution:** Refactored the SQL architecture using CTEs to pre-aggregate the tables individually. I decoupled this into a daily scheduled job that materializes a static `user_ml_features` table, eliminating the fan-out bug and slashing enterprise compute costs.

#### 2. Taming Non-Deterministic ML Outputs (K-Means)
* **The Challenge:** K-Means randomizes cluster starting points, causing arbitrary, shifting IDs (0, 1, 2, 3) that broke hardcoded business rules and falsely flagged "Ghost" accounts as "Prime" users.
* **The Solution:** Developed SQL-based **Cluster Profiling** to calculate true centroids post-prediction. By analyzing behavioral averages (Avg TPV, decline velocity), I dynamically mapped the arbitrary ML outputs to concrete business tiers, eliminating prediction blindness.

#### 3. Cloud Identity & Security (IAM)
* **The Challenge:** Transitioning to automated Google Cloud deployments caused immediate `PERMISSION_DENIED` errors when accessing storage or triggering Databricks due to default environment limits.
* **The Solution:** Deployed a custom GCP Service Account enforcing the **Principle of Least Privilege**. Engineered Python hybrid-auth logic to seamlessly toggle between local developer keys and GCP's metadata service without hardcoding credentials.

