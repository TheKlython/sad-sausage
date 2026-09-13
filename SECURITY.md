# Security Policy

## Security by Design Principles

The **Sad Sausage (SS-Ops)** project and its showcased hardware integrations (such as `Gasmeter_ESP`) are engineered around strict **Security by Design** principles:

1. **Local-First & Zero Cloud Dependency:** All components operate strictly within the user's local network (LAN) without required telemetry upload, analytics pingbacks, or third-party cloud routing.
2. **Encrypted Communication:** Native Home Assistant API integrations enforce modern Noise PSK encryption (`api_encryption_key`).
3. **Protected Firmware Updates:** Over-the-Air (OTA) updates require individual cryptographic passwords (`ota_password`).
4. **Credential Isolation:** Real credentials and local network details must never be committed to source control; only sanitized `.example` templates are tracked.
5. **Path Traversal & Injection Guards:** All management tools, MCP functions, and validators validate and sanitize input paths, URLs, and schemas.

---

## Supported Versions

Only the latest release on the `main` branch is actively supported with security patches.

| Component / Subproject | Supported | Notes |
| :--- | :--- | :--- |
| **Sad Sausage Core / MCP** | :white_check_mark: | Latest `main` branch |
| **Gasmeter_ESP** | :white_check_mark: | Latest release |

---

## Reporting a Vulnerability

We take the security of this project, its operators, and the community seriously. If you discover a security vulnerability or potential credential leak:

### 1. Private Vulnerability Reporting (Preferred)
Please report security issues privately via GitHub's **Private Vulnerability Reporting**:
1. Navigate to the repository's **Security** tab.
2. Click **Advisories** -> **Report a vulnerability**.
3. Provide detailed steps to reproduce the issue, along with any potential impact analysis.

### 2. Direct Security Contact
If you cannot use GitHub Advisories, please submit your findings to the maintainer via the GitHub profile contact or an encrypted communication channel.

> [!CAUTION]
> **Please do NOT open a public GitHub Issue** for security vulnerabilities, zero-day exploits, or accidental credential discoveries until an advisory and fix have been coordinated.

---

## Disclosure & Remediation Process
1. **Acknowledgement:** We will acknowledge receipt of your vulnerability report within 48 hours.
2. **Investigation:** We will verify and investigate the reported vulnerability in an isolated staging environment.
3. **Patch & Release:** A fix will be developed, tested against our automated test suites, and committed.
4. **Public Advisory:** A security advisory with credit to the reporter will be published once the patch is live.
