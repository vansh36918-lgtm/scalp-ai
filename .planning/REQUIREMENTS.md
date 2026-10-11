# Requirements Specification

## Functional Requirements

- **[REQ-01] Multi-Class Scalp Pathology Classification**:
  - The model must identify 15 distinct classes: `alopecia_areata`, `androgenetic_alopecia`, `contact_dermatitis`, `dandruff`, `folliculitis`, `folliculitis_decalvans`, `lichen_planopilaris`, `normal_healthy_scalp`, `pediculosis_capitis`, `psoriasis`, `seborrheic_dermatitis`, `telogen_effluvium`, `tinea_capitis`, `traction_alopecia`, and `trichotillomania`.
  - Priority: High | Status: Implemented (92.67% unseen accuracy)

- **[REQ-02] Scalp Domain Rejection Guard**:
  - The system must verify human skin and hair presence and reject non-scalp images (documents, screenshots, anime, wallpapers, and clinical non-biological drapes) with an explicit warning and 0% confidence.
  - Priority: High | Status: Implemented

- **[REQ-03] Objective Trichometry Metrics**:
  - Quantify flakiness percentage (desquamation index), erythema percentage (inflammation index), and scalp exposure percentage (hair density index), along with a composite Scalp Health Score (0–100).
  - Priority: High | Status: Implemented

- **[REQ-04] Specular Flash Glare Filtering**:
  - Detect and subtract camera flash reflections off sebum/sweat (\(R > 235, G > 220, B > 210\)) to prevent overexposed highlights from triggering false erythema on healthy scalps.
  - Priority: High | Status: Implemented

- **[REQ-05] Explainable AI (Grad-CAM Heatmaps)**:
  - Generate visual saliency heatmaps overlaid on the input image showing the convolutional activation regions responsible for the diagnosis.
  - Priority: High | Status: Implemented

- **[REQ-06] Clinical Urgency Staging & Top-3 Differential**:
  - Stage findings into Emergency Specialist, Routine Dermatologist, or Over-the-Counter Hygiene tiers with Top-3 differential probabilities.
  - Priority: High | Status: Implemented

- **[REQ-07] Active Ingredient Guidance**:
  - Provide evidence-based active ingredient recommendations (e.g. Ketoconazole, Zinc Pyrithione, Minoxidil, Clobetasol) tailored to the predicted condition.
  - Priority: Medium | Status: Implemented

- **[REQ-08] Web Application User Interface**:
  - Responsive, modern frontend allowing camera capture, drag-and-drop upload, real-time diagnostic presentation, and PDF report export.
  - Priority: Medium | Status: Implemented

- **[REQ-09] Longitudinal Trichometry Recovery Timeline**:
  - Track patient progress over time by visualizing changes in Scalp Health Score, Erythema %, and Flakiness % across sequential scans.
  - Priority: High | Status: Planned (Phase 08)

- **[REQ-10] Interactive Historical Scan Detail View**:
  - Dedicated `/scan/<id>/` view allowing patients/clinicians to re-examine historical scans, including saved Grad-CAM heatmaps, trichometry metrics, and active ingredient plans.
  - Priority: High | Status: Planned (Phase 08)

- **[REQ-11] Guest Scan Session Claiming**:
  - Persist scans performed by guest users in session storage and automatically bind them to the account when the user logs in or registers.
  - Priority: High | Status: Planned (Phase 08)

- **[REQ-12] Scan History Search, Filtering & Management**:
  - Enable filtering by condition, date sorting, and deletion of unwanted scans with user authorization checks.
  - Priority: Medium | Status: Planned (Phase 08)

---

## Non-Functional Requirements

- **[NFR-01] Latency & Resource Efficiency**:
  - Complete full inference (downsampling, TTA, trichometry, Grad-CAM) in $< 1.5$ seconds on a single CPU core with peak RAM $< 50\text{MB}$.
  - Priority: High | Status: Verified

- **[NFR-02] Stateless Privacy**:
  - Diagnostic photo analysis must occur in-memory without storing patient images in disk logs or persistent databases.
  - Priority: High | Status: Verified

- **[NFR-03] High Availability & Continuous Deployment**:
  - Docker container running with auto-restart on AWS EC2, fronted by Cloudflare Tunnel for end-to-end SSL encryption without public open ingress ports.
  - Priority: High | Status: Verified
