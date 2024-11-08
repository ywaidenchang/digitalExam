from flask import Flask, render_template, redirect, request, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "helloworldmother"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
db = SQLAlchemy(app)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Quiz {self.title}>'

@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/teacher-login')
def teacher_login():
    return render_template("teacher_login.html")

@app.route('/login-post', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username == 'teacher' and password == 'test':
        session['logged_in'] = True
        session.pop('_flashes', None)  # Clear flashed messages
        return redirect("/dashboard")
    else:
        flash('Invalid credentials')
        return redirect("/teacher-login")

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect("/teacher-login")
    return render_template("dashboard.html")

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect("/home")

@app.route('/add_quiz', methods=['POST'])
def add_quiz():
    data = request.get_json()
    new_quiz = Quiz(title=data['title'], description=data['description'])
    db.session.add(new_quiz)
    db.session.commit()
    return jsonify({'message': 'New quiz created successfully'})#, redirect("/edit/<int:quiz_id>")

@app.route('/update_quiz/<int:quiz_id>', methods=['PUT'])
def update_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    quiz.title = data['title']
    quiz.description = data['description']
    db.session.commit()
    return jsonify({'message': 'Quiz updated successfully'})

@app.route('/delete_quiz/<int:quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    return jsonify({'message': 'Quiz deleted successfully'})

@app.route("/edit/<int:quiz_id>")
def edit(quiz_id):
    return render_template("edit.html")

@app.route('/get_quizzes', methods=['GET'])
def get_quizzes():
    quizzes = Quiz.query.all()
    quizzes_list = [{'id': quiz.id, 'title': quiz.title, 'description': quiz.description} for quiz in quizzes]
    return jsonify({'quizzes': quizzes_list})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
