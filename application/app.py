from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_caching import Cache
from config import Config
from models import db, Doctor, Patient, Medicine, Prescription, Pharmacy
from datetime import datetime
from geopy.distance import geodesic
import os
import logging

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
cache = Cache(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return Doctor.query.get(int(user_id))

def init_database():
    """Initialize database and create default doctor accounts"""
    with app.app_context():
        # Create all tables
        db.create_all()
        logger.info("Database tables created successfully")
        
        # Create default doctor accounts if they don't exist
        default_doctors = [
            {
                'username': 'kaashvi',
                'name': 'Dr. Kaashvi Srivastava',
                'password': 'kaashvi123',
                'specialization': 'General Medicine',
                'contact': '+91-9876543210',
                'email': 'kaashvi@sksmedical.com'
            },
            {
                'username': 'yuvaan',
                'name': 'Dr. Yuvaan Srivastava',
                'password': 'yuvaan123',
                'specialization': 'Pediatrics',
                'contact': '+91-9876543211',
                'email': 'yuvaan@sksmedical.com'
            },
            {
                'username': 'karthik',
                'name': 'Dr. Karthik',
                'password': 'karthik123',
                'specialization': 'Cardiology',
                'contact': '+91-9876543212',
                'email': 'karthik@sksmedical.com'
            },
            {
                'username': 'omkar',
                'name': 'Dr. Omkar',
                'password': 'omkar123',
                'specialization': 'Orthopedics',
                'contact': '+91-9876543213',
                'email': 'omkar@sksmedical.com'
            }
        ]
        
        for doc_data in default_doctors:
            existing_doctor = Doctor.query.filter_by(username=doc_data['username']).first()
            if not existing_doctor:
                doctor = Doctor(
                    username=doc_data['username'],
                    name=doc_data['name'],
                    specialization=doc_data['specialization'],
                    contact=doc_data.get('contact'),
                    email=doc_data.get('email')
                )
                doctor.set_password(doc_data['password'])
                db.session.add(doctor)
                logger.info(f"Created doctor account: {doc_data['username']}")
        
        try:
            db.session.commit()
            logger.info("Database initialized successfully!")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error initializing database: {str(e)}")

# Routes

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in, else login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Doctor login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter both username and password', 'warning')
            return render_template('login.html')
        
        doctor = Doctor.query.filter_by(username=username).first()
        
        if doctor and doctor.check_password(password):
            login_user(doctor)
            logger.info(f"Doctor logged in: {doctor.username}")
            flash(f'Welcome back, {doctor.name}!', 'success')
            
            # Redirect to next page if specified
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout current doctor"""
    logger.info(f"Doctor logged out: {current_user.username}")
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page with statistics"""
    total_patients = Patient.query.count()
    my_patients = Patient.query.filter_by(registered_by=current_user.id).count()
    recent_patients = Patient.query.order_by(Patient.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         total_patients=total_patients,
                         my_patients=my_patients,
                         recent_patients=recent_patients)

@app.route('/patients')
@login_required
def patients():
    """Patient list page with search functionality"""
    search_query = request.args.get('search', '').strip()
    
    if search_query:
        # Search by first name, last name, or contact number
        patients_list = Patient.query.filter(
            db.or_(
                Patient.first_name.ilike(f'%{search_query}%'),
                Patient.last_name.ilike(f'%{search_query}%'),
                Patient.contact_number.ilike(f'%{search_query}%')
            )
        ).order_by(Patient.created_at.desc()).all()
        logger.info(f"Search performed: '{search_query}', results: {len(patients_list)}")
    else:
        patients_list = Patient.query.order_by(Patient.created_at.desc()).all()
    
    return render_template('patients.html', patients=patients_list, search_query=search_query)

@app.route('/patients/new', methods=['GET', 'POST'])
@login_required
def new_patient():
    """Add new patient"""
    if request.method == 'POST':
        try:
            # Parse date of birth
            dob_str = request.form.get('date_of_birth')
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
            
            if not dob:
                flash('Please provide a valid date of birth', 'danger')
                return render_template('patient_form.html', patient=None)
            
            patient = Patient(
                first_name=request.form.get('first_name', '').strip(),
                last_name=request.form.get('last_name', '').strip(),
                date_of_birth=dob,
                gender=request.form.get('gender'),
                contact_number=request.form.get('contact_number', '').strip(),
                email=request.form.get('email', '').strip() or None,
                address=request.form.get('address', '').strip() or None,
                blood_group=request.form.get('blood_group') or None,
                medical_history=request.form.get('medical_history', '').strip() or None,
                allergies=request.form.get('allergies', '').strip() or None,
                current_medications=request.form.get('current_medications', '').strip() or None,
                emergency_contact_name=request.form.get('emergency_contact_name', '').strip() or None,
                emergency_contact_number=request.form.get('emergency_contact_number', '').strip() or None,
                registered_by=current_user.id
            )
            
            db.session.add(patient)
            db.session.commit()
            
            logger.info(f"New patient registered: {patient.full_name} (ID: {patient.id})")
            flash(f'Patient {patient.full_name} registered successfully!', 'success')
            return redirect(url_for('patient_detail', patient_id=patient.id))
            
        except ValueError as e:
            flash('Invalid date format. Please use YYYY-MM-DD format.', 'danger')
            logger.error(f"Date parsing error: {str(e)}")
        except Exception as e:
            db.session.rollback()
            flash(f'Error registering patient: {str(e)}', 'danger')
            logger.error(f"Error creating patient: {str(e)}")
    
    return render_template('patient_form.html', patient=None)

@app.route('/patients/<int:patient_id>')
@login_required
def patient_detail(patient_id):
    """View patient details"""
    patient = Patient.query.get_or_404(patient_id)
    return render_template('patient_detail.html', patient=patient)

@app.route('/patients/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    """Edit patient information"""
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        try:
            # Parse date of birth
            dob_str = request.form.get('date_of_birth')
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
            
            if not dob:
                flash('Please provide a valid date of birth', 'danger')
                return render_template('patient_form.html', patient=patient)
            
            # Update patient information
            patient.first_name = request.form.get('first_name', '').strip()
            patient.last_name = request.form.get('last_name', '').strip()
            patient.date_of_birth = dob
            patient.gender = request.form.get('gender')
            patient.contact_number = request.form.get('contact_number', '').strip()
            patient.email = request.form.get('email', '').strip() or None
            patient.address = request.form.get('address', '').strip() or None
            patient.blood_group = request.form.get('blood_group') or None
            patient.medical_history = request.form.get('medical_history', '').strip() or None
            patient.allergies = request.form.get('allergies', '').strip() or None
            patient.current_medications = request.form.get('current_medications', '').strip() or None
            patient.emergency_contact_name = request.form.get('emergency_contact_name', '').strip() or None
            patient.emergency_contact_number = request.form.get('emergency_contact_number', '').strip() or None
            patient.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Patient updated: {patient.full_name} (ID: {patient.id})")
            flash(f'Patient {patient.full_name} updated successfully!', 'success')
            return redirect(url_for('patient_detail', patient_id=patient.id))
            
        except ValueError as e:
            flash('Invalid date format. Please use YYYY-MM-DD format.', 'danger')
            logger.error(f"Date parsing error: {str(e)}")
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating patient: {str(e)}', 'danger')
            logger.error(f"Error updating patient: {str(e)}")
    
    return render_template('patient_form.html', patient=patient)

# ============================================================================
# Phase 2 Routes: Medicine Management
# ============================================================================

@app.route('/medicines')
@login_required
def medicines():
    """List all medicines"""
    search_query = request.args.get('search', '').strip()

    if search_query:
        medicines_list = Medicine.query.filter(
            db.or_(
                Medicine.name.ilike(f'%{search_query}%'),
                Medicine.generic_name.ilike(f'%{search_query}%'),
                Medicine.category.ilike(f'%{search_query}%')
            )
        ).filter_by(is_active=True).order_by(Medicine.name).all()
    else:
        medicines_list = Medicine.query.filter_by(is_active=True).order_by(Medicine.name).all()

    return render_template('medicines.html', medicines=medicines_list, search_query=search_query)

@app.route('/medicines/new', methods=['GET', 'POST'])
@login_required
def new_medicine():
    """Add new medicine"""
    if request.method == 'POST':
        try:
            medicine = Medicine(
                name=request.form.get('name', '').strip(),
                generic_name=request.form.get('generic_name', '').strip() or None,
                description=request.form.get('description', '').strip() or None,
                category=request.form.get('category', '').strip() or None,
                dosage_form=request.form.get('dosage_form', '').strip() or None,
                strength=request.form.get('strength', '').strip() or None,
                manufacturer=request.form.get('manufacturer', '').strip() or None
            )

            db.session.add(medicine)
            db.session.commit()

            logger.info(f"New medicine added: {medicine.name} (ID: {medicine.id})")
            flash(f'Medicine {medicine.name} added successfully!', 'success')
            return redirect(url_for('medicines'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding medicine: {str(e)}', 'danger')
            logger.error(f"Error creating medicine: {str(e)}")

    return render_template('medicine_form.html', medicine=None)

@app.route('/medicines/<int:medicine_id>')
@login_required
def medicine_detail(medicine_id):
    """View medicine details"""
    medicine = Medicine.query.get_or_404(medicine_id)
    prescription_count = Prescription.query.filter_by(medicine_id=medicine_id).count()
    return render_template('medicine_detail.html', medicine=medicine, prescription_count=prescription_count)

@app.route('/medicines/<int:medicine_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_medicine(medicine_id):
    """Edit medicine information"""
    medicine = Medicine.query.get_or_404(medicine_id)

    if request.method == 'POST':
        try:
            medicine.name = request.form.get('name', '').strip()
            medicine.generic_name = request.form.get('generic_name', '').strip() or None
            medicine.description = request.form.get('description', '').strip() or None
            medicine.category = request.form.get('category', '').strip() or None
            medicine.dosage_form = request.form.get('dosage_form', '').strip() or None
            medicine.strength = request.form.get('strength', '').strip() or None
            medicine.manufacturer = request.form.get('manufacturer', '').strip() or None
            medicine.updated_at = datetime.utcnow()

            db.session.commit()

            logger.info(f"Medicine updated: {medicine.name} (ID: {medicine.id})")
            flash(f'Medicine {medicine.name} updated successfully!', 'success')
            return redirect(url_for('medicine_detail', medicine_id=medicine.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating medicine: {str(e)}', 'danger')
            logger.error(f"Error updating medicine: {str(e)}")

    return render_template('medicine_form.html', medicine=medicine)

# ============================================================================
# Phase 2 Routes: Prescription Management
# ============================================================================

@app.route('/prescriptions')
@login_required
def prescriptions():
    """List all prescriptions"""
    patient_id = request.args.get('patient_id', type=int)

    if patient_id:
        prescriptions_list = Prescription.query.filter_by(patient_id=patient_id).order_by(Prescription.prescribed_date.desc()).all()
    else:
        prescriptions_list = Prescription.query.order_by(Prescription.prescribed_date.desc()).limit(50).all()

    return render_template('prescriptions.html', prescriptions=prescriptions_list)

@app.route('/prescriptions/new', methods=['GET', 'POST'])
@login_required
def new_prescription():
    """Create new prescription"""
    patient_id = request.args.get('patient_id', type=int)
    patient = Patient.query.get(patient_id) if patient_id else None

    if request.method == 'POST':
        try:
            prescription = Prescription(
                patient_id=request.form.get('patient_id', type=int),
                doctor_id=current_user.id,
                medicine_id=request.form.get('medicine_id', type=int),
                dosage=request.form.get('dosage', '').strip(),
                frequency=request.form.get('frequency', '').strip(),
                duration=request.form.get('duration', '').strip(),
                instructions=request.form.get('instructions', '').strip() or None,
                diagnosis=request.form.get('diagnosis', '').strip() or None
            )

            db.session.add(prescription)
            db.session.commit()

            logger.info(f"New prescription created (ID: {prescription.id}) for patient {prescription.patient_id}")
            flash('Prescription created successfully!', 'success')
            return redirect(url_for('prescription_detail', prescription_id=prescription.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating prescription: {str(e)}', 'danger')
            logger.error(f"Error creating prescription: {str(e)}")

    patients_list = Patient.query.order_by(Patient.first_name).all()
    medicines_list = Medicine.query.filter_by(is_active=True).order_by(Medicine.name).all()

    return render_template('prescription_form.html',
                         prescription=None,
                         patient=patient,
                         patients=patients_list,
                         medicines=medicines_list)

@app.route('/prescriptions/<int:prescription_id>')
@login_required
def prescription_detail(prescription_id):
    """View prescription details"""
    prescription = Prescription.query.get_or_404(prescription_id)
    return render_template('prescription_detail.html', prescription=prescription)

# ============================================================================
# Phase 2 Routes: Pharmacy Management & Finder
# ============================================================================

@app.route('/pharmacies')
@login_required
@cache.cached(timeout=300, query_string=True)
def pharmacies():
    """List all pharmacies"""
    pharmacies_list = Pharmacy.query.filter_by(is_active=True).order_by(Pharmacy.name).all()
    return render_template('pharmacies.html', pharmacies=pharmacies_list)

@app.route('/pharmacies/find-nearest')
@login_required
def find_nearest_pharmacies():
    """Find nearest pharmacies based on coordinates"""
    # Get coordinates from query params or use hospital location
    latitude = request.args.get('lat', type=float, default=app.config['HOSPITAL_LATITUDE'])
    longitude = request.args.get('lng', type=float, default=app.config['HOSPITAL_LONGITUDE'])

    user_location = (latitude, longitude)

    # Get all active pharmacies
    all_pharmacies = Pharmacy.query.filter_by(is_active=True).all()

    # Calculate distances and sort
    pharmacies_with_distance = []
    for pharmacy in all_pharmacies:
        pharmacy_location = (pharmacy.latitude, pharmacy.longitude)
        distance = geodesic(user_location, pharmacy_location).kilometers
        pharmacies_with_distance.append({
            'pharmacy': pharmacy,
            'distance': round(distance, 2)
        })

    # Sort by distance and get nearest 3
    pharmacies_with_distance.sort(key=lambda x: x['distance'])
    nearest_pharmacies = pharmacies_with_distance[:3]

    return render_template('pharmacy_finder.html',
                         nearest_pharmacies=nearest_pharmacies,
                         user_lat=latitude,
                         user_lng=longitude,
                         hospital_lat=app.config['HOSPITAL_LATITUDE'],
                         hospital_lng=app.config['HOSPITAL_LONGITUDE'])

@app.route('/pharmacies/new', methods=['GET', 'POST'])
@login_required
def new_pharmacy():
    """Add new pharmacy"""
    if request.method == 'POST':
        try:
            pharmacy = Pharmacy(
                name=request.form.get('name', '').strip(),
                address=request.form.get('address', '').strip(),
                contact_number=request.form.get('contact_number', '').strip(),
                email=request.form.get('email', '').strip() or None,
                latitude=float(request.form.get('latitude')),
                longitude=float(request.form.get('longitude')),
                operating_hours=request.form.get('operating_hours', '').strip() or None
            )

            db.session.add(pharmacy)
            db.session.commit()

            # Clear cache
            cache.clear()

            logger.info(f"New pharmacy added: {pharmacy.name} (ID: {pharmacy.id})")
            flash(f'Pharmacy {pharmacy.name} added successfully!', 'success')
            return redirect(url_for('pharmacies'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding pharmacy: {str(e)}', 'danger')
            logger.error(f"Error creating pharmacy: {str(e)}")

    return render_template('pharmacy_form.html', pharmacy=None)

@app.route('/pharmacies/<int:pharmacy_id>')
@login_required
def pharmacy_detail(pharmacy_id):
    """View pharmacy details"""
    pharmacy = Pharmacy.query.get_or_404(pharmacy_id)

    # Calculate distance from hospital
    hospital_location = (app.config['HOSPITAL_LATITUDE'], app.config['HOSPITAL_LONGITUDE'])
    pharmacy_location = (pharmacy.latitude, pharmacy.longitude)
    distance = round(geodesic(hospital_location, pharmacy_location).kilometers, 2)

    return render_template('pharmacy_detail.html', pharmacy=pharmacy, distance=distance)

@app.route('/pharmacies/<int:pharmacy_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_pharmacy(pharmacy_id):
    """Edit pharmacy information"""
    pharmacy = Pharmacy.query.get_or_404(pharmacy_id)

    if request.method == 'POST':
        try:
            pharmacy.name = request.form.get('name', '').strip()
            pharmacy.address = request.form.get('address', '').strip()
            pharmacy.contact_number = request.form.get('contact_number', '').strip()
            pharmacy.email = request.form.get('email', '').strip() or None
            pharmacy.latitude = float(request.form.get('latitude'))
            pharmacy.longitude = float(request.form.get('longitude'))
            pharmacy.operating_hours = request.form.get('operating_hours', '').strip() or None
            pharmacy.updated_at = datetime.utcnow()

            db.session.commit()

            # Clear cache
            cache.clear()

            logger.info(f"Pharmacy updated: {pharmacy.name} (ID: {pharmacy.id})")
            flash(f'Pharmacy {pharmacy.name} updated successfully!', 'success')
            return redirect(url_for('pharmacy_detail', pharmacy_id=pharmacy.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating pharmacy: {str(e)}', 'danger')
            logger.error(f"Error updating pharmacy: {str(e)}")

    return render_template('pharmacy_form.html', pharmacy=pharmacy)

# Error handlers

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    flash('The page you are looking for does not exist.', 'warning')
    return redirect(url_for('dashboard'))

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    logger.error(f"Internal server error: {str(error)}")
    flash('An internal error occurred. Please try again later.', 'danger')
    return redirect(url_for('dashboard'))

# Application startup

if __name__ == '__main__':
    init_database()
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting SKS Medical Center application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)