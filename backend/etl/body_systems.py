"""
Medical Knowledge Base - Body System Mappings.

Maps ICD-10 condition codes and medication codes to body systems
for visualization and explanation generation.
"""

# ICD-10 Condition Code → Body System Mapping
CONDITION_TO_BODY_SYSTEM = {
    # ============== CARDIOVASCULAR (I00-I99) ==============
    "I10": {"system": "Heart", "subsystem": "Blood Vessels", "description": "Pumps blood throughout your body"},
    "I11": {"system": "Heart", "subsystem": "Muscle", "description": "Pumps blood throughout your body"},
    "I13": {"system": "Heart", "subsystem": "Muscle", "description": "Pumps blood throughout your body"},
    "I20": {"system": "Heart", "subsystem": "Coronary Arteries", "description": "Pumps blood throughout your body"},
    "I21": {"system": "Heart", "subsystem": "Coronary Arteries", "description": "Pumps blood throughout your body"},
    "I25": {"system": "Heart", "subsystem": "Coronary Arteries", "description": "Pumps blood throughout your body"},
    "I48": {"system": "Heart", "subsystem": "Electrical System", "description": "Pumps blood throughout your body"},
    "I50": {"system": "Heart", "subsystem": "Muscle", "description": "Pumps blood throughout your body"},
    "I63": {"system": "Brain", "subsystem": "Blood Vessels", "description": "Controls all body functions"},
    "I70": {"system": "Blood Vessels", "subsystem": "Arteries", "description": "Carry blood throughout the body"},
    
    # ============== METABOLIC/ENDOCRINE (E00-E89) ==============
    "E10": {"system": "Pancreas", "subsystem": "Insulin Production", "description": "Produces insulin to control blood sugar"},
    "E11": {"system": "Pancreas", "subsystem": "Insulin Production", "description": "Produces insulin to control blood sugar"},
    "E13": {"system": "Pancreas", "subsystem": "Insulin Production", "description": "Produces insulin to control blood sugar"},
    "E66": {"system": "Metabolism", "subsystem": "Energy Balance", "description": "Converts food into energy"},
    "E78": {"system": "Liver", "subsystem": "Cholesterol Processing", "description": "Processes fats and removes toxins"},
    "E03": {"system": "Thyroid", "subsystem": "Hormone Production", "description": "Regulates metabolism"},
    "E05": {"system": "Thyroid", "subsystem": "Hormone Production", "description": "Regulates metabolism"},
    
    # ============== RESPIRATORY (J00-J99) ==============
    "J44": {"system": "Lungs", "subsystem": "Airways", "description": "Brings oxygen into your body"},
    "J45": {"system": "Lungs", "subsystem": "Airways", "description": "Brings oxygen into your body"},
    "J18": {"system": "Lungs", "subsystem": "Air Sacs", "description": "Brings oxygen into your body"},
    "J06": {"system": "Lungs", "subsystem": "Upper Airways", "description": "Brings oxygen into your body"},
    
    # ============== NEUROLOGICAL (G00-G99) ==============
    "G20": {"system": "Brain", "subsystem": "Motor Control", "description": "Controls all body functions"},
    "G30": {"system": "Brain", "subsystem": "Memory", "description": "Controls all body functions"},
    "G40": {"system": "Brain", "subsystem": "Electrical Activity", "description": "Controls all body functions"},
    "G43": {"system": "Brain", "subsystem": "Blood Vessels", "description": "Controls all body functions"},
    "G47": {"system": "Brain", "subsystem": "Sleep Centers", "description": "Controls all body functions"},
    
    # ============== MUSCULOSKELETAL (M00-M99) ==============
    "M54": {"system": "Spine", "subsystem": "Vertebrae", "description": "Supports your body and protects nerves"},
    "M17": {"system": "Joints", "subsystem": "Knees", "description": "Allow movement"},
    "M16": {"system": "Joints", "subsystem": "Hips", "description": "Allow movement"},
    "M79": {"system": "Muscles", "subsystem": "Soft Tissue", "description": "Enable movement"},
    "M81": {"system": "Bones", "subsystem": "Density", "description": "Support and protect your body"},
    
    # ============== MENTAL HEALTH (F00-F99) ==============
    "F32": {"system": "Brain", "subsystem": "Mood Centers", "description": "Controls all body functions"},
    "F33": {"system": "Brain", "subsystem": "Mood Centers", "description": "Controls all body functions"},
    "F41": {"system": "Brain", "subsystem": "Stress Response", "description": "Controls all body functions"},
    "F17": {"system": "Brain", "subsystem": "Reward Centers", "description": "Controls all body functions"},
    
    # ============== DIGESTIVE (K00-K95) ==============
    "K21": {"system": "Stomach", "subsystem": "Acid Production", "description": "Digests food"},
    "K50": {"system": "Intestines", "subsystem": "Large Intestine", "description": "Absorbs nutrients"},
    "K51": {"system": "Intestines", "subsystem": "Large Intestine", "description": "Absorbs nutrients"},
    "K70": {"system": "Liver", "subsystem": "Cells", "description": "Processes nutrients and removes toxins"},
    "K76": {"system": "Liver", "subsystem": "Cells", "description": "Processes nutrients and removes toxins"},
    
    # ============== KIDNEY/URINARY (N00-N99) ==============
    "N18": {"system": "Kidneys", "subsystem": "Filtering", "description": "Filter waste from your blood"},
    "N17": {"system": "Kidneys", "subsystem": "Filtering", "description": "Filter waste from your blood"},
    "N40": {"system": "Prostate", "subsystem": "Gland", "description": "Part of the urinary system"},
    
    # ============== COMPLICATIONS ==============
    "H36": {"system": "Eyes", "subsystem": "Blood Vessels", "description": "Enable vision"},
    "H35": {"system": "Eyes", "subsystem": "Retina", "description": "Enable vision"},
    "H40": {"system": "Eyes", "subsystem": "Pressure", "description": "Enable vision"},
    "H25": {"system": "Eyes", "subsystem": "Lens", "description": "Enable vision"},
    
    # ============== CANCER (C00-D49) ==============
    "C34": {"system": "Lungs", "subsystem": "Tissue", "description": "Brings oxygen into your body"},
    "C50": {"system": "Breast", "subsystem": "Tissue", "description": "Mammary glands"},
    "C61": {"system": "Prostate", "subsystem": "Gland", "description": "Part of the reproductive system"},
    "C18": {"system": "Intestines", "subsystem": "Large Intestine", "description": "Absorbs nutrients"},
}


