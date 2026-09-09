# Financial Governance & Hardware Development Fund Ledger – Sad Sausage (SS-Ops)

This document establishes the formal financial governance, public audit log, and procurement verification protocol for the **Sad Sausage (SS-Ops)** open-source project.

---

## 🏛️ Governance & Co-Investment Policy

1. **Maintainer Co-Investment (30% Eigenanteil):**  
   To demonstrate genuine skin-in-the-game and long-term commitment, **the project maintainer co-invests 30% of all hardware procurement costs from personal funds**. Community sponsorship covers the remaining 70%.
2. **Dedicated Capital Deployment:**  
   100% of community sponsorship funds are allocated strictly to hardware components specified in the itemized roadmap. No funds are diverted to administrative overhead.
3. **Public Auditability & Transparency:**  
   Every contribution, disbursement, and hardware invoice is publicly reconciled in this ledger in Euros (€).
4. **Mandatory Milestone Verification:**  
   Upon reaching each funding milestone, the project maintainer publishes:
   - **Proof of Purchase:** Sanitized merchant invoices and payment receipts.
   - **Hardware Integration:** High-resolution photographs of unboxing, motherboard installation, and cabling.
   - **Reproducible Benchmarks:** Public test outputs measuring inference throughput (tokens/second), maximum sustainable context window without truncation, and power efficiency (Watts/token).

---

## 📊 Summary & Active Funding Status

* **Active Objective:** Tier 1 – Modern Workstation Host Platform
  * **Total Hardware Procurement Cost:** 680,00 €
  * **Maintainer Personal Share (30%):** 204,00 €
  * **Community Sponsorship Target (70%):** **476,00 €**
* **Total Community Capital Raised:** 0,00 € (0 Contributions received)
* **Maintainer Co-Investment Disbursed:** 0,00 € (Triggered upon milestone funding)
* **Official Sponsorship Channel:**  
  👉 [https://buymeacoffee.com/klythoni](https://buymeacoffee.com/klythoni)

---

## 📦 Itemized Hardware Milestones & Co-Investment Breakdown

| Tier | Component Target | Total Cost (€) | Maintainer (30%) | Community Goal (70%) | Verification Deliverables | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | Modern AM5 CPU + Multi-PCIe Motherboard + 64GB DDR5 RAM + 2TB PCIe 4.0 NVMe SSD + 750W Gold PSU | 680 € | 204 € | **476 €** | Host OS swap latency benchmarks; vector database indexing throughput | ⏳ Active Funding |
| **Tier 2** | Dedicated 24GB Compute Accelerator (Used NVIDIA GeForce RTX 3090 / equivalent) + Thermal Pads | 880 € | 264 € | **616 €** | 32k token context retention benchmark; tokens/sec inference comparison | ⏳ Planned |
| **Tier 3** | Secondary 24GB GPU + 1200W Titanium PSU + Dual-GPU Airflow Chassis & PCIe 4.0 Riser | 1.260 € | 378 € | **882 €** | Dual-GPU tensor parallelism benchmark; 70B parameter inference logs | ⏳ Planned |

---

## 📜 Contributions & Audit Log

| Timestamp | Contributor / Reference | Amount (€ / Units) | Allocated Objective | Verification / Status |
| :--- | :--- | :--- | :--- | :--- |
| *2026-09-09* | *Repository Initialization* | 0,00 € | Project Launch | Public GitHub Release |

*(All sponsorship contributions received via Buy Me a Coffee are audited, reconciled in EUR (€), and matched with the maintainer's 30% co-investment).*

---

## 🛠️ Benchmark & Verification Log

*When a funding milestone is achieved and hardware is commissioned, empirical evaluation records will be appended to this section.*

### Verification Protocol
1. **Inference Latency & Throughput:**  
   Measured using `llama.cpp` / `vLLM` on representative open-weight models (Llama 3.1 8B, Qwen 2.5 14B/32B).
2. **Context Window Stability Test:**  
   Evaluated with multi-turn needle-in-a-haystack log extraction over 8k, 16k, 32k, and 64k token spans.
3. **Continuous Load & Thermal Metrics:**  
   Measured across 24-hour continuous Home Assistant event ingestion under simulated fault bursts.
