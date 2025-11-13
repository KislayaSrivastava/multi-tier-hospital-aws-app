"""
Database initialization script for Phase 2 - Multi-Tier Hospital Management System
This script populates sample data for medicines, pharmacies, and prescriptions
"""

from app import app
from models import db, Medicine, Pharmacy, Prescription, Doctor, Patient
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_medicines():
    """Initialize sample medicines"""
    medicines = [
        {
            'name': 'Paracetamol',
            'generic_name': 'Acetaminophen',
            'category': 'Pain Relief',
            'dosage_form': 'Tablet',
            'strength': '500mg',
            'manufacturer': 'GSK Pharmaceuticals',
            'description': 'Used for fever and mild to moderate pain relief'
        },
        {
            'name': 'Amoxicillin',
            'generic_name': 'Amoxicillin Trihydrate',
            'category': 'Antibiotic',
            'dosage_form': 'Capsule',
            'strength': '500mg',
            'manufacturer': 'Cipla Ltd',
            'description': 'Broad-spectrum antibiotic for bacterial infections'
        },
        {
            'name': 'Crocin',
            'generic_name': 'Paracetamol',
            'category': 'Pain Relief',
            'dosage_form': 'Tablet',
            'strength': '650mg',
            'manufacturer': 'GSK Pharmaceuticals',
            'description': 'Pain reliever and fever reducer'
        },
        {
            'name': 'Azithromycin',
            'generic_name': 'Azithromycin Dihydrate',
            'category': 'Antibiotic',
            'dosage_form': 'Tablet',
            'strength': '500mg',
            'manufacturer': 'Pfizer',
            'description': 'Macrolide antibiotic for respiratory infections'
        },
        {
            'name': 'Omeprazole',
            'generic_name': 'Omeprazole',
            'category': 'Gastrointestinal',
            'dosage_form': 'Capsule',
            'strength': '20mg',
            'manufacturer': 'Dr. Reddy\'s',
            'description': 'Proton pump inhibitor for acid reflux and ulcers'
        },
        {
            'name': 'Metformin',
            'generic_name': 'Metformin Hydrochloride',
            'category': 'Diabetes',
            'dosage_form': 'Tablet',
            'strength': '500mg',
            'manufacturer': 'Sun Pharma',
            'description': 'Oral diabetes medication for Type 2 diabetes'
        },
        {
            'name': 'Atorvastatin',
            'generic_name': 'Atorvastatin Calcium',
            'category': 'Cardiovascular',
            'dosage_form': 'Tablet',
            'strength': '10mg',
            'manufacturer': 'Pfizer',
            'description': 'Statin medication to lower cholesterol'
        },
        {
            'name': 'Cetirizine',
            'generic_name': 'Cetirizine Hydrochloride',
            'category': 'Antihistamine',
            'dosage_form': 'Tablet',
            'strength': '10mg',
            'manufacturer': 'UCB Pharma',
            'description': 'Antihistamine for allergies and hay fever'
        },
        {
            'name': 'Vitamin D3',
            'generic_name': 'Cholecalciferol',
            'category': 'Vitamin/Supplement',
            'dosage_form': 'Capsule',
            'strength': '60000 IU',
            'manufacturer': 'Abbott',
            'description': 'Vitamin D supplement for bone health'
        },
        {
            'name': 'Ibuprofen',
            'generic_name': 'Ibuprofen',
            'category': 'Pain Relief',
            'dosage_form': 'Tablet',
            'strength': '400mg',
            'manufacturer': 'Abbott',
            'description': 'NSAID for pain, inflammation, and fever'
        }
    ]

    count = 0
    for med_data in medicines:
        existing = Medicine.query.filter_by(name=med_data['name'], strength=med_data['strength']).first()
        if not existing:
            medicine = Medicine(**med_data)
            db.session.add(medicine)
            count += 1
            logger.info(f"Added medicine: {med_data['name']} ({med_data['strength']})")

    db.session.commit()
    logger.info(f"Initialized {count} medicines")
    return count

