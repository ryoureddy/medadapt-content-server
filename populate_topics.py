import database

def populate_basic_topic_mappings():
    """Populate database with basic medical topic relationships"""
    # Cardiovascular System
    database.add_topic_mapping("cardiac cycle", "cardiovascular physiology", "cardiology", 
        "The sequence of events during a single heartbeat")
    database.add_topic_mapping("heart valves", "cardiac anatomy", "cardiology", 
        "Structures that control blood flow through the heart")
    database.add_topic_mapping("cardiac output", "cardiovascular physiology", "cardiology", 
        "Volume of blood pumped by the heart per minute")
    database.add_topic_mapping("ECG", "cardiovascular diagnostics", "cardiology", 
        "Electrocardiogram for recording heart electrical activity")
    database.add_topic_mapping("heart sounds", "cardiac auscultation", "cardiology", 
        "Sounds produced by the heart during the cardiac cycle")
    
    # Respiratory System
    database.add_topic_mapping("pulmonary ventilation", "respiratory physiology", "pulmonology", 
        "Movement of air into and out of the lungs")
    database.add_topic_mapping("gas exchange", "respiratory physiology", "pulmonology", 
        "Transfer of oxygen and carbon dioxide between lungs and blood")
    database.add_topic_mapping("pneumothorax", "respiratory pathology", "pulmonology", 
        "Presence of air in the pleural cavity")
    database.add_topic_mapping("respiratory muscles", "respiratory anatomy", "pulmonology", 
        "Muscles involved in breathing")
    
    # Musculoskeletal System
    database.add_topic_mapping("forearm muscles", "upper limb anatomy", "orthopedics", 
        "Muscles located in the forearm")
    database.add_topic_mapping("forearm nerves", "upper limb innervation", "neurology", 
        "Nerves supplying the forearm")
    database.add_topic_mapping("forearm arteries", "upper limb vasculature", "vascular", 
        "Arteries supplying the forearm")
    database.add_topic_mapping("upper limb innervation", "peripheral nervous system", "neurology", 
        "Nerve supply to the upper limb")
    database.add_topic_mapping("muscle contraction", "muscle physiology", "physiology", 
        "Process by which muscles generate force")
    
    # Nervous System
    database.add_topic_mapping("brain anatomy", "neuroanatomy", "neurology", 
        "Structural organization of the brain")
    database.add_topic_mapping("spinal cord", "neuroanatomy", "neurology", 
        "Part of the central nervous system within the vertebral column")
    database.add_topic_mapping("cranial nerves", "peripheral nervous system", "neurology", 
        "Twelve pairs of nerves emerging directly from the brain")
    
    # Add parent-child relationships for broader categories
    database.add_topic_mapping("cardiovascular physiology", "physiology", "cardiology", 
        "Study of heart and blood vessel function")
    database.add_topic_mapping("respiratory physiology", "physiology", "pulmonology", 
        "Study of respiratory system function")
    database.add_topic_mapping("neuroanatomy", "anatomy", "neurology", 
        "Study of nervous system structure")
    database.add_topic_mapping("upper limb anatomy", "anatomy", "orthopedics", 
        "Study of upper limb structure")
    
    print("Basic topic mappings populated successfully.")

if __name__ == "__main__":
    # Initialize database
    database.initialize_database()
    
    # Populate topic mappings
    populate_basic_topic_mappings() 