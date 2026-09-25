"""
trichometry_engine.py
Clinical computer vision module for objective scalp and hair quantitative metrics:
1. Flakiness & White Scaly Skin Index (0-100%)
2. Scalp Erythema / Redness Index (0-100%)
3. Scalp Exposure / Hair Density Ratio (0-100%)
4. Composite Scalp Health Score (0-100)
5. Clinical Severity Staging & Targeted Active Ingredients
"""

import numpy as np
from PIL import Image

ACTIVE_INGREDIENTS = {
    "psoriasis": {
        "title": "Scalp Psoriasis Management",
        "ingredients": [
            {"name": "Salicylic Acid (3% - 6%)", "role": "Keratolytic agent to soften and remove thick silvery adherent scales"},
            {"name": "Coal Tar Solution (1% - 5%)", "role": "Suppresses epidermal hyperproliferation and relieves scalp itching"},
            {"name": "Topical Corticosteroids (Clobetasol / Betamethasone)", "role": "Potent anti-inflammatory to resolve acute erythema plaques"},
            {"name": "Calcipotriol (Vitamin D3 analog)", "role": "Normalizes keratinocyte differentiation without steroid skin thinning"}
        ],
        "wash_routine": "Medicated shampoo 2-3x per week; leave lather on scalp for 5-7 minutes before rinsing.",
        "avoid": "Physical aggressive scratching or fine-toothed scraping which triggers the Koebner phenomenon (new lesions at trauma sites)."
    },
    "seborrheic_dermatitis": {
        "title": "Seborrheic Dermatitis & Scale Control",
        "ingredients": [
            {"name": "Ketoconazole 2%", "role": "Broad-spectrum antifungal targeting Malassezia yeast colonization"},
            {"name": "Zinc Pyrithione / Selenium Sulfide 1%", "role": "Reduces sebum secretion rate and epidermal flaking"},
            {"name": "Ciclopirox Olamine 1%", "role": "Dual anti-inflammatory and fungicidal action"},
            {"name": "Mild Topical Hydrocortisone 1%", "role": "Short-term relief for intense scalp itching and redness"}
        ],
        "wash_routine": "Alternate between Ketoconazole and Zinc Pyrithione shampoos every other day during active flare-ups.",
        "avoid": "Heavy occlusive hair oils or greases (e.g. pure coconut or castor oil) which fuel Malassezia yeast proliferation."
    },
    "dandruff": {
        "title": "Anti-Dandruff Flake Control",
        "ingredients": [
            {"name": "Zinc Pyrithione (1% - 2%)", "role": "Standard first-line anti-dandruff antimicrobial"},
            {"name": "Piroctone Olamine", "role": "Gentle antifungal and soothing agent for dry flaking"},
            {"name": "Salicylic Acid (2%)", "role": "Exfoliates loose flakes along hair partings"}
        ],
        "wash_routine": "Lather 3 times weekly; rinse thoroughly with lukewarm water.",
        "avoid": "Very hot water showers and alcohol-heavy hair styling gels that dry out scalp epidermis."
    },
    "folliculitis": {
        "title": "Folliculitis & Antimicrobial Regimen",
        "ingredients": [
            {"name": "Benzoyl Peroxide Wash (5%)", "role": "Reduces follicular bacterial load (Staphylococcus)"},
            {"name": "Chlorhexidine Gluconate Scalp Cleanser", "role": "Broad-spectrum medical antiseptic wash"},
            {"name": "Topical Clindamycin / Erythromycin", "role": "Targeted antibiotic for inflamed follicular pustules"}
        ],
        "wash_routine": "Gentle antiseptic lather once daily during acute breakouts; do not pop pustules.",
        "avoid": "Heavy pomades, sharing razors or clippers, and tight non-breathable caps."
    },
    "folliculitis_decalvans": {
        "title": "Urgent Cicatricial Care",
        "ingredients": [
            {"name": "Oral Rifampicin + Clindamycin", "role": "Standard gold-standard combination prescribed by specialists"},
            {"name": "Antiseptic Chlorhexidine Scalp Solution", "role": "Topical maintenance between medical treatments"}
        ],
        "wash_routine": "Daily gentle antiseptic wash under dermatologist supervision.",
        "avoid": "Delays in treatment; this condition causes permanent irreversible follicle scarring."
    },
    "alopecia_areata": {
        "title": "Alopecia Areata Support",
        "ingredients": [
            {"name": "Intralesional Triamcinolone Acetonide", "role": "Dermatologist-administered localized immunotherapy"},
            {"name": "Topical Minoxidil 5%", "role": "Stimulates hair follicle anagen phase regrowth"},
            {"name": "Topical JAK Inhibitors", "role": "Cutting-edge targeted autoimmune cytokine suppression"}
        ],
        "wash_routine": "Sulfate-free mild nourishing shampoo daily or every other day.",
        "avoid": "Harsh chemical straightening, chemical bleaches, or traction tension."
    },
    "androgenetic_alopecia": {
        "title": "Pattern Thinning Regimen",
        "ingredients": [
            {"name": "Topical Minoxidil 5%", "role": "Vasodilator promoting follicular caliber and density"},
            {"name": "Oral Finasteride / Dutasteride", "role": "Inhibits 5-alpha reductase conversion to DHT (physician prescribed)"},
            {"name": "Ketoconazole 2% Shampoo", "role": "Mild anti-androgenic effect and scalp sebum control"}
        ],
        "wash_routine": "Apply Minoxidil twice daily to clean, dry scalp continuously.",
        "avoid": "Stopping Minoxidil abruptly once started, as regrown hair will shed."
    },
    "telogen_effluvium": {
        "title": "Telogen Effluvium Recovery",
        "ingredients": [
            {"name": "Nutritional Repletion (Iron, Ferritin, Vitamin D, Zinc)", "role": "Corrects underlying metabolic hair shedding triggers"},
            {"name": "Gentle Peptide Scalp Serums", "role": "Nourishes anagen hair matrix during shedding recovery"}
        ],
        "wash_routine": "Gentle washing 2-3 times per week; comb gently with wide-tooth comb.",
        "avoid": "Aggressive brushing, extreme calorie-restriction diets, and severe emotional stressors."
    },
    "tinea_capitis": {
        "title": "Fungal Tinea Capitis Protocol",
        "ingredients": [
            {"name": "Oral Griseofulvin or Terbinafine", "role": "Mandatory systemic antifungal to reach the hair follicle root"},
            {"name": "Ketoconazole 2% / Selenium Sulfide 2.5% Shampoo", "role": "Reduces fungal spore shedding to prevent spreading"}
        ],
        "wash_routine": "Use antifungal shampoo 2-3 times weekly alongside prescription oral tablets.",
        "avoid": "Topical-only treatment (ineffective for scalp tinea) and sharing combs or towels."
    },
    "pediculosis_capitis": {
        "title": "Pediculicide Eradication",
        "ingredients": [
            {"name": "Dimethicone 4% Lotion", "role": "Suffocates adult lice and nymphs without chemical pesticide resistance"},
            {"name": "Permethrin 1% Cream Rinse", "role": "Neurotoxic pediculicide targeting active parasites"}
        ],
        "wash_routine": "Apply to dry hair, wait full contact time, then meticulously wet-comb with metal nit comb.",
        "avoid": "Skipping repeat treatment at Day 9 (needed to kill newly hatched nits)."
    },
    "lichen_planopilaris": {
        "title": "Cicatricial Lichenoid Care",
        "ingredients": [
            {"name": "Superpotent Topical Steroid (Clobetasol Propionate)", "role": "Halt lymphocytic follicle destruction"},
            {"name": "Hydroxychloroquine (Systemic)", "role": "Immunomodulatory therapy prescribed by dermatologist"}
        ],
        "wash_routine": "Hypoallergenic, fragrance-free gentle shampoo.",
        "avoid": "Scalp friction, irritating botanical oils, and thermal hair styling."
    },
    "traction_alopecia": {
        "title": "Mechanical Hairline Restoration",
        "ingredients": [
            {"name": "Hairstyle De-Tensioning", "role": "Immediate relief of mechanical strain on marginal follicles"},
            {"name": "Topical Minoxidil 5%", "role": "Stimulates revival of early-stage stressed follicles"}
        ],
        "wash_routine": "Gentle cleansing without pulling or high-tension brushing.",
        "avoid": "Tight braids, weaves, heavy dreadlocks, high ponytails, or chemical hair relaxers."
    },
    "trichotillomania": {
        "title": "Trichotillomania Behavioral Support",
        "ingredients": [
            {"name": "Habit Reversal Training (HRT)", "role": "Clinical behavioral therapy technique to intercept pulling urges"},
            {"name": "Scalp Barrier Creams & Fingertip Protectors", "role": "Reduces sensory urge during vulnerable evening periods"}
        ],
        "wash_routine": "Cool soothing washes with aloe vera and chamomile extracts.",
        "avoid": "Self-punishment or guilt; this is a recognized neurobehavioral impulse condition."
    },
    "contact_dermatitis": {
        "title": "Allergen Elimination & Soothing",
        "ingredients": [
            {"name": "Topical Hydrocortisone 1% or Desonide", "role": "Relieves acute weeping, edema, and itching"},
            {"name": "Cool Saline Compresses", "role": "Soothes hot, inflamed epidermal skin barrier"}
        ],
        "wash_routine": "Rinse thoroughly with tepid water and fragrance-free medical wash.",
        "avoid": "Hair dyes containing p-Phenylenediamine (PPD), sulfates, and synthetic perfumes."
    },
    "normal_healthy_scalp": {
        "title": "Physiological Scalp Maintenance",
        "ingredients": [
            {"name": "Balanced pH (5.5) Cleanser", "role": "Preserves natural scalp acid mantle and microbiome"},
            {"name": "Mild Botanical Antioxidants", "role": "Maintains optimal follicular hydration"}
        ],
        "wash_routine": "Wash 2-4 times weekly depending on sebum production.",
        "avoid": "Over-washing with harsh clarifying shampoos that strip natural lipid barriers."
    }
}

