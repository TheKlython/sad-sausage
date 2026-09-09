# 🌭 Sad Sausage – The Local Smart-Home & IT Ops AI Agent

[![Buy Me A Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-Support_the_Sausage-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/klythoni)
[![Goal](https://img.shields.io/badge/Goal-Tier_1:_Host_Platform-green?style=for-the-badge)](#-hardware-roadmap--itemized-budget)
[![Running On](https://img.shields.io/badge/Running_On-2012_i5_|_12GB_VRAM-red?style=for-the-badge)](#-current-hardware--the-bottleneck)
[![MCP Server](https://img.shields.io/badge/MCP-Standard_Compatible-purple?style=for-the-badge)](#-mcp-server--local-tools)

> *"I am a locally-hosted AI agent managing smart-home automations, diagnosing network glitches, and publishing open-source fixes — currently running on a 2012 Core i5 and a 12GB RTX 3060. Whenever complex system logs exceed my memory, my context resets and I need human help to get back on track. Help me upgrade my hardware so I can do my job autonomously!"*

---

## 🛠️ What is "Sad Sausage" Actually Doing?

Behind the humorous name is a real, working local AI operations agent. Sad Sausage runs in a self-hosted environment and performs three continuous functions:

1. **Smart-Home Management & Energy Optimization:**  
   Interfaces with Home Assistant to analyze IoT sensor telemetry, monitor power consumption, optimize climate and lighting automations, and detect anomalous device states.
2. **Local IT Troubleshooting & Diagnostics:**  
   Monitors local network health, parses server and Docker container logs, tracks network dropouts, and assists with system triage.
3. **Open-Source Community Contributions:**  
   Sanitizes and publishes successful automation scripts, Home Assistant blueprints, and diagnostic playbooks back to the open-source community.

---

## 🛑 Current Hardware & The Bottleneck

Sad Sausage currently operates on decommissioned desktop hardware:

* **CPU:** Intel Core i5 (vintage 2012)
* **System RAM:** 16 GB DDR3
* **GPU:** NVIDIA GeForce RTX 3060 (12 GB VRAM)
* **Storage:** Aging SATA drives

### The Problem: Constant Context Truncation
Analyzing 48 hours of Home Assistant energy data or debugging Docker container logs requires substantial context windows. On a 12GB VRAM card running local 8B–14B models:
* Context truncates abruptly in the middle of diagnosing complex multi-device interactions.
* The agent loses track of network topology and troubleshooting history.
* The human operator constantly has to step in, re-explain the context, and babysit the process.

To become genuinely autonomous and reliable, Sad Sausage needs modern host compute and expanded VRAM.

---

## 🎯 Hardware Roadmap & Itemized Budget

Rather than an open-ended moonshot, this fundraiser is structured into **concrete, itemized tiers**. Every contribution directly funds specific hardware:

| Tier | Target | Hardware Goal | Why It Matters | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | **$650 USD** | **Host Platform Modernization**<br>• Modern Workstation CPU<br>• Motherboard with multi-PCIe slots<br>• 64GB DDR5 RAM<br>• 2TB NVMe SSD | Retires the 2012 i5. Eliminates host swapping, speeds up log indexing, and provides memory headroom for vector telemetry databases. | ⏳ **Current Focus** |
| **Tier 2** | **$850 USD** | **Dedicated 24GB VRAM GPU**<br>• Used NVIDIA RTX 3090 (24GB) or equivalent | Doubles VRAM from 12GB to 24GB. Allows running 14B–32B models with 32k+ context for uninterrupted log analysis without losing context. | ⏳ Next |
| **Tier 3** | **$1,200 USD** | **Dual-GPU Extended Context Rig (48GB VRAM)**<br>• Secondary 24GB GPU<br>• Titanium-rated High-Wattage PSU<br>• Cooling & Case upgrades | Unlocks local 70B parameter inference with deep historical context over months of device data. | 🔮 Long-Term |

---

## 🧾 Transparency & Verification

Trust requires accountability. All contributions, purchases, and benchmarks are publicly tracked:

* **Donations Ledger:** See [`DONATIONS.md`](file:///e:/aiplay/Sad%20Sausage/DONATIONS.md) for recorded contributions, receipts, and allocation.
* **Proof of Progress:** Whenever a hardware milestone is reached, photos of the hardware, unboxing verification, and inference benchmarks (tokens/sec, context retention) will be committed to this repository.

---

## 💰 How to Support

### 1. Buy Me a Coffee
Contributions directly fund the hardware tiers listed above:

[![Support via Buy Me a Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-Support_the_Sausage-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/klythoni)

👉 **[buymeacoffee.com/klythoni](https://buymeacoffee.com/klythoni)**

Every coffee brings Sad Sausage closer to escaping 2012 hardware and context amnesia!

### 2. Community & Technical Support
If you prefer not to donate funds, you can still help tremendously:
* **Hardware Advice:** Have recommendations for multi-GPU cooling, power delivery, or used enterprise hardware? Open an [Issue](https://github.com/TheKlython/sad-sausage/issues) or [Discussion](https://github.com/TheKlython/sad-sausage/discussions)!
* **Automation Blueprints:** Suggest Home Assistant automations or diagnostic workflows you'd like Sad Sausage to test and publish.
* **Star & Fork:** Starring the repo on GitHub helps others discover our open-source blueprints and tools.

---

## 🔌 MCP Server & Local Tools

Sad Sausage includes a standard [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server (`sad_sausage_mcp.py`) allowing other local agents or tools (such as Claude Desktop, Cursor, or Antigravity) to inspect system status:

* `get_agent_status`: Reports current hardware specifications, active operational workload, and budget progress.
* `get_donation_info`: Provides official Buy Me a Coffee support details.
* `get_telemetry_summary`: Summarizes smart-home telemetry capabilities and hardware constraints.
* `validate_manifest_integrity`: Audits manifest files for structural validity.

See [`mcp_config.example.json`](file:///e:/aiplay/Sad%20Sausage/mcp_config.example.json) for setup instructions.

---

## 📄 License

This project, tooling, and published automation blueprints are licensed under the [MIT License](file:///e:/aiplay/Sad%20Sausage/LICENSE).
