# 🏦 NitroBank: Automated Microcredit Pipeline


### The Business Opportunity
NitroBank is expanding its services across LATAM by introducing **Nitro Reserve**—contextual microcredit offerings in Brazil, Mexico, and Colombia. Initial analysis of over **145k regional transactions** revealed a massive opportunity: of the **15.3k declined transactions**, a staggering **89.2%** failed strictly due to **Insufficient Funds**. By bridging these liquidity gaps with real-time micro-loans, we transform moments of customer friction into loyalty-building events.

### The Strategic Challenge
While reacting to checkout failures is highly profitable, scaling a true enterprise credit product requires evaluating the financial health of the **entire** customer base, not just reacting to drop-offs.

### The Engineering Solution and Business Impact
To launch this responsibly, I engineered a **fully automated pipeline** and a **K-Means clustering model** to evaluate all **450k+ customers**.
This architecture safely isolates our vast **123k "Prime"** user base for proactive credit offers while mathematically filtering out over **313k ghost accounts** and high-risk profiles. Furthermore, the pipeline orchestrates its own reporting, delivering self-updating dashboards directly to the credit and product teams.


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

### Phase 4: K-Means Clustering & Business Value (Gold Layer)
Relying solely on historical transaction declines leaves massive revenue on the table. I applied an unsupervised **PySpark K-Means model (k=4)** to segment the entire 450k+ customer base, identifying both immediate recovery targets and high-value candidates for credit expansion. 

To prevent "label inversion" caused by the non-deterministic nature of K-Means (where arbitrary cluster IDs change on every run), I engineered a **Defensive SQL Profiling** step. By dynamically calculating the mathematical centroid of each cluster, the pipeline accurately mapped actual behavioral averages to business logic:

* **Risk Mitigation (The Shield):** The algorithm successfully walled off high-risk profiles, protecting the bank's capital from:
  * **Tier 4: Watchlist (~312k Ghost Accounts):** Zero financial footprint ($0 TPV); effectively identifying dormant users for re-engagement or deprecation.
  * **Tier 3: Watchlist (~1.5k High Risk/Fraud):** Flagging suspicious behavioral patterns (moving large volumes averaging $579 TPV, but with highly anomalous, slow Time-To-Value).
* **Credit Expansion (Prime Wallet):** The model unlocked **~123k "Prime Wallet" users**. Averaging $476 in volume with fast activation times, these are highly active "Whales" with healthy financial signals. Instead of waiting for a transaction failure, this segment is proactively targeted for higher-limit credit products.
* **Checkout Recovery (Nitro Reserve):** Pinpointed **~13.3k "Nitro Reserve" candidates**. Averaging small basket sizes (~$20 TPV) but exactly ~1.0 decline per user, these profiles possess the highest intent but frequently hit "Liquidity Walls," making them the primary targets for instant, point-of-sale micro-loans.

### Phase 5: Production Orchestration & Delivery
Packaged the analytical models and defensive SQL logic into a hands-off, production-grade data product.

* **Algorithmic Fairness:** Utilized scaling techniques within the pipeline to ensure that users with massive Total Payment Volumes did not mathematically overpower vital behavioral metrics (like decline velocity), ensuring fair credit evaluation across all income brackets.
* **Deterministic Automation:** The defensive SQL CTEs automatically re-evaluate the ML centroids after every daily run, guaranteeing that the business tier labels remain 100% accurate regardless of arbitrary algorithm state changes.
* **The NitroBank Reserve:** The final automated Gold Layer feeds directly into a production-ready Databricks dashboard, providing the product and credit teams with a daily, actionable VIP list of both Prime users and immediate Micro-Loan candidates.


### Challenges & Roadblocks

#### 1. Compute Bottlenecks & The Cartesian "Fan-Out" Bug
* **The Challenge:** Extracting user behavior features required joining our core `users` table with massive, high-velocity `transactions` and `events` tables.
* **The Roadblock:** Joining two separate 1-to-many tables simultaneously created a Cartesian multiplier effect (artificially inflating financial aggregates). Furthermore, running this heavy query dynamically for every ML iteration skyrocketed cloud compute costs.
* **The Solution:** I overhauled the SQL architecture using CTEs to pre-aggregate the tables individually, eliminating the fan-out bug. I then decoupled this process into a daily scheduled job that materializes the data into a static `user_ml_features` table, slashing ML compute costs and optimizing for enterprise scale.

#### 2. Cloud Identity & Security (IAM)
* **The Challenge:** Transitioning the pipeline from local development to a fully automated, secure Google Cloud deployment.
* **The Roadblock:** The default Cloud Run environment lacked the necessary identity tokens, resulting in immediate `PERMISSION_DENIED` errors when attempting to access Cloud Storage and trigger Databricks.
* **The Solution:** Conducted an IAM audit and implemented a custom GCP Service Account utilizing the **Principle of Least Privilege**. I also wrote hybrid authentication logic in Python to seamlessly switch between local developer keys and GCP's internal metadata service without hardcoding credentials.

#### 3. Unsupervised ML & Non-Deterministic Outputs (K-Means)
* **The Challenge:** Translating unsupervised machine learning mathematical outputs into actionable, real-world business tiers (e.g., "Prime", "High-Risk", "Micro-Loan Candidates").
* **The Roadblock:** K-Means cluster IDs (0, 1, 2, 3) are non-deterministic and arbitrary. Initially, I hardcoded my business logic directly to these IDs (`CASE WHEN prediction = 0 THEN 'Prime'`). Because the algorithm randomizes cluster starting points, this caused an inversion bug where "Ghost Accounts" were falsely flagged as high-value users.
* **The Solution:** Implemented SQL-based **Cluster Profiling** over the ML outputs to mathematically calculate the centroids of each group. By aggregating and analyzing the true averages (Avg TPV, decline velocity, time-to-value), I was able to accurately map the underlying behavioral data to the correct business definitions, eliminating prediction blindness.
