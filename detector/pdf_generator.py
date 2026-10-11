import io
import os
import base64
import hashlib
from datetime import datetime
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Unicode fonts for Devanagari and international characters if available
HINDI_FONT = "Helvetica"
HINDI_FONT_BOLD = "Helvetica-Bold"

for _fname, _fpath in [
    ("Mangal", "C:/Windows/Fonts/mangal.ttf"),
    ("Mangal-Bold", "C:/Windows/Fonts/mangalb.ttf"),
    ("Nirmala", "C:/Windows/Fonts/Nirmala.ttc"),
    ("FreeSans", "/usr/share/fonts/truetype/freefont/FreeSans.ttf"),
    ("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]:
    if os.path.exists(_fpath):
        try:
            pdfmetrics.registerFont(TTFont(_fname, _fpath))
            if "Mangal" in _fname:
                HINDI_FONT = "Mangal"
                if "Bold" in _fname:
                    HINDI_FONT_BOLD = "Mangal-Bold"
            elif HINDI_FONT == "Helvetica":
                HINDI_FONT = _fname
                HINDI_FONT_BOLD = _fname
        except Exception:
            pass

CONDITION_LOCALIZATIONS = {
    "en": {
        "alopecia_areata": {
            "title": "Alopecia Areata",
            "desc": "An autoimmune condition causing round or oval patches of sudden, non-scarring hair loss. The body's immune system mistakenly attacks hair follicles.",
            "advice": "Consult a dermatologist. First-line treatments may include topical corticosteroids, minoxidil, or intralesional steroid injections."
        },
        "androgenetic_alopecia": {
            "title": "Androgenetic Alopecia",
            "desc": "Genetically predetermined progressive thinning and miniaturization of hair follicles (male or female pattern baldness).",
            "advice": "Evidence-based options include topical minoxidil, oral anti-androgens (under physician guidance), and low-level laser therapy."
        },
        "contact_dermatitis": {
            "title": "Contact Dermatitis",
            "desc": "An acute or subacute inflammatory reaction triggered by allergens or irritants (e.g. hair dyes, fragrances, surfactants) causing erythema and weeping.",
            "advice": "Identify and remove the offending allergen immediately. Cool compresses and topical mild corticosteroids can provide symptomatic relief."
        },
        "dandruff": {
            "title": "Dandruff (Pityriasis Capitis)",
            "desc": "Mild, non-inflammatory scalp shedding presenting as fine white or grayish dry flaking without marked erythema.",
            "advice": "Regular cleansing with over-the-counter anti-dandruff shampoos containing zinc pyrithione, ketoconazole, or selenium sulfide is recommended."
        },
        "folliculitis": {
            "title": "Folliculitis",
            "desc": "Superficial inflammation or bacterial/fungal infection of the hair follicles presenting as erythematous papules and pustules.",
            "advice": "Gentle antiseptic washes (e.g. chlorhexidine or benzoyl peroxide). Severe or persistent cases require targeted oral antibiotics or antifungals."
        },
        "folliculitis_decalvans": {
            "title": "Folliculitis Decalvans",
            "desc": "A chronic, cicatricial (scarring) alopecia characterized by tufted hairs ('doll's hairs'), recurrent follicular pustules, and irreversible hair loss.",
            "advice": "Requires urgent dermatological care to prevent permanent scarring. Long-term combination antibiotic therapy is commonly prescribed."
        },
        "lichen_planopilaris": {
            "title": "Lichen Planopilaris",
            "desc": "A primary cicatricial alopecia variant of lichen planus presenting with violaceous perifollicular erythema, keratotic spine casts, and follicular loss.",
            "advice": "Immediate evaluation by a trichology specialist. Anti-inflammatory treatments (corticosteroids, hydroxychloroquine) help halt scarring progression."
        },
        "normal_healthy_scalp": {
            "title": "Normal Healthy Scalp",
            "desc": "No evidence of pathological erythema, scaling, follicular plugging, or abnormal shedding. Hair density and follicular units appear physiological.",
            "advice": "Maintain standard scalp hygiene and balanced nutrition. No medical intervention required."
        },
        "pediculosis_capitis": {
            "title": "Pediculosis Capitis (Head Lice)",
            "desc": "Infestation by Pediculus humanus capitis with visible oval nits firmly cemented to hair shafts, accompanied by pruritus.",
            "advice": "Pediculicide treatments (e.g. permethrin or dimethicone-based lotions) combined with meticulous wet-combing with a fine-toothed nit comb."
        },
        "psoriasis": {
            "title": "Scalp Psoriasis",
            "desc": "A chronic autoimmune dermatosis characterized by well-demarcated erythematous plaques covered with thick, silvery-white lamellar scales.",
            "advice": "Topical corticosteroids combined with calcipotriol (vitamin D analogs), keratolytic agents (salicylic acid), or systemic biologics for extensive disease."
        },
        "seborrheic_dermatitis": {
            "title": "Seborrheic Dermatitis",
            "desc": "Inflammatory scalp disorder linked to Malassezia yeast colonization, presenting as greasy yellowish crusts, scaling, and diffuse erythema.",
            "advice": "Medicated shampoos containing ketoconazole 2%, ciclopirox, or coal tar, coupled with intermittent low-potency topical steroids if inflamed."
        },
        "telogen_effluvium": {
            "title": "Telogen Effluvium",
            "desc": "Diffuse, non-scarring hair shedding caused by premature transition of follicles into the telogen phase, usually 2-3 months following an acute stressor.",
            "advice": "Address underlying triggers (iron/ferritin deficiency, thyroid dysfunction, post-illness stress, nutritional deficits). Hair usually regrows spontaneously."
        },
        "tinea_capitis": {
            "title": "Tinea Capitis",
            "desc": "A fungal dermatophyte infection of scalp hair follicles, presenting as circular scaly patches, broken hair stubble ('black dots'), and lymphadenopathy.",
            "advice": "Systemic antifungal medications (e.g. oral griseofulvin or terbinafine) are necessary; topical therapy alone is insufficient to clear follicular infection."
        },
        "traction_alopecia": {
            "title": "Traction Alopecia",
            "desc": "Hair loss resulting from prolonged, repetitive mechanical tension on hair roots (e.g. tight ponytails, braids, weaves, or heavy extensions).",
            "advice": "Immediately adopt loose, natural hairstyles. Early-stage traction is completely reversible; late-stage scarring requires specialist treatment."
        },
        "trichotillomania": {
            "title": "Trichotillomania",
            "desc": "A compulsive hair-pulling disorder presenting with irregular, bizarre patches of incomplete hair loss with fractured hairs of uneven lengths.",
            "advice": "Multidisciplinary management including behavioral therapy (habit reversal training) and dermatological support."
        },
    },
    "es": {
        "alopecia_areata": {
            "title": "Alopecia Areata",
            "desc": "Trastorno autoinmune que provoca parches redondos u ovalados de caída repentina del cabello sin cicatrización. El sistema inmunológico ataca los folículos pilosos.",
            "advice": "Consulte a un dermatólogo. Los tratamientos de primera línea incluyen corticosteroides tópicos, minoxidil o microinyecciones intralesionales."
        },
        "androgenetic_alopecia": {
            "title": "Alopecia Androgenética",
            "desc": "Adelgazamiento y miniaturización progresiva de folículos pilosos de origen genético y hormonal (calvicie de patrón masculino o femenino).",
            "advice": "Las opciones con respaldo científico incluyen minoxidil tópico, antiandrógenos orales bajo supervisión médica y terapia láser de baja intensidad."
        },
        "contact_dermatitis": {
            "title": "Dermatitis de Contacto",
            "desc": "Reacción inflamatoria aguda desencadenada por alérgenos o irritantes (tintes capilares, fragancias, sulfatos) que causa eritema y exudación.",
            "advice": "Identifique y elimine el alérgeno causante de inmediato. Compresas frías y corticosteroides tópicos suaves alivian los síntomas."
        },
        "dandruff": {
            "title": "Caspa (Pitiriasis Simple)",
            "desc": "Descamación leve y no inflamatoria del cuero cabelludo que se presenta como escamas secas blanquecinas o grisáceas sin eritema pronunciado.",
            "advice": "Se recomienda el lavado regular con champús anticaspa que contengan piritionato de zinc, ketoconazol o sulfuro de selenio."
        },
        "folliculitis": {
            "title": "Foliculitis",
            "desc": "Inflamación o infección bacteriana/fúngica superficial de los folículos pilosos que produce pápulas eritematosas y pústulas.",
            "advice": "Lavados antisépticos suaves (clorhexidina o peróxido de benzoilo). Casos persistentes requieren antibióticos o antifúngicos específicos."
        },
        "folliculitis_decalvans": {
            "title": "Foliculitis Decalvante",
            "desc": "Alopecia cicatrizal crónica caracterizada por mechones de cabello agrupados ('pelo en muñeca'), pústulas foliculares recurrentes y destrucción folicular irreversible.",
            "advice": "Requiere atención dermatológica urgente para prevenir cicatrización irreversible. Tratamiento combinado con antibióticos prolongados."
        },
        "lichen_planopilaris": {
            "title": "Liquen Plano Pilar",
            "desc": "Alopecia cicatrizal primaria que cursa con eritema violáceo perifolicular, tapones queratósicos y pérdida folicular definitiva.",
            "advice": "Evaluación inmediata por un especialista en tricología. Antiinflamatorios potentes frenan la progresión de la fibrosis cicatrizal."
        },
        "normal_healthy_scalp": {
            "title": "Cuero Cabelludo Sano",
            "desc": "Sin indicios de eritema patológico, descamación ni taponamiento folicular. La densidad capilar y los folículos muestran parámetros normales.",
            "advice": "Mantenga la higiene capilar habitual y una dieta equilibrada. No requiere intervención farmacológica."
        },
        "pediculosis_capitis": {
            "title": "Pediculosis Capitis (Piojos)",
            "desc": "Infestación por Pediculus humanus capitis con liendres ovaladas adheridas a los tallos pilosos y prurito intenso.",
            "advice": "Tratamiento pediculicida (lociones de permetrina o dimeticona) acompañado de peinado minucioso con lendrera."
        },
        "psoriasis": {
            "title": "Psoriasis del Cuero Cabelludo",
            "desc": "Dermatosis autoinmune crónica con placas eritematosas bien delimitadas cubiertas por escamas gruesas plateadas o nacaradas.",
            "advice": "Corticosteroides tópicos combinados con calcipotriol, agentes queratolíticos (ácido salicílico) o terapias biológicas en casos extensos."
        },
        "seborrheic_dermatitis": {
            "title": "Dermatitis Seborreica",
            "desc": "Trastorno inflamatorio asociado a la colonización por levaduras Malassezia, manifestándose con escamas grasas amarillentas y eritema.",
            "advice": "Champús medicinales con ketoconazol 2%, ciclopirox o alquitrán de hulla, junto con corticoides suaves intermitentes."
        },
        "telogen_effluvium": {
            "title": "Efluvio Telógeno",
            "desc": "Caída difusa y no cicatrizal del cabello debida a la entrada prematura en fase de reposo (telógena), a menudo tras estrés, fiebre o déficit nutricional.",
            "advice": "Tratar la causa subyacente (niveles de ferritina/hierro, tiroides, nutrición). El cabello suele recuperarse gradualmente de forma espontánea."
        },
        "tinea_capitis": {
            "title": "Tiña del Cuero Cabelludo",
            "desc": "Infección fúngica dermatofítica de folículos pilosos que produce áreas circulares descamativas y pelos rotos ('puntos negros').",
            "advice": "Requiere antifúngicos orales sistémicos (griseofulvina o terbinafina); los tópicos por sí solos no erradican la infección folicular."
        },
        "traction_alopecia": {
            "title": "Alopecia por Tracción",
            "desc": "Pérdida de cabello debida a tensión mecánica continuada sobre la raíz (coletas tirantes, trenzas apretadas, extensiones pesadas).",
            "advice": "Cambie de inmediato a peinados sueltos y naturales. En etapas tempranas es totalmente reversible."
        },
        "trichotillomania": {
            "title": "Tricotilomanía",
            "desc": "Trastorno compulsivo de arrancamiento del cabello que genera parches irregulares con cabellos fracturados a longitudes desiguales.",
            "advice": "Abordaje multidisciplinar con terapia cognitivo-conductual (entrenamiento en inversión de hábitos) y apoyo dermatológico."
        },
    },
    "hi": {
        "alopecia_areata": {
            "title": "एलोपेसिया एरीआटा (Alopecia Areata)",
            "desc": "एक ऑटोइम्यून स्थिति जिसके कारण अचानक गोल या अंडाकार पैच में बाल झड़ने लगते हैं। शरीर की प्रतिरक्षा प्रणाली बालों के रोमों पर हमला करती है।",
            "advice": "त्वचा विशेषज्ञ से परामर्श लें। प्राथमिक उपचार में सामयिक कॉर्टिकोस्टेरॉइड्स, मिनोक्सिडिल या स्टेरॉयड इंजेक्शन शामिल हो सकते हैं।"
        },
        "androgenetic_alopecia": {
            "title": "एंड्रोजेनेटिक एलोपेसिया (Pattern Baldness)",
            "desc": "आनुवंशिक और हार्मोनल कारणों से बालों के रोमों का पतला होना (पुरुष या महिला पैटर्न गंजापन)।",
            "advice": "उपचार में सामयिक मिनोक्सिडिल, चिकित्सक की सलाह पर एंटी-एंड्रोजेन और लो-लेवल लेजर थेरेपी शामिल हैं।"
        },
        "contact_dermatitis": {
            "title": "कॉन्टैक्ट डर्मेटाइटिस (Contact Dermatitis)",
            "desc": "एलर्जी या जलन पैदा करने वाले पदार्थों (जैसे हेयर डाई, सुगंध) के संपर्क में आने से होने वाली तीव्र सूजन, लालिमा और खुजली।",
            "advice": "एलर्जी पैदा करने वाले उत्पाद का उपयोग तुरंत बंद करें। ठंडी सिकाई और हल्के सामयिक स्टेरॉयड राहत देते हैं।"
        },
        "dandruff": {
            "title": "रूसी / डैंड्रफ (Dandruff)",
            "desc": "स्कैल्प से हल्की, गैर-सूजन वाली सूखी सफेद या भूरे रंग की पपड़ी गिरना, जिसमें कोई गंभीर लालिमा नहीं होती।",
            "advice": "जिंक पाइरिथियोन, कीटोकोनाज़ोल या सेलेनियम सल्फाइड युक्त एंटी-डैंड्रफ शैम्पू से नियमित बाल धोएं।"
        },
        "folliculitis": {
            "title": "फॉलिकुलिटिस (Folliculitis)",
            "desc": "बालों के रोमों की सतही सूजन या जीवाणु/कवक संक्रमण, जिससे लाल दाने और मवाद भरी फुंसियां होती हैं।",
            "advice": "हल्के एंटीसेप्टिक वॉश (क्लोरहेक्सिडिन या बेंजोइल पेरोक्साइड) का उपयोग करें। गंभीर मामलों में ओरल एंटीबायोटिक्स की आवश्यकता होती है।"
        },
        "folliculitis_decalvans": {
            "title": "फॉलिकुलिटिस डिकैल्वन्स (Folliculitis Decalvans)",
            "desc": "एक गंभीर निशान बनाने वाला गंजापन जिसमें एक रोमछिद्र से कई बाल गुच्छों में निकलते हैं और मवाद फुंसियां होती हैं।",
            "advice": "स्थायी बालों के नुकसान को रोकने के लिए तुरंत त्वचा विशेषज्ञ से संपर्क करें। लंबे समय तक एंटीबायोटिक उपचार आवश्यक होता है।"
        },
        "lichen_planopilaris": {
            "title": "लाइकेन प्लानोपिलारिस (Lichen Planopilaris)",
            "desc": "एक प्राथमिक निशानदार गंजापन जिसमें रोमछिद्रों के चारों ओर बैंगनी लालिमा और पपड़ीदार स्पाइन बनते हैं।",
            "advice": "ट्राइकोलॉजी विशेषज्ञ से तुरंत जांच कराएं। घाव को बढ़ने से रोकने के लिए शक्तिशाली एंटी-इंफ्लेमेटरी दवाएं दी जाती हैं।"
        },
        "normal_healthy_scalp": {
            "title": "स्वस्थ और सामान्य स्कैल्प (Normal Healthy Scalp)",
            "desc": "किसी भी असामान्य लालिमा, रूसी या रोम छिद्रों के बंद होने का कोई लक्षण नहीं। बालों का घनत्व सामान्य और स्वस्थ है।",
            "advice": "नियमित स्वच्छता और संतुलित आहार बनाए रखें। किसी चिकित्सीय उपचार की आवश्यकता नहीं है।"
        },
        "pediculosis_capitis": {
            "title": "सिर में जूं / लीक (Pediculosis Capitis)",
            "desc": "सिर में जुओं का संक्रमण जिसमें बालों से चिपकी हुई लीखें (अंडे) और तेज खुजली होती है।",
            "advice": "एंटी-लाइस लोशन (परमेथ्रिन या डाइमेथिकोन) लगाएं और बारीक कंघी से बालों को अच्छी तरह सुलझाएं।"
        },
        "psoriasis": {
            "title": "स्कैल्प सोरायसिस (Scalp Psoriasis)",
            "desc": "एक पुरानी ऑटोइम्यून बीमारी जिसमें स्कैल्प पर मोटी, चांदी जैसी सफेद पपड़ी और लाल चकत्ते बन जाते हैं।",
            "advice": "कॉर्टिकोस्टेरॉइड्स, कैल्सीपोट्रियोल (विटामिन डी एनालॉग) और सैलिसिलिक एसिड युक्त सामयिक उपचार का उपयोग करें।"
        },
        "seborrheic_dermatitis": {
            "title": "सेबोरहाइक डर्मेटाइटिस (Seborrheic Dermatitis)",
            "desc": "मालासेजिया यीस्ट से जुड़ी सूजन, जिसमें चिपचिपी पीली पपड़ी, रूसी और लालिमा दिखाई देती है।",
            "advice": "2% कीटोकोनाज़ोल, सिक्लोपिरोक्स या कोल टार युक्त औषधीय शैम्पू का प्रयोग करें।"
        },
        "telogen_effluvium": {
            "title": "टेलोजेन एफ्लुवियम (Telogen Effluvium)",
            "desc": "तनाव, बीमारी या पोषण की कमी के कारण अचानक बड़ी मात्रा में बालों का झड़ना। इसमें रोम नष्ट नहीं होते।",
            "advice": "मूल कारण (आयरन, थायराइड, तनाव) का समाधान करें। स्वास्थ्य ठीक होने पर बाल आमतौर पर वापस उग आते हैं।"
        },
        "tinea_capitis": {
            "title": "टिनिया कैपिटिस (Tinea Capitis)",
            "desc": "स्कैल्प का फंगल संक्रमण जिससे गोल पपड़ीदार चकत्ते और टूटे हुए बालों के काले ठूंठ बन जाते हैं।",
            "advice": "ओरल एंटीफंगल दवाएं (जैसे ग्रिसोफुलविन या टर्बिनाफाइन) अनिवार्य हैं; केवल क्रीम पर्याप्त नहीं होती।"
        },
        "traction_alopecia": {
            "title": "ट्रैक्शन एलोपेसिया (Traction Alopecia)",
            "desc": "बालों को कसकर बांधने (जैसे कसी हुई चोटी, पोनीटेल या एक्सटेंशन) से होने वाला बालों का झड़ना।",
            "advice": "तुरंत ढीले और प्राकृतिक हेयर स्टाइल अपनाएं। शुरुआती स्थिति में बाल पूरी तरह वापस आ जाते हैं।"
        },
        "trichotillomania": {
            "title": "ट्राइकोटिलोमेनिया (Trichotillomania)",
            "desc": "अनजाने में बाल खींचने और तोड़ने की आदत, जिससे असमान लंबाई के टूटे बालों वाले अजीब पैच बन जाते हैं।",
            "advice": "व्यवहार चिकित्सा (हैबिट रिवर्सल ट्रेनिंग) और त्वचा विशेषज्ञ की सलाह से उपचार संभव है।"
        },
    }
}

# Standard English dictionary export for backward compatibility
CONDITION_INFO = CONDITION_LOCALIZATIONS["en"]

ICD10_CODES = {
    "alopecia_areata": "L63.9 (Alopecia areata, unspecified)",
    "androgenetic_alopecia": "L64.9 (Androgenetic alopecia, unspecified)",
    "contact_dermatitis": "L23.9 (Allergic contact dermatitis, unspecified cause)",
    "dandruff": "L21.0 (Seborrhea capitis / Pityriasis capitis)",
    "folliculitis": "L73.9 (Follicular disorder, unspecified)",
    "folliculitis_decalvans": "L66.2 (Folliculitis decalvans)",
    "lichen_planopilaris": "L66.1 (Lichen planopilaris)",
    "normal_healthy_scalp": "Z00.00 (General medical examination without abnormal findings)",
    "pediculosis_capitis": "B85.0 (Pediculosis due to Pediculus humanus capitis)",
    "psoriasis": "L40.0 (Psoriasis vulgaris / Scalp psoriasis)",
    "seborrheic_dermatitis": "L21.0 (Seborrheic dermatitis of scalp)",
    "telogen_effluvium": "L65.0 (Telogen effluvium)",
    "tinea_capitis": "B35.0 (Tinea barbae and tinea capitis)",
    "traction_alopecia": "L65.8 (Other specified nonscarring hair loss)",
    "trichotillomania": "F63.3 (Trichotillomania / Hair-pulling disorder)",
}

UI_STRINGS = {
    "en": {
        "report_title": "SCALP & HAIR AI CLINICAL SCREENING REPORT",
        "report_subtitle": "Automated Dermatological Analysis & Differential Screening Assessment",
        "report_id": "Report ID",
        "date": "Date",
        "patient": "Patient / User",
        "backbone": "Model Backbone",
        "backbone_val": "EfficientNet-B0 (Compound Scaling & Grad-CAM)",
        "classification": "Screening Spectrum",
        "classification_val": "15-Class Scalp Spectrum (84.8% Scaled Cohort Benchmark)",
        "inference_status": "Inference Status",
        "status_review": "Review Advised (Low Confidence)",
        "status_conclusive": "Normal Screening Complete",
        "primary_predicted": "PRIMARY PREDICTED CONDITION:",
        "ai_confidence": "AI Confidence",
        "clinical_triage": "Clinical Triage",
        "status_uncertain": "⚠️ Inconclusive (< 50%)",
        "status_certain": "✓ Conclusive Pattern",
        "clinical_desc": "Clinical Description:",
        "clinical_photo": "Clinical Photo:",
        "gradcam_photo": "Grad-CAM Heatmap:",
        "tricho_heading": "Quantitative Scalp Trichometry (Morphometric Analysis)",
        "health_score": "Scalp Health Score:",
        "flakiness": "Flakiness & White Scale:",
        "erythema": "Scalp Erythema (Redness):",
        "scalp_exposure": "Exposed Scalp Area:",
        "hairline_parting": "(Hairline / Parting)",
        "diff_heading": "Differential Diagnosis Breakdown (Ranked by Likelihood)",
        "rank": "Rank",
        "condition_name": "Condition Name",
        "prob_score": "Probability Score",
        "diff_indicator": "Differential Indicator",
        "primary_match": "Primary Match",
        "sig_prob": "Significant Probability",
        "low_prob": "Low / Baseline",
        # Page 2
        "page2_title": "TARGETED THERAPEUTIC REGIMEN & CLINICAL DOSSIER",
        "page2_subtitle": "Evidence-Based Active Ingredients & Dermatologist Referral Handover",
        "regimen_heading": "Recommended Active Ingredient Formulations",
        "ingredient": "Active Compound",
        "mechanism": "Pharmacological Role & Mechanism",
        "application": "Application / Usage",
        "wash_routine": "Recommended Wash Protocol:",
        "avoid_items": "Precautions & Ingredients to Avoid:",
        "referral_heading": "CLINICIAN TRIAGE REFERRAL HANDOVER SLIP",
        "ref_id": "Referral Verification Code:",
        "ref_patient": "Patient Name:",
        "ref_system": "Referring Engine: ScalpAI Clinical Diagnostic System v2.4 Enterprise",
        "presumptive_diag": "Presumptive Primary Finding:",
        "icd10": "Indication ICD-10 Code:",
        "triage_priority": "Triage Priority:",
        "physician_checklist": "Clinician Physical Review Checklist:",
        "check_diag": "[  ] Primary Diagnosis Verified & Confirmed",
        "check_tricho": "[  ] Trichoscopy / Dermatoscopy Completed",
        "check_rx": "[  ] Pharmacological Regimen Prescribed",
        "signature_line": "Attending Dermatologist / Trichologist Signature & Clinical Stamp:",
        "disclaimer_title": "LEGAL & MEDICAL SCREENING DISCLAIMER:",
        "disclaimer_text": "This report is generated by a computer vision deep learning model (EfficientNet-B0 Compound Scaling with Grad-CAM Visual Heatmaps) trained for educational and preliminary screening assistance only. This analysis does NOT constitute medical advice, diagnosis, or clinical evaluation. Image quality, lighting, and camera angle significantly affect model confidence. Always consult a qualified dermatologist or medical practitioner for any scalp or hair health concerns.",
    },
    "es": {
        "report_title": "INFORME DE EVALUACIÓN CLÍNICA DE CUERO CABELLUDO Y CABELLO",
        "report_subtitle": "Análisis Dermatológico Automatizado y Cribado Diferencial",
        "report_id": "ID de Informe",
        "date": "Fecha",
        "patient": "Paciente / Usuario",
        "backbone": "Arquitectura del Modelo",
        "backbone_val": "EfficientNet-B0 (Escalado Compuesto y Grad-CAM)",
        "classification": "Espectro de Clasificación",
        "classification_val": "Espectro de 15 Patologías (84.8% en Cohorte Clínica)",
        "inference_status": "Estado de Inferencia",
        "status_review": "Revisión Sugerida (Baja Confianza)",
        "status_conclusive": "Evaluación Concluyente",
        "primary_predicted": "CONDICIÓN PRINCIPAL DETECTADA:",
        "ai_confidence": "Confianza de IA",
        "clinical_triage": "Triaje Clínico",
        "status_uncertain": "⚠️ No Concluyente (< 50%)",
        "status_certain": "✓ Patrón Concluyente",
        "clinical_desc": "Descripción Clínica:",
        "clinical_photo": "Fotografía Clínica:",
        "gradcam_photo": "Mapa de Calor Grad-CAM:",
        "tricho_heading": "Tricometría Cuantitativa del Cuero Cabelludo (Análisis Morfométrico)",
        "health_score": "Puntuación de Salud Capilar:",
        "flakiness": "Descamación y Escamas:",
        "erythema": "Eritema (Enrojecimiento):",
        "scalp_exposure": "Área de Cuero Cabelludo Expuesta:",
        "hairline_parting": "(Línea de implantación / Raya)",
        "diff_heading": "Desglose de Diagnóstico Diferencial (Por Probabilidad)",
        "rank": "Posición",
        "condition_name": "Nombre de la Condición",
        "prob_score": "Puntuación Probabilística",
        "diff_indicator": "Indicador Diferencial",
        "primary_match": "Coincidencia Principal",
        "sig_prob": "Probabilidad Significativa",
        "low_prob": "Baja / Basal",
        # Page 2
        "page2_title": "RÉGIMEN TERAPÉUTICO DIRIGIDO Y EXPEDIENTE CLÍNICO",
        "page2_subtitle": "Ingredientes Activos Respaldados por Evidencia y Volante de Derivación",
        "regimen_heading": "Formulaciones y Principios Activos Recomendados",
        "ingredient": "Principio Activo",
        "mechanism": "Mecanismo y Rol Farmacológico",
        "application": "Aplicación / Frecuencia",
        "wash_routine": "Protocolo de Lavado Recomendado:",
        "avoid_items": "Precauciones e Ingredientes a Evitar:",
        "referral_heading": "VOLANTE DE DERIVACIÓN Y TRIAJE DERMATOLÓGICO",
        "ref_id": "Código de Verificación:",
        "ref_patient": "Nombre del Paciente:",
        "ref_system": "Sistema Emisor: ScalpAI Diagnóstico Clínico v2.4 Enterprise",
        "presumptive_diag": "Hallazgo Principal Presuntivo:",
        "icd10": "Código CIE-10 (ICD-10):",
        "triage_priority": "Prioridad de Triaje:",
        "physician_checklist": "Lista de Verificación del Especialista:",
        "check_diag": "[  ] Diagnóstico Principal Verificado y Confirmado",
        "check_tricho": "[  ] Tricoscopia / Dermatoscopia Realizada",
        "check_rx": "[  ] Régimen Farmacológico Prescrito",
        "signature_line": "Firma y Sello del Dermatólogo / Tricólogo Responsable:",
        "disclaimer_title": "AVISO LEGAL Y DE EVALUACIÓN MÉDICA:",
        "disclaimer_text": "Este informe es generado por un modelo de aprendizaje profundo (EfficientNet-B0 con Mapas de Calor Grad-CAM) para asistencia preliminar y educativa. Este análisis NO constituye diagnóstico ni consejo médico profesional. Consulte siempre a un dermatólogo colegiado ante cualquier problema de salud capilar.",
    },
    "hi": {
        "report_title": "स्कैल्प और बाल एआई क्लिनिकल रिपोर्ट (ScalpAI Report)",
        "report_subtitle": "स्वचालित त्वचाविज्ञान विश्लेषण एवं विभेदक जांच (Automated Dermatological Screening)",
        "report_id": "रिपोर्ट आईडी (ID)",
        "date": "दिनांक (Date)",
        "patient": "रोगी / उपयोगकर्ता (Patient)",
        "backbone": "मॉडल आर्किटेक्चर",
        "backbone_val": "EfficientNet-B0 (Compound Scaling & Grad-CAM)",
        "classification": "स्क्रीनिंग स्पेक्ट्रम",
        "classification_val": "15-क्लास स्कैल्प स्पेक्ट्रम (84.8% क्लिनिकल सटीकता)",
        "inference_status": "जांच स्थिति (Status)",
        "status_review": "पुनरावलोकन अनुशंसित (कम आत्मविश्वास)",
        "status_conclusive": "सामान्य स्क्रीनिंग पूर्ण",
        "primary_predicted": "प्राथमिक अनुमानित स्थिति (Primary Condition):",
        "ai_confidence": "एआई आत्मविश्वास (Confidence)",
        "clinical_triage": "क्लिनिकल प्राथमिकता (Triage)",
        "status_uncertain": "⚠️ अनिर्णायक (< 50%)",
        "status_certain": "✓ पुष्ट पैटर्न (Conclusive)",
        "clinical_desc": "नैदानिक विवरण (Clinical Description):",
        "clinical_photo": "क्लिनिकल फोटो:",
        "gradcam_photo": "Grad-CAM हीटमैप:",
        "tricho_heading": "मात्रात्मक स्कैल्प ट्राइकोमेट्री (Quantitative Scalp Trichometry)",
        "health_score": "स्कैल्प स्वास्थ्य स्कोर:",
        "flakiness": "रूसी एवं पपड़ी (Flakiness):",
        "erythema": "लालिमा (Erythema Redness):",
        "scalp_exposure": "खुली स्कैल्प का क्षेत्र:",
        "hairline_parting": "(मांग / हेयरलाइन)",
        "diff_heading": "विभेदक निदान विवरण (Differential Diagnosis Breakdown)",
        "rank": "रैंक",
        "condition_name": "बीमारी का नाम (Condition)",
        "prob_score": "संभावना स्कोर",
        "diff_indicator": "विभेदक सूचक",
        "primary_match": "प्राथमिक मेल (Primary)",
        "sig_prob": "उल्लेखनीय संभावना",
        "low_prob": "सामान्य / कम",
        # Page 2
        "page2_title": "लक्षित चिकित्सीय आहार एवं परामर्श डॉसियर (Therapeutic Dossier)",
        "page2_subtitle": "प्रमाण-आधारित सक्रिय तत्व और डॉक्टर रेफरल हैंडओवर पर्ची",
        "regimen_heading": "अनुशंसित सक्रिय घटक और दवाएं (Active Ingredients)",
        "ingredient": "सक्रिय घटक (Compound)",
        "mechanism": "औषधीय भूमिका और कार्यप्रणाली",
        "application": "उपयोग विधि (Application)",
        "wash_routine": "अनुशंसित धुलाई दिनचर्या (Wash Routine):",
        "avoid_items": "सावधानियां एवं परहेज (Things to Avoid):",
        "referral_heading": "चिकित्सक रेफरल एवं ट्राइएज हैंडओवर पर्ची (Referral Slip)",
        "ref_id": "रेफरल सत्यापन कोड:",
        "ref_patient": "रोगी का नाम:",
        "ref_system": "रेफरिंग इंजन: ScalpAI क्लिनिकल डायग्नोस्टिक v2.4 Enterprise",
        "presumptive_diag": "प्राथमिक अनुमानित बीमारी:",
        "icd10": "आईसीडी-10 कोड (ICD-10):",
        "triage_priority": "प्राथमिकता स्तर (Urgency):",
        "physician_checklist": "चिकित्सक सत्यापन चेकलिस्ट:",
        "check_diag": "[  ] प्राथमिक निदान सत्यापित और पुष्टि की गई",
        "check_tricho": "[  ] ट्राइकोस्कोपी / डर्मेटोस्कोपी पूर्ण",
        "check_rx": "[  ] औषधीय उपचार निर्धारित किया गया",
        "signature_line": "त्वचा विशेषज्ञ / ट्राइकोलॉजिस्ट के हस्ताक्षर एवं मुहर (Signature & Stamp):",
        "disclaimer_title": "कानूनी एवं चिकित्सीय अस्वीकरण (Medical Disclaimer):",
        "disclaimer_text": "यह रिपोर्ट केवल प्रारंभिक स्क्रीनिंग और शैक्षिक सहायता के लिए कंप्यूटर विजन एआई मॉडल द्वारा तैयार की गई है। यह किसी प्रमाणित चिकित्सक की सलाह या निदान का विकल्प नहीं है। किसी भी समस्या के लिए हमेशा प्रमाणित त्वचा विशेषज्ञ (Dermatologist) से परामर्श लें।",
    }
}


def generate_clinical_pdf(scan_record, patient_name=None, lang="en"):
    """
    Builds a professional 2-page clinical PDF report and referral dossier for a given ScanRecord.
    Supports localization in English ('en'), Spanish ('es'), and Hindi ('hi').
    Returns bytes buffer.
    """
    if not lang or lang.lower() not in ["en", "es", "hi"]:
        lang = "en"
    else:
        lang = lang.lower()

    ui = UI_STRINGS.get(lang, UI_STRINGS["en"])
    cond_catalog = CONDITION_LOCALIZATIONS.get(lang, CONDITION_LOCALIZATIONS["en"])

    # Determine fonts
    if lang == "hi":
        font_name = HINDI_FONT
        font_bold = HINDI_FONT_BOLD
    else:
        font_name = "Helvetica"
        font_bold = "Helvetica-Bold"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=32,
        leftMargin=32,
        topMargin=28,
        bottomMargin=28,
    )

    styles = getSampleStyleSheet()

    # Brand Colors
    primary_color = colors.HexColor("#1e3a8a")    # Deep Navy
    secondary_color = colors.HexColor("#0f766e")  # Clinical Teal
    text_dark = colors.HexColor("#1e293b")
    text_muted = colors.HexColor("#64748b")
    border_color = colors.HexColor("#cbd5e1")
    accent_bg = colors.HexColor("#f8fafc")
    slip_bg = colors.HexColor("#f0fdf4")
    slip_border = colors.HexColor("#16a34a")

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName=font_bold,
        fontSize=16,
        leading=19,
        textColor=primary_color,
        spaceAfter=2,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=9,
        leading=12,
        textColor=text_muted,
        spaceAfter=8,
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName=font_bold,
        fontSize=11,
        leading=14,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=8.5,
        leading=11.5,
        textColor=text_dark,
    )
    bold_style = ParagraphStyle(
        "ReportBold",
        parent=body_style,
        fontName=font_bold,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=7,
        leading=9.5,
        textColor=text_muted,
    )

    elements = []

    # =========================================================================
    # PAGE 1: CLINICAL SCREENING, GRAD-CAM & TRICHOMETRIC MORPHOMETRY
    # =========================================================================

    # Header Banner
    header_data = [
        [
            Paragraph(f"<b>{ui['report_title']}</b>", title_style),
            Paragraph(
                f"<b>{ui['report_id']}:</b> #{scan_record.id:06d}<br/><b>{ui['date']}:</b> {scan_record.created_at.strftime('%Y-%m-%d %H:%M')}",
                ParagraphStyle("Meta", parent=body_style, alignment=2)
            )
        ]
    ]
    header_table = Table(header_data, colWidths=[370, 178])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Paragraph(ui["report_subtitle"], subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=8))

    # Patient & System Metadata Table
    patient_display = patient_name or (scan_record.user.username if scan_record.user else "Anonymous / Guest Screening")
    status_label = ui["status_review"] if scan_record.is_uncertain else ui["status_conclusive"]
    meta_info = [
        [
            Paragraph(f"<b>{ui['patient']}:</b> {patient_display}", body_style),
            Paragraph(f"<b>{ui['backbone']}:</b> {ui['backbone_val']}", body_style),
        ],
        [
            Paragraph(f"<b>{ui['classification']}:</b> {ui['classification_val']}", body_style),
            Paragraph(f"<b>{ui['inference_status']}:</b> {status_label}", body_style),
        ]
    ]
    meta_table = Table(meta_info, colWidths=[274, 274])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), accent_bg),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 8))

    # Condition Details & Morphological Visuals
    cond_data = cond_catalog.get(scan_record.predicted_label, {
        "title": scan_record.predicted_label.replace("_", " ").title(),
        "desc": "A condition affecting scalp tissue or hair follicle structures.",
        "advice": "Consult a certified medical dermatologist for clinical examination."
    })

    # Prepare Clinical Photo
    image_element = None
    if scan_record.image and os.path.exists(scan_record.image.path):
        try:
            with Image.open(scan_record.image.path) as p_img:
                p_img.load()
            image_element = RLImage(scan_record.image.path, width=105, height=105)
        except Exception:
            image_element = Paragraph("[Image Unavailable]", body_style)
    else:
        image_element = Paragraph("[Image Unavailable]", body_style)

    # Prepare Grad-CAM Heatmap
    gradcam_element = None
    if scan_record.gradcam_base64:
        try:
            raw_bytes = base64.b64decode(scan_record.gradcam_base64)
            with Image.open(io.BytesIO(raw_bytes)) as p_img:
                p_img.load()
            gradcam_element = RLImage(io.BytesIO(raw_bytes), width=105, height=105)
        except Exception as e:
            print("GradCAM decode note:", e)

    if not gradcam_element and scan_record.image and os.path.exists(scan_record.image.path):
        try:
            from .ml_model import _load, _compute_gradcam
            model, grad_model, class_names = _load()
            if grad_model and scan_record.predicted_label in class_names:
                top_idx = class_names.index(scan_record.predicted_label)
                pil_img = Image.open(scan_record.image.path)
                b64_str = _compute_gradcam(pil_img, model, grad_model, top_idx)
                if b64_str:
                    raw_bytes = base64.b64decode(b64_str)
                    gradcam_element = RLImage(io.BytesIO(raw_bytes), width=105, height=105)
        except Exception as e:
            print("Grad-CAM generation note:", e)

    conf_color = "#10b981" if scan_record.confidence >= 75 else ("#f59e0b" if scan_record.confidence >= 50 else "#ef4444")

    from .ml_model import CLINICAL_URGENCY
    urgency = CLINICAL_URGENCY.get(scan_record.predicted_label, {})
    urgency_tier = urgency.get("tier", "ROUTINE")
    urgency_badge = urgency.get("badge", "Clinical Consultation")
    urgency_color = urgency.get("color", "#2563eb")

    status_str = ui["status_uncertain"] if scan_record.is_uncertain else ui["status_certain"]

    finding_html = f"""
    <b>{ui['primary_predicted']}</b><br/>
    <font size="12" color="#1e3a8a"><b>{cond_data['title']}</b></font><br/><br/>
    <b>{ui['ai_confidence']}:</b> <font color="{conf_color}"><b>{scan_record.confidence:.2f}%</b></font><br/>
    <b>{ui['clinical_triage']}:</b> <font color="{urgency_color}"><b>[{urgency_tier}] {urgency_badge}</b></font><br/>
    <b>Status:</b> {status_str}<br/><br/>
    <b>{ui['clinical_desc']}</b><br/>
    {cond_data['desc']}
    """
    finding_para = Paragraph(finding_html, body_style)

    if gradcam_element:
        col_img1 = [Paragraph(f"<b>{ui['clinical_photo']}</b>", body_style), Spacer(1, 2), image_element]
        col_img2 = [Paragraph(f"<b>{ui['gradcam_photo']}</b>", body_style), Spacer(1, 2), gradcam_element]
        overview_table = Table([[col_img1, col_img2, finding_para]], colWidths=[112, 112, 324])
    else:
        col_img1 = [Paragraph(f"<b>{ui['clinical_photo']}</b>", body_style), Spacer(1, 2), image_element]
        overview_table = Table([[col_img1, finding_para]], colWidths=[140, 408])

    overview_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 8))

    # Trichometry Morphometric Analysis
    tricho = scan_record.trichometry_metrics or {}
    if not tricho and scan_record.image and os.path.exists(scan_record.image.path):
        try:
            from .trichometry_engine import analyze_scalp_metrics
            with Image.open(scan_record.image.path) as p_img:
                tricho = analyze_scalp_metrics(p_img)
        except Exception as e:
            print("PDF Trichometry metrics note:", e)

    if tricho:
        elements.append(Paragraph(ui["tricho_heading"], section_heading))
        h_score = tricho.get("health_score", 0.0)
        h_stage = tricho.get("severity_stage", "Evaluated")
        h_col = tricho.get("stage_color", "#10b981")
        fl_pct = tricho.get("flakiness_pct", 0.0)
        fl_badge = tricho.get("flakiness_badge", "")
        fl_col = tricho.get("flake_color", "#10b981")
        er_pct = tricho.get("erythema_pct", 0.0)
        er_badge = tricho.get("erythema_badge", "")
        er_col = tricho.get("erythema_color", "#10b981")
        exp_pct = tricho.get("scalp_exposure_pct", 0.0)

        tricho_data = [
            [
                Paragraph(f"<b>{ui['health_score']}</b>", body_style),
                Paragraph(f"<font color='{h_col}'><b>{h_score}/100</b> ({h_stage})</font>", body_style),
                Paragraph(f"<b>{ui['flakiness']}</b>", body_style),
                Paragraph(f"<font color='{fl_col}'><b>{fl_pct}%</b> ({fl_badge})</font>", body_style),
            ],
            [
                Paragraph(f"<b>{ui['erythema']}</b>", body_style),
                Paragraph(f"<font color='{er_col}'><b>{er_pct}%</b> ({er_badge})</font>", body_style),
                Paragraph(f"<b>{ui['scalp_exposure']}</b>", body_style),
                Paragraph(f"<b>{exp_pct}%</b> {ui['hairline_parting']}", body_style),
            ]
        ]
        tricho_table = Table(tricho_data, colWidths=[120, 154, 120, 154])
        tricho_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), accent_bg),
            ("BOX", (0, 0), (-1, -1), 0.5, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(tricho_table)
        elements.append(Spacer(1, 8))

    # Differential Diagnosis Breakdown Table
    elements.append(Paragraph(ui["diff_heading"], section_heading))
    scores = scan_record.all_scores or {}
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    diff_table_data = [[ui["rank"], ui["condition_name"], ui["prob_score"], ui["diff_indicator"]]]
    for idx, (cls_name, score) in enumerate(sorted_scores[:6], start=1):
        friendly = cond_catalog.get(cls_name, {}).get("title", cls_name.replace("_", " ").title())
        indicator = ui["primary_match"] if idx == 1 else (ui["sig_prob"] if score > 10.0 else ui["low_prob"])
        diff_table_data.append([
            f"#{idx}",
            friendly,
            f"{score:.2f}%",
            indicator
        ])

    diff_table = Table(diff_table_data, colWidths=[45, 243, 110, 150])
    diff_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), font_bold),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
        ("TOPPADDING", (0, 0), (-1, 0), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, accent_bg]),
        ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("FONTNAME", (0, 1), (-1, -1), font_name),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
    ]))
    elements.append(diff_table)

    # Page 1 Footer Note
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        f"<font size='7.5' color='#64748b'>ScalpAI Clinical Diagnostic System • Page 1 of 2 • Official Screening Assessment</font>",
        ParagraphStyle("P1Foot", parent=body_style, alignment=1)
    ))

    # =========================================================================
    # PAGE BREAK -> PAGE 2: THERAPEUTIC REGIMEN & TRIAGE REFERRAL SLIP
    # =========================================================================
    elements.append(PageBreak())

    # Page 2 Header Banner
    p2_header_data = [
        [
            Paragraph(f"<b>{ui['page2_title']}</b>", title_style),
            Paragraph(
                f"<b>{ui['report_id']}:</b> #{scan_record.id:06d}<br/><b>Status:</b> Official Dossier",
                ParagraphStyle("P2Meta", parent=body_style, alignment=2)
            )
        ]
    ]
    p2_header_table = Table(p2_header_data, colWidths=[370, 178])
    p2_header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(p2_header_table)
    elements.append(Paragraph(ui["page2_subtitle"], subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=8))

    # Treatment Regimen Section
    from .trichometry_engine import get_treatment_recommendation
    tx = scan_record.treatment_summary or get_treatment_recommendation(scan_record.predicted_label)

    elements.append(Paragraph(ui["regimen_heading"], section_heading))
    ingredients = tx.get("ingredients", [])
    if ingredients:
        reg_rows = [[ui["ingredient"], ui["mechanism"]]]
        for ing in ingredients[:3]:
            reg_rows.append([
                Paragraph(f"<b>{ing.get('name', '')}</b>", bold_style),
                Paragraph(ing.get("role", ""), body_style)
            ])
        reg_table = Table(reg_rows, colWidths=[180, 368])
        reg_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), secondary_color),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), font_bold),
            ("FONTSIZE", (0, 0), (-1, 0), 8.5),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
            ("TOPPADDING", (0, 0), (-1, 0), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, accent_bg]),
            ("GRID", (0, 0), (-1, -1), 0.5, border_color),
            ("FONTNAME", (0, 1), (-1, -1), font_name),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("TOPPADDING", (0, 1), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
        ]))
        elements.append(reg_table)
        elements.append(Spacer(1, 6))

    wash_text = tx.get("wash_routine", "Maintain regular scalp cleansing with dermatological care.")
    avoid_text = tx.get("avoid", "Avoid harsh bleaches, excessive traction tension, and heat treatments.")
    care_box_data = [
        [
            Paragraph(f"<b>{ui['wash_routine']}</b> {wash_text}<br/><br/><b>{ui['avoid_items']}</b> {avoid_text}", body_style)
        ]
    ]
    care_box = Table(care_box_data, colWidths=[548])
    care_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#86efac")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(care_box)
    elements.append(Spacer(1, 10))

    # Clinician Triage Referral Handover Slip (Voucher / Doctor Referral Box)
    hash_seed = f"ScalpAI-{scan_record.id}-{scan_record.created_at.isoformat()}-{scan_record.predicted_label}"
    ref_code = f"REF-{scan_record.id:05d}-" + hashlib.sha256(hash_seed.encode()).hexdigest()[:6].upper()
    icd10_val = ICD10_CODES.get(scan_record.predicted_label, "L65.9 (Unspecified nonscarring hair loss)")

    referral_slip_data = [
        [
            Paragraph(f"<b>{ui['referral_heading']}</b>", ParagraphStyle("RefTitle", parent=title_style, fontSize=12, leading=15, textColor=primary_color)),
            Paragraph(f"<b>{ui['ref_id']}</b> <font color='#16a34a'><b>{ref_code}</b></font>", ParagraphStyle("RefCode", parent=body_style, alignment=2))
        ],
        [
            Paragraph(f"<b>{ui['ref_patient']}</b> {patient_display}<br/><b>{ui['ref_system']}</b>", body_style),
            Paragraph(f"<b>{ui['triage_priority']}</b> <font color='{urgency_color}'><b>[{urgency_tier}] {urgency_badge}</b></font>", body_style)
        ],
        [
            Paragraph(f"<b>{ui['presumptive_diag']}</b> {cond_data['title']}<br/><b>{ui['icd10']}</b> {icd10_val}", body_style),
            Paragraph(f"<b>Confidence:</b> {scan_record.confidence:.2f}% (Calibrated Softmax)", body_style)
        ],
        [
            Paragraph(
                f"<b>{ui['physician_checklist']}</b><br/>"
                f"{ui['check_diag']}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                f"{ui['check_tricho']}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                f"{ui['check_rx']}",
                body_style
            ),
            Paragraph("", body_style)
        ],
        [
            Paragraph(
                f"<br/><b>{ui['signature_line']}</b><br/>"
                f"_____________________________________________________ &nbsp;&nbsp;&nbsp;&nbsp; Date: ________________",
                body_style
            ),
            Paragraph(
                "<br/><font size='7' color='#94a3b8'>[ Clinical Stamp / Clinic Seal Box ]</font>",
                ParagraphStyle("Stamp", parent=body_style, alignment=1)
            )
        ]
    ]

    referral_slip = Table(referral_slip_data, colWidths=[360, 188])
    referral_slip.setStyle(TableStyle([
        ("SPAN", (0, 3), (1, 3)),
        ("BACKGROUND", (0, 0), (-1, -1), slip_bg),
        ("BOX", (0, 0), (-1, -1), 1.2, slip_border),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, slip_border),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(referral_slip)
    elements.append(Spacer(1, 10))

    # Medical & Legal Disclaimer Footer
    elements.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceBefore=2, spaceAfter=4))
    elements.append(Paragraph(f"<b>{ui['disclaimer_title']}</b> {ui['disclaimer_text']}", disclaimer_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(
        f"<font size='7.5' color='#64748b'>ScalpAI Clinical Diagnostic System • Page 2 of 2 • Doctor Handover Triage Slip</font>",
        ParagraphStyle("P2Foot", parent=body_style, alignment=1)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
