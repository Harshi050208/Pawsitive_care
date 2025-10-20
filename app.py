from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from datetime import date, datetime
from functools import wraps
import os
import json


app = Flask(__name__)
app.secret_key = "your_secret_key"

# Files and Data
DATA_FILE = "users.json"
FEATURES_FILE = "animal_data.json"
DOCUMENT_RECORDS_FILE = os.path.join('static', 'document_records.json')

# Upload configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}



# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user' not in session:
#             flash("Please log in first!", "warning")
#             return redirect(url_for('login'))
#         return f(*args, **kwargs)
#     return decorated_function


def load_users():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        default_users = {
            "admin": {"password": "password", "type": "admin"},
            "user": {"password": "12345", "type": "user"}
        }
        save_users(default_users)
        return default_users
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}

def save_users(users):
    with open(DATA_FILE, "w") as file:
        json.dump(users, file, indent=4)

def load_animal_data():
    if not os.path.exists(FEATURES_FILE):
        return {}
    try:
        with open(FEATURES_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}

def save_animal_data(data):
    with open(FEATURES_FILE, "w") as file:
        json.dump(data, file, indent=4)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_document/<animal_id>', methods=['POST'])
def upload_document(animal_id):
    if 'document' not in request.files:
        flash('No file part')
        return redirect(url_for('animal_features', animal_id=animal_id))

    file = request.files['document']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('animal_features', animal_id=animal_id))

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{animal_id}_{file.filename}")
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        # ✅ Save file metadata in document_records.json
        json_path = os.path.join('static', 'document_records.json')
        try:
            with open(json_path, 'r') as f:
                records = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            records = {}

        records[animal_id] = {
            'filename': filename,
            'uploaded_on': date.today().isoformat()
        }

        with open(json_path, 'w') as f:
            json.dump(records, f, indent=4)

        flash('Document uploaded successfully.')
    else:
        flash('File type not allowed.')

    return redirect(url_for('animal_features', animal_id=animal_id))



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/category/cow')
def cow_category():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('cow.html')

@app.route('/category/sheep')
def sheep_category():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('sheep.html')


@app.route('/category/goat')
def goat_category():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('goat.html')


@app.route('/category/chicken')
def chicken_category():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('chicken.html')


@app.route('/category/pig')
def pig_category():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('pig.html')