# Medication Code → Target Body System Mapping
MEDICATION_TO_TARGET = {
    # ============== BLOOD THINNERS ==============
    "B01AA03": {"target": "Blood", "action": "Prevents clotting"},  # Warfarin
    "B01AF01": {"target": "Blood", "action": "Prevents clotting"},  # Rivaroxaban
    "B01AF02": {"target": "Blood", "action": "Prevents clotting"},  # Apixaban
    "B01AC06": {"target": "Blood", "action": "Prevents clotting"},  # Aspirin (as antiplatelet)
    
    # ============== DIABETES MEDICATIONS ==============
    "A10BA02": {"target": "Liver", "action": "Reduces glucose production"},  # Metformin
    "A10AB01": {"target": "Body Cells", "action": "Enables glucose uptake"},  # Insulin (regular)
    "A10AE04": {"target": "Body Cells", "action": "Enables glucose uptake"},  # Insulin glargine
    "A10BK01": {"target": "Kidneys", "action": "Removes excess glucose"},     # Empagliflozin
    "A10BJ02": {"target": "Pancreas", "action": "Stimulates insulin release"}, # Liraglutide
    
    # ============== HEART MEDICATIONS ==============
    "C07AB02": {"target": "Heart", "action": "Slows heart rate"},           # Metoprolol
    "C07AB03": {"target": "Heart", "action": "Slows heart rate"},           # Atenolol
    "C09AA02": {"target": "Blood Vessels", "action": "Relaxes vessels"},    # Enalapril
    "C09AA03": {"target": "Blood Vessels", "action": "Relaxes vessels"},    # Lisinopril
    "C09CA01": {"target": "Blood Vessels", "action": "Relaxes vessels"},    # Losartan
    "C03CA01": {"target": "Kidneys", "action": "Removes excess fluid"},     # Furosemide
    "C03AA03": {"target": "Kidneys", "action": "Removes excess fluid"},     # Hydrochlorothiazide
    "C08CA01": {"target": "Blood Vessels", "action": "Relaxes vessels"},    # Amlodipine
    "C01BD01": {"target": "Heart", "action": "Regulates rhythm"},           # Amiodarone
    
    # ============== CHOLESTEROL MEDICATIONS ==============
    "C10AA01": {"target": "Liver", "action": "Reduces cholesterol production"},  # Simvastatin
    "C10AA05": {"target": "Liver", "action": "Reduces cholesterol production"},  # Atorvastatin
    "C10AA07": {"target": "Liver", "action": "Reduces cholesterol production"},  # Rosuvastatin
    
    # ============== RESPIRATORY MEDICATIONS ==============
    "R03AC02": {"target": "Lungs", "action": "Opens airways"},              # Salbutamol/Albuterol
    "R03AK06": {"target": "Lungs", "action": "Opens airways, reduces inflammation"},  # Fluticasone/salmeterol
    "R03BB04": {"target": "Lungs", "action": "Opens airways"},              # Tiotropium
    
    # ============== PAIN/INFLAMMATION ==============
    "N02BE01": {"target": "Brain", "action": "Reduces pain signals"},       # Paracetamol/Acetaminophen
    "M01AE01": {"target": "Body", "action": "Reduces inflammation"},        # Ibuprofen
    "N02AX02": {"target": "Brain", "action": "Reduces pain signals"},       # Tramadol
    
    # ============== MENTAL HEALTH MEDICATIONS ==============
    "N06AB06": {"target": "Brain", "action": "Balances mood chemicals"},    # Sertraline
    "N06AB04": {"target": "Brain", "action": "Balances mood chemicals"},    # Citalopram
    "N06AB10": {"target": "Brain", "action": "Balances mood chemicals"},    # Escitalopram
    "N05AH04": {"target": "Brain", "action": "Balances brain chemicals"},   # Quetiapine
    
    # ============== THYROID ==============
    "H03AA01": {"target": "Thyroid", "action": "Replaces thyroid hormone"}, # Levothyroxine
    
    # ============== STOMACH/GI ==============
    "A02BC01": {"target": "Stomach", "action": "Reduces acid production"},  # Omeprazole
    "A02BC02": {"target": "Stomach", "action": "Reduces acid production"},  # Pantoprazole
}


def get_body_system_for_condition(icd_code: str) -> dict:
    """
    Look up body system for an ICD-10 code.
    
    Tries exact match first, then 3-character category.
    
    Args:
        icd_code: ICD-10 diagnosis code
        
    Returns:
        Dictionary with system, subsystem, and description
    """
    # Try exact match
    if icd_code in CONDITION_TO_BODY_SYSTEM:
        return CONDITION_TO_BODY_SYSTEM[icd_code]
    
    # Try 3-character category
    prefix = icd_code[:3] if len(icd_code) >= 3 else icd_code
    if prefix in CONDITION_TO_BODY_SYSTEM:
        return CONDITION_TO_BODY_SYSTEM[prefix]
    
    # Unknown
    return {
        "system": "Body",
        "subsystem": "Unknown",
        "description": "Part of your body"
    }


def get_target_for_medication(med_code: str) -> dict:
    """
    Look up target body system for a medication code.
    
    Args:
        med_code: ATC or RxNorm medication code
        
    Returns:
        Dictionary with target and action
    """
    if med_code in MEDICATION_TO_TARGET:
        return MEDICATION_TO_TARGET[med_code]
    
    return {
        "target": "Body",
        "action": "Helps with treatment"
    }
