from flask import Flask, abort, request, render_template, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS  # Importing flask_cors
import joblib
from forms import UserProfileForm
from models import db, User, Resource
from transformers import pipeline
import csv
import os
from resource_fetcher import fetch_books, fetch_research_papers, fetch_youtube_videos
from sklearn.preprocessing import StandardScaler
from chat import get_response

app = Flask(__name__)
app.config['SECRET_KEY'] = '4bc99783f8ecc9b1b94165edf0368c4f'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')

# Enable CORS for the Flask app
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize the database
db.init_app(app)
migrate = Migrate(app, db)

# Create the database tables
with app.app_context():
    db.create_all()

# Load the CSV data of students
student_data = {}
csv_file_path = 'data/cleaned_students_data.csv'

if os.path.exists(csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                student_id = float(row.get('StudentID', 0))
                if student_id != 0:
                    if student_id not in student_data:
                        student_data[student_id] = {
                            'semester_marks': [
                                float(row['Semester1_Marks']) if row['Semester1_Marks'] else 0.0,
                                float(row['Semester2_Marks']) if row['Semester2_Marks'] else 0.0,
                                float(row['Semester3_Marks']) if row['Semester3_Marks'] else 0.0,
                                float(row['Semester4_Marks']) if row['Semester4_Marks'] else 0.0,
                                float(row['Semester5_Marks']) if row['Semester5_Marks'] else 0.0,
                                float(row['Semester6_Marks']) if row['Semester6_Marks'] else 0.0,
                            ],
                            'attendance': [
                                float(row['Attendance_Sem1']) if row['Attendance_Sem1'] else 0.0,
                                float(row['Attendance_Sem2']) if row['Attendance_Sem2'] else 0.0,
                                float(row['Attendance_Sem3']) if row['Attendance_Sem3'] else 0.0,
                                float(row['Attendance_Sem4']) if row['Attendance_Sem4'] else 0.0,
                                float(row['Attendance_Sem5']) if row['Attendance_Sem5'] else 0.0,
                                float(row['Attendance_Sem6']) if row['Attendance_Sem6'] else 0.0,
                            ],
                            'total_gpa': float(row['Total_GPA']) if row['Total_GPA'] else 0.0,
                            'total_attendance': float(row['Total_Attendance'].strip('%')) if row['Total_Attendance'] else 0.0
                        }
            except KeyError as e:
                print(f"KeyError: {e} in row {row}")
            except ValueError as e:
                print(f"ValueError: {e} in row {row}")

# Load the trained model
model = joblib.load('student_performance_model.pkl')

# Initialize AI generator
generator = pipeline('text-generation', model='gpt2')

def generate_prescriptive_message(grade, attendance):
    if isinstance(attendance, list):
        average_attendance = sum(attendance) / len(attendance)
    else:
        average_attendance = attendance

    if grade >= 3.0 and average_attendance >= 80:
        return "Your academic performance and attendance are excellent. Keep up the good work!"
    elif grade >= 2.5 and average_attendance >= 70:
        return "Your academic performance and attendance are above average. Keep striving for improvement!"
    else:
        return "Attention: Your grade is below average and your attendance is low. Immediate action is required to improve your academic performance and attendance."

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form['prompt']
    generated = generator(prompt, max_length=100, num_return_sequences=1)[0]['generated_text']
    return render_template('result.html', prompt=prompt, generated=generated)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = float(request.form['id'])
        password = request.form['password']
        
        user = User.query.get(student_id)

        if user:
            if user.verify_password(password):
                session['student_id'] = str(user.id)
                return redirect(url_for('dashboard', username=user.username))
            else:
                return render_template('login.html', error='Invalid password')
        else:
            if student_id in student_data:
                student = student_data[student_id]
                new_user = User(
                    id=student_id,
                    username=str(student_id),  
                    password=password,
                    grade=student['total_gpa'],
                    attendance=student['attendance'],
                    semester_marks=student['semester_marks']
                )
                db.session.add(new_user)
                db.session.commit()
                session['student_id'] = str(new_user.id)
                return redirect(url_for('dashboard', username=new_user.username))
            else:
                return render_template('login.html', error='Student ID not found in records')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    user_id = session.get('student_id')
    user = User.query.get(user_id)
    if not user:
        abort(404)

    if user.semester_marks is None:
        user.semester_marks = [0] * 6
    if user.attendance is None or not isinstance(user.attendance, list):
        user.attendance = [0] * 6

    # Predict total GPA using the trained model
    features = user.semester_marks + user.attendance
    # Scaling features if necessary
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform([features])
    predicted_gpa = model.predict(features_scaled)[0]

    prescriptive_message = generate_prescriptive_message(user.grade, user.attendance)

    if "requires improvement" in prescriptive_message.lower() or "action is required" in prescriptive_message.lower():
        prescriptive_message_class = "bad"
    else:
        prescriptive_message_class = "good"

    return render_template('dashboard.html', user=user, prescriptive_message=prescriptive_message, predicted_gpa=predicted_gpa,
                           prescriptive_message_class=prescriptive_message_class)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('student_id')
    user = User.query.get(user_id)
    if not user:
        abort(404)

    form = UserProfileForm()

    if form.validate_on_submit():
        user.preferred_subject = form.preferred_subject.data
        user.learning_style = form.learning_style.data
        user.strengths = form.strengths.data
        user.weaknesses = form.weaknesses.data
        db.session.commit()

        # Redirect to recommendations page after saving the profile
        return redirect(url_for('recommendations'))

    # Populate form fields with user data
    form.preferred_subject.data = user.preferred_subject
    form.learning_style.data = user.learning_style
    form.strengths.data = user.strengths
    form.weaknesses.data = user.weaknesses

    return render_template('profile.html', form=form)


@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    user_id = session.get('student_id')
    user = User.query.get(user_id)
    
    if not user:
        abort(404)  # Redirect to a 404 page if user is not found

    # Determine the search query
    query = request.args.get('query', '').strip() if request.method == 'GET' else request.form.get('query', '').strip()

    if query:
        # Fetch recommendations based on the search query
        if user.learning_style == 'Visual':
            resources = fetch_youtube_videos(query)
        elif user.learning_style == 'Reading/Writing':
            resources = fetch_research_papers(query)
        elif user.learning_style == 'In-person':
            resources = fetch_books(query)
        else:
            resources = []
    else:
        # Fetch recommendations based on user's learning style and preferred subject
        if user.learning_style == 'Visual':
            resources = fetch_youtube_videos(user.preferred_subject)
        elif user.learning_style == 'Reading/Writing':
            resources = fetch_research_papers(user.preferred_subject)
        elif user.learning_style == 'In-person':
            resources = fetch_books(user.preferred_subject)
        else:
            resources = []

    return render_template('recommendations.html', resources=resources, user=user, show_search=True)



@app.route('/resources', methods=['GET'])
def get_resources():
    search_query = request.args.get('search', '')
    resources = Resource.query.filter(Resource.title.ilike(f'%{search_query}%')).all()
    resource_data = [resource.to_dict() for resource in resources]

    # Add additional logic to prioritize answers
    for resource in resource_data:
        if not resource.get('answer'):
            resource['answer'] = "No direct answer available."

    return jsonify(resource_data)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    resources = Resource.query.filter(
        Resource.title.ilike(f'%{query}%') |
        Resource.subject.ilike(f'%{query}%') |
        Resource.learning_style.ilike(f'%{query}%')
    ).all()
    resource_data = [resource.to_dict() for resource in resources]
    return render_template('search_results.html', resources=resource_data, query=query)


@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)



@app.template_filter('get_circle_class')
def get_circle_class(mark):
    if mark >= 80:
        return 'circle-full'
    elif mark >= 50:
        return 'circle-half'
    else:
        return 'circle-low'

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('student_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