def analyze_scalp_metrics(pil_image):
    """
    Computes objective quantitative computer vision metrics on the scalp image.
    Returns dictionary with:
      - flakiness_pct (0.0 - 100.0)
      - erythema_pct (0.0 - 100.0)
      - scalp_exposure_pct (0.0 - 100.0)
      - health_score (0.0 - 100.0)
      - severity_stage ("Mild", "Moderate", "Severe")
      - flakiness_badge ("Low / Clean", "Moderate Flaking", "Severe Scaling & Plaques")
      - erythema_badge ("Normal / Pale", "Mild Redness", "Severe Inflammation")
    """
    img = pil_image.convert("RGB").resize((300, 300))
    arr = np.array(img).astype(float)

    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    # 1. Brightness & Color Saturation
    brightness = (r + g + b) / 3.0
    max_c = np.maximum(np.maximum(r, g), b)
    min_c = np.minimum(np.minimum(r, g), b)
    saturation = (max_c - min_c) / (max_c + 1e-5)

    # 2. White Scaly Skin / Flakiness Detection:
    # Characterized by high brightness (> 150) and low-to-moderate saturation (< 0.35)
    # on hair and scalp parting regions
    flake_mask = (brightness > 145) & (saturation < 0.38)
    flakiness_pct = round(float(np.mean(flake_mask) * 100.0), 1)

    # 3. Scalp Erythema (Redness / Inflammation) Detection:
    # Elevated red channel relative to green and blue
    erythema_val = np.maximum(0, r - (g + b) / 2.0)
    erythema_mask = (erythema_val > 18) & (brightness > 40)
    erythema_pct = round(float(np.mean(erythema_mask) * 100.0), 1)

    # 4. Scalp Exposure / Hair Density Ratio:
    # Skin tone detection: R > G > B with moderate brightness
    skin_mask = (r > g) & (g > b) & (brightness > 50) & (brightness < 215)
    scalp_exposure_pct = round(float(np.mean(skin_mask) * 100.0), 1)

    # 5. Scalp Health Score (0 - 100):
    # A perfect healthy scalp has minimal flakiness (< 5%) and minimal erythema (< 5%)
    # Deductions are weighted based on clinical impact:
    flakiness_penalty = min(50.0, flakiness_pct * 1.8)
    erythema_penalty = min(35.0, erythema_pct * 1.5)
    exposure_penalty = min(15.0, max(0.0, (scalp_exposure_pct - 30.0) * 0.4))

    raw_health = 100.0 - (flakiness_penalty + erythema_penalty + exposure_penalty)
    health_score = round(float(max(10.0, min(100.0, raw_health))), 1)

    # Badges
    if flakiness_pct >= 18.0:
        flakiness_badge = "Severe Scaling & Plaques"
        flake_color = "#dc2626"
    elif flakiness_pct >= 8.0:
        flakiness_badge = "Moderate Flaking"
        flake_color = "#d97706"
    else:
        flakiness_badge = "Minimal / Clean Scalp"
        flake_color = "#059669"

    if erythema_pct >= 15.0:
        erythema_badge = "High Inflammation / Redness"
        erythema_color = "#dc2626"
    elif erythema_pct >= 7.0:
        erythema_badge = "Mild Erythema"
        erythema_color = "#d97706"
    else:
        erythema_badge = "Normal Physiological Tone"
        erythema_color = "#059669"

    if health_score >= 75.0:
        severity_stage = "Mild / Good Condition"
        stage_color = "#059669"
    elif health_score >= 45.0:
        severity_stage = "Moderate / Active Dermatosis"
        stage_color = "#d97706"
    else:
        severity_stage = "Severe / Clinical Intervention Advised"
        stage_color = "#dc2626"

    return {
        "flakiness_pct": flakiness_pct,
        "flakiness_badge": flakiness_badge,
        "flake_color": flake_color,
        "erythema_pct": erythema_pct,
        "erythema_badge": erythema_badge,
        "erythema_color": erythema_color,
        "scalp_exposure_pct": scalp_exposure_pct,
        "health_score": health_score,
        "severity_stage": severity_stage,
        "stage_color": stage_color,
    }

def get_treatment_recommendation(predicted_label):
    """
    Returns clinical treatment plan and active ingredients for the diagnosed condition.
    """
    return ACTIVE_INGREDIENTS.get(predicted_label, ACTIVE_INGREDIENTS["normal_healthy_scalp"])
