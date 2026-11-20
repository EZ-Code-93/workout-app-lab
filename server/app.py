from flask import Flask, request, make_response
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

# Initialize Schemas for serialization and deserialization
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True, exclude=('workout_exercises', 'exercises'))

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True, exclude=('workout_exercises', 'workouts'))

workout_exercise_schema = WorkoutExerciseSchema()

# Define Routes here
@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.all()
    return make_response(workouts_schema.dump(workouts), 200)


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout_by_id(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return make_response({'error': 'Workout not found'}, 404)

    # Includes both 'exercises' and 'workout_exercises' (reps/sets/duration)
    return make_response(workout_schema.dump(workout), 200)


@app.route('/exercises', methods=['GET'])
def get_exercises():
    exercises = Exercise.query.all()
    return make_response(exercises_schema.dump(exercises), 200)


@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise_by_id(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return make_response({'error': 'Exercise not found'}, 404)

    return make_response(exercise_schema.dump(exercise), 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)