@app.route('/category/horse')
def horse_category():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('horse.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('signup'))

        users = load_users()
        if username in users:
            flash("Username already exists!", "danger")
            return redirect(url_for('signup'))

        users[username] = {"password": password, "type": "user"}
        save_users(users)
        flash("Account created successfully!", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()

        if username in users and users[username]['password'] == password:
            session['user'] = username
            return redirect(url_for('category'))
        else:
            flash("Invalid credentials!", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('login'))

@app.route('/category')
def category():
    if 'user' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('login'))
    return render_template('category.html', username=session['user'])


@app.route('/animal/<animal_id>', methods=['GET', 'POST'])
def animal_features(animal_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    animal_data = load_animal_data()
    recommendation = None

    # Initialize dynamic options if not present
    if "dynamic_options" not in animal_data:
        animal_data["dynamic_options"] = {
            "health_status": ["UnderObservation", "Stable", "CriticalCondition"],
            "breeding_status": ["ReadyforBreeding", "NotReadyforBreeding", "CannotBreed"],
            "lifestyle": ["ActiveandGrazing", "Sedentary", "UsedforLabour"],
            "report_status": ["RequiresMedicalAttention", "LethargicBehavior", "IrregularEatingHabits", "ActiveandEnergetic"]
        }

    # Ensure the animal exists with default values
    if animal_id not in animal_data:
        animal_data[animal_id] = {
            "dob": "Unknown",
            "health_status": "Unknown",
            "breeding_status": "Unknown",
            "region": "Unknown",
            "prev_disease_history": "None",
            "environmental_risk": "Low",
            "lifestyle": "Unknown",
            "report_status": "Unknown",
            "temperature": 36.0,
            "vaccination": {
                "last_vaccine_date": "Not Recorded",
                "next_due_date": "Not Recorded",
                "status": "Pending"
            },
            "custom_inputs": {}
        }
        save_animal_data(animal_data)

    # Handle form submission
    if request.method == 'POST':
        print("Received form data:", request.form)
        try:
            # Update animal data with user inputs
            animal_data[animal_id]["dob"] = request.form["dob"]
            animal_data[animal_id]["region"] = request.form.get("region", "Unknown")
            animal_data[animal_id]["prev_disease_history"] = request.form.get("prev_disease_history", "None")
            animal_data[animal_id]["environmental_risk"] = request.form.get("environmental_risk", "Low")
            animal_data[animal_id]["temperature"] = float(request.form["temperature"])
            animal_data[animal_id]["vaccination"]["last_vaccine_date"] = request.form["last_vaccine_date"]
            animal_data[animal_id]["vaccination"]["next_due_date"] = request.form["next_due_date"]
            animal_data[animal_id]["vaccination"]["status"] = request.form["vaccine_status"]

            # Unified 'Other' handler for dropdown fields
            for field in ["health_status", "breeding_status", "lifestyle", "report_status"]:
                selected_value = request.form.get(field, "")
                if selected_value == "Other":
                    other_value = request.form.get(f"{field}_other", "").strip()
                    if other_value:
                        animal_data[animal_id][field] = other_value
                        if other_value not in animal_data["dynamic_options"][field]:
                            animal_data["dynamic_options"][field].append(other_value)
                    else:
                        animal_data[animal_id][field] = "Other"
                else:
                    animal_data[animal_id][field] = selected_value

            print("Updated Animal Data:", json.dumps(animal_data[animal_id], indent=4))
            save_animal_data(animal_data)
            flash("Details updated successfully!", "success")
        except Exception as e:
            flash(f"Error updating details: {str(e)}", "danger")

    # Calculate age from DOB
    dob_str = animal_data[animal_id].get("dob", "Unknown")
    if dob_str not in ["Unknown", "Not Recorded"]:
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.today() - dob).days // 365
        except ValueError:
            age = "Invalid DOB"
    else:
        age = "Unknown"

    # Define category mapping
    category_mapping = {
        "C": "Cow & Cattle",
        "S": "Sheep & Lamb",
        "H": "Horse",
        "G": "Goat",
        "P": "Pig",
        "K": "Chicken & Hen"
    }

    category_letter = animal_id[0]
    category_name = category_mapping.get(category_letter, "Unknown Category")

    # Load document file name
    document_filename = None
    document_path = os.path.join('static', 'document_records.json')
    if os.path.exists(document_path):
        with open(document_path, 'r') as f:
            records = json.load(f)
            document_info = records.get(animal_id)
            if document_info:
                document_filename = document_info['filename']

    # AI Recommendation Logic
    action = request.form.get("action")
    if action == "ai":
        risk_score = 0

        if animal_data[animal_id]["health_status"] in ["CriticalCondition", "UnderObservation"]:
            risk_score += 2
        elif animal_data[animal_id]["health_status"] == "Stable":
            risk_score += 1

        if animal_data[animal_id]["breeding_status"] == "CannotBreed":
            risk_score += 1

        if animal_data[animal_id]["lifestyle"] == "Sedentary":
            risk_score += 1

        if animal_data[animal_id]["report_status"] in ["RequiresMedicalAttention", "LethargicBehavior"]:
            risk_score += 2

        temp = animal_data[animal_id]["temperature"]
        if temp >= 40 or temp <= 35:
            risk_score += 2

        prev_disease = animal_data[animal_id].get("prev_disease_history", "").lower()
        if prev_disease and prev_disease != "none":
            risk_score += 2

        risky_states = ["Uttar Pradesh", "Bihar", "Odisha", "West Bengal", "Jharkhand"]
        region = animal_data[animal_id].get("region", "")
        if region in risky_states:
            risk_score += 1

        if risk_score >= 7:
            recommendation = "⚠️ High Risk – Immediate medical check-up recommended!"
        elif risk_score >= 4:
            recommendation = "⚠️ Medium Risk – Monitor closely and schedule vet check-up."
        else:
            recommendation = "✅ Low Risk – Animal is in good condition."

    return render_template(
        "animal_features.html",
        animal_id=animal_id,
        category_name=category_name,
        age=age,
        document_filename=document_filename,
        report_filename=animal_data[animal_id].get("report_filename"),
        options=animal_data["dynamic_options"],
        ai_recommendation=recommendation,
        **animal_data[animal_id]
    )



@app.route('/upload_report/<animal_id>', methods=['POST'])
def upload_report(animal_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    if 'report_file' not in request.files:
        flash("No file part", "danger")
        return redirect(url_for('animal_features', animal_id=animal_id))

    file = request.files['report_file']
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{animal_id}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        animal_data = load_animal_data()
        if animal_id in animal_data:
            animal_data[animal_id]['report_filename'] = filename
            save_animal_data(animal_data)

        flash("Report uploaded successfully!", "success")
    else:
        flash("Invalid file type. Only PDF and DOC/DOCX allowed.", "danger")

    return redirect(url_for('animal_features', animal_id=animal_id))

if __name__ == '__main__':
    app.run(debug=True)