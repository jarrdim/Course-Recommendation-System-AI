import os
import pickle
from flask import Flask, render_template, request, redirect, url_for,  session
import pandas as pd

from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Load data
courses_list = pd.read_pickle('courses.pkl')
similarity = pd.read_pickle('similarity.pkl')



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hscscsdccdsdcds'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    hobbies = db.Column(db.String(200), nullable=False)
    passion = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.full_name
    
with app.app_context():
    db.create_all()


def recommend(course):
    index = courses_list[courses_list['course_name'] == course].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_course_names = []
    for i in distances[1:7]:
        course_name = courses_list.iloc[i[0]].course_name
        recommended_course_names.append(course_name)

    return recommended_course_names

@app.route('/')
def index():
    # user = User.query.first()
    # username = user.full_name if user else 'Guest' 
    # return render_template('index.html', courses=courses_list['course_name'].values,  username=username)
    print(session)
    if 'username' in session:
        username = session['username']
        return render_template('index.html', username=username)
    else:
        return render_template('index.html')

@app.route('/recommentcourses')
def recommentcourses():
    return render_template('recommentcourses.html', courses=courses_list['course_name'].values)

@app.route('/logout')
def logout():
    session.pop('username', None)  # Clear the username from the session
    return redirect(url_for('index'))
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/details')
def details():
    return render_template('details.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        full_name = request.form['full_name']
        hobbies = request.form['hobbies']
        passion = request.form['passion']
        new_user = User(full_name=full_name, hobbies=hobbies, passion=passion)
        db.session.add(new_user)
        session['username'] = full_name
        db.session.commit()
        return redirect(url_for('recommentcourses'))

@app.route('/course')
def course():
    return render_template('course.html')

@app.route('/recommendation', methods=['POST'])
def recommendation():
    selected_course = request.form['selected_course']
    recommended_course_names = recommend(selected_course)
    return render_template('recommendation.html', selected_course=selected_course, recommended_courses=recommended_course_names)

if __name__ == '__main__':
    app.run(debug=True)
