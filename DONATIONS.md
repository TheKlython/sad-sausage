# Financial Governance & Hardware Development Fund Ledger – Sad Sausage (SS-Ops)

This document establishes the formal financial governance, public audit log, and procurement verification protocol for the **Sad Sausage (SS-Ops)** open-source project.

---

## 🏛️ Governance & Transparency Policy

1. **Dedicated Capital Deployment:**  
   100% of community sponsorship funds are allocated directly to hardware components outlined in the itemized development roadmap. No funds are diverted to administrative or proprietary expenses.
2. **Public Auditability:**  
   Every contribution, disbursement, and hardware procurement is publicly logged in this document.
3. **Mandatory Milestone Verification:**  
   Upon reaching each funding milestone, the project maintainer is obligated to publish:
   - **Proof of Purchase:** Sanitized merchant invoices and payment confirmations.
   - **Hardware Integration Documentation:** Photographs of unboxing, chassis installation, and cabling.
   - **Reproducible Benchmarks:** Public test outputs measuring inference throughput (tokens/second), maximum sustainable context window without degradation, and energy efficiency (Watts/token).

---

## 📊 Summary & Active Funding Status

* **Active Objective:** Tier 1 – Modern Workstation Host Platform ($650 USD)
* **Total Capital Raised:** $0.00 USD (0 Contributions received)
* **Capital Disbursed to Date:** $0.00 USD
* **Official Sponsorship Channel:**  
  👉 [https://buymeacoffee.com/klythoni](https://buymeacoffee.com/klythoni)

---

## 📦 Itemized Hardware Milestones

| Tier | Component Target | Budget (USD) | Verification Deliverables | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | Modern Workstation CPU + Multi-PCIe Motherboard + 64GB DDR5 RAM + 2TB PCIe 4.0 NVMe SSD | ~$650 USD | Host OS swap latency benchmarks; vector database indexing throughput | ⏳ Active Funding |
| **Tier 2** | Dedicated 24GB Compute Accelerator (Used NVIDIA RTX 3090 / equivalent) | ~$850 USD | 32k token context retention benchmark; tokens/sec inference comparison | ⏳ Planned |
| **Tier 3** | Secondary 24GB GPU + Titanium High-Wattage PSU + Thermal Enclosure | ~$1,200 USD | Dual-GPU tensor parallelism benchmark; 70B parameter inference logs | ⏳ Planned |

---

## 📜 Contributions & Audit Log

| Timestamp | Contributor / Reference | Amount (USD / Units) | Allocated Objective | Verification / Status |
| :--- | :--- | :--- | :--- | :--- |
| *2026-09-09* | *Repository Initialization* | $0.00 USD | Project Launch | Public GitHub Release |

*(All sponsorship contributions received via Buy Me a Coffee are audited, converted to net USD, and reconciled in this ledger).*

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
