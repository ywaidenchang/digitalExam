from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template("test_home.html")

@app.route('/teacher')
def teacher():
    return render_template("teacher.html")

if __name__ == "__main__":
    app.run(debug=True, port=8080)
