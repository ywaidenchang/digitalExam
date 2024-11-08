from flask import Flask, render_template, redirect, request, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "helloworldmother"  # Secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'  # SQLite database URI
db = SQLAlchemy(app)

# Models
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    questions = db.relationship('Question', backref='quiz', lazy=True)

    def __repr__(self):
        return f'<Quiz {self.title}>'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    answers = db.relationship('Answer', backref='question', lazy=True)

    def __repr__(self):
        return f'<Question {self.content}>'

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)

    def __repr__(self):
        return f'<Answer {self.content}>'

# Routes
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
    return jsonify({'message': 'New quiz created successfully'})

@app.route('/get_quizzes', methods=['GET'])
def get_quizzes():
    quizzes = Quiz.query.all()
    quizzes_list = [{'id': quiz.id, 'title': quiz.title, 'description': quiz.description} for quiz in quizzes]
    return jsonify({'quizzes': quizzes_list})

@app.route('/delete_quiz/<int:quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    # Deleting associated questions and answers
    for question in quiz.questions:
        for answer in question.answers:
            db.session.delete(answer)
        db.session.delete(question)
    db.session.delete(quiz)
    db.session.commit()
    return jsonify({'message': 'Quiz and all associated questions and answers deleted successfully'})

@app.route("/edit/<int:quiz_id>", methods=["GET"])
def edit(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template("edit.html", quiz=quiz, questions=questions)

@app.route('/add_question/<int:quiz_id>', methods=['POST'])
def add_question(quiz_id):
    data = request.get_json()
    new_question = Question(content=data['content'], quiz_id=quiz_id)
    db.session.add(new_question)
    db.session.commit()
    return jsonify({'message': 'New question added successfully'})

@app.route('/add_answer/<int:question_id>', methods=['POST'])
def add_answer(question_id):
    data = request.get_json()
    new_answer = Answer(content=data['content'], is_correct=data['is_correct'], question_id=question_id)
    db.session.add(new_answer)
    db.session.commit()
    return jsonify({'message': 'New answer added successfully'})

@app.route('/update_question/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    question = Question.query.get_or_404(question_id)
    data = request.get_json()
    question.content = data['content']
    db.session.commit()
    return jsonify({'message': 'Question updated successfully'})

@app.route('/update_answer/<int:answer_id>', methods=['PUT'])
def update_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    data = request.get_json()
    answer.content = data['content']
    answer.is_correct = data['is_correct']
    db.session.commit()
    return jsonify({'message': 'Answer updated successfully'})

@app.route('/delete_question/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    # Delete associated answers first
    for answer in question.answers:
        db.session.delete(answer)
    db.session.delete(question)
    db.session.commit()
    return jsonify({'message': 'Question and associated answers deleted successfully'})

@app.route('/delete_answer/<int:answer_id>', methods=['DELETE'])
def delete_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    db.session.delete(answer)
    db.session.commit()
    return jsonify({'message': 'Answer deleted successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