def init_pharmacies():
    """Initialize sample pharmacies in Bengaluru"""
    pharmacies = [
        {
            'name': 'Apollo Pharmacy - Koramangala',
            'address': '80 Feet Road, Koramangala 4th Block, Bengaluru, Karnataka 560034',
            'contact_number': '+91-80-41551234',
            'email': 'koramangala@apollopharmacy.in',
            'latitude': 12.9352,
            'longitude': 77.6245,
            'operating_hours': 'Mon-Sun: 24 Hours',
        },
        {
            'name': 'MedPlus Pharmacy - Indiranagar',
            'address': '100 Feet Road, Indiranagar, Bengaluru, Karnataka 560038',
            'contact_number': '+91-80-25201234',
            'email': 'indiranagar@medplusmart.com',
            'latitude': 12.9716,
            'longitude': 77.6412,
            'operating_hours': 'Mon-Sun: 8 AM - 11 PM',
        },
        {
            'name': 'Wellness Forever - Whitefield',
            'address': 'ITPL Main Road, Whitefield, Bengaluru, Karnataka 560066',
            'contact_number': '+91-80-28451234',
            'email': 'whitefield@wellnessforever.com',
            'latitude': 12.9698,
            'longitude': 77.7500,
            'operating_hours': 'Mon-Sun: 9 AM - 10 PM',
        },
        {
            'name': 'Fortis Healthcare Pharmacy',
            'address': '154/9, Bannerghatta Road, Bengaluru, Karnataka 560076',
            'contact_number': '+91-80-66214444',
            'email': 'pharmacy@fortishealthcare.com',
            'latitude': 12.9010,
            'longitude': 77.5950,
            'operating_hours': 'Mon-Sun: 24 Hours',
        },
        {
            'name': 'Manipal Hospital Pharmacy - HAL',
            'address': 'Old Airport Road, HAL, Bengaluru, Karnataka 560017',
            'contact_number': '+91-80-25023456',
            'email': 'hal@manipalhospitals.com',
            'latitude': 12.9611,
            'longitude': 77.6387,
            'operating_hours': 'Mon-Sun: 24 Hours',
        },
        {
            'name': '1mg Pharmacy - Jayanagar',
            'address': '9th Block, Jayanagar, Bengaluru, Karnataka 560069',
            'contact_number': '+91-80-26783456',
            'email': 'jayanagar@1mg.com',
            'latitude': 12.9250,
            'longitude': 77.5838,
            'operating_hours': 'Mon-Sun: 7 AM - 11 PM',
        }
    ]

    count = 0
    for pharm_data in pharmacies:
        existing = Pharmacy.query.filter_by(name=pharm_data['name']).first()
        if not existing:
            pharmacy = Pharmacy(**pharm_data)
            db.session.add(pharmacy)
            count += 1
            logger.info(f"Added pharmacy: {pharm_data['name']}")

    db.session.commit()
    logger.info(f"Initialized {count} pharmacies")
    return count

def init_sample_prescriptions():
    """Initialize sample prescriptions (if patients and doctors exist)"""
    # Check if we have data to work with
    patients = Patient.query.limit(5).all()
    doctors = Doctor.query.all()
    medicines = Medicine.query.limit(10).all()

    if not patients or not doctors or not medicines:
        logger.warning("Skipping prescription initialization - missing patients, doctors, or medicines")
        return 0

    sample_prescriptions = [
        {
            'patient': patients[0],
            'doctor': doctors[0],
            'medicine': medicines[0],
            'dosage': '1 tablet',
            'frequency': 'Three times daily',
            'duration': '5 days',
            'diagnosis': 'Fever and body ache',
            'instructions': 'Take after meals with water'
        },
        {
            'patient': patients[0] if len(patients) > 0 else patients[0],
            'doctor': doctors[1] if len(doctors) > 1 else doctors[0],
            'medicine': medicines[1] if len(medicines) > 1 else medicines[0],
            'dosage': '1 capsule',
            'frequency': 'Twice daily',
            'duration': '7 days',
            'diagnosis': 'Upper respiratory tract infection',
            'instructions': 'Complete the full course even if symptoms improve'
        }
    ]

    count = 0
    for i, presc_data in enumerate(sample_prescriptions):
        if i < len(patients):
            prescription = Prescription(
                patient_id=presc_data['patient'].id,
                doctor_id=presc_data['doctor'].id,
                medicine_id=presc_data['medicine'].id,
                dosage=presc_data['dosage'],
                frequency=presc_data['frequency'],
                duration=presc_data['duration'],
                diagnosis=presc_data.get('diagnosis'),
                instructions=presc_data.get('instructions'),
                prescribed_date=datetime.utcnow() - timedelta(days=i)
            )
            db.session.add(prescription)
            count += 1
            logger.info(f"Added prescription for patient: {presc_data['patient'].full_name}")

    db.session.commit()
    logger.info(f"Initialized {count} sample prescriptions")
    return count

def main():
    """Main initialization function"""
    with app.app_context():
        logger.info("Starting Phase 2 data initialization...")

        try:
            # Initialize medicines
            medicine_count = init_medicines()

            # Initialize pharmacies
            pharmacy_count = init_pharmacies()

            # Initialize sample prescriptions
            prescription_count = init_sample_prescriptions()

            logger.info("=" * 60)
            logger.info("Phase 2 Data Initialization Complete!")
            logger.info(f"  - Medicines added: {medicine_count}")
            logger.info(f"  - Pharmacies added: {pharmacy_count}")
            logger.info(f"  - Prescriptions added: {prescription_count}")
            logger.info("=" * 60)

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during initialization: {str(e)}")
            raise

if __name__ == '__main__':
    main()
