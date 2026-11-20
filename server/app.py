from flask import Flask, request, make_response
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import *
# Initialize Flask app and database connection
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

#    ----- Workout Routes -----


# Get all workouts
@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.all()
    return make_response(workouts_schema.dump(workouts), 200)


# Get workout by ID
@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout_by_id(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return make_response({'error': 'Workout not found'}, 404)

    # Includes both 'exercises' and 'workout_exercises' (reps/sets/duration)
    return make_response(workout_schema.dump(workout), 200)


# Create a new workout
@app.route('/workouts', methods=['POST'])
def create_workout():
    data = request.get_json(silent=True) or {}
    try:
        validated_data = workout_schema.load(data)
        new_workout = Workout(**validated_data)
        db.session.add(new_workout)
        db.session.commit()
        return make_response(workout_schema.dump(new_workout), 201)
    except ValidationError as err:
        return make_response({'errors': err.messages}, 400)
    except (ValueError, IntegrityError) as err:
        db.session.rollback()
        return make_response({'errors': [str(err)]}, 400)


# Delete a workout by ID
@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return make_response({'error': 'Workout not found'}, 404)

    # cascade='all, delete-orphan' on Workout automatically deletes associated WorkoutExercises
    db.session.delete(workout)
    db.session.commit()
    return make_response({}, 204)


#    ----- Exercise Routes -----


# Get all exercises
@app.route('/exercises', methods=['GET'])
def get_exercises():
    exercises = Exercise.query.all()
    return make_response(exercises_schema.dump(exercises), 200)


# Get exercise by ID
@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise_by_id(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return make_response({'error': 'Exercise not found'}, 404)

    return make_response(exercise_schema.dump(exercise), 200)


# Create a new exercise
@app.route('/exercises', methods=['POST'])
def create_exercise():
    data = request.get_json(silent=True) or {}
    try:
        validated_data = exercise_schema.load(data)
        new_exercise = Exercise(**validated_data)
        db.session.add(new_exercise)
        db.session.commit()
        return make_response(exercise_schema.dump(new_exercise), 201)
    except ValidationError as err:
        return make_response({'errors': err.messages}, 400)
    except (ValueError, IntegrityError) as err:
        db.session.rollback()
        return make_response({'errors': [str(err)]}, 400)


# Delete an exercise by ID
@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return make_response({'error': 'Exercise not found'}, 404)

    # cascade='all, delete-orphan' on Exercise automatically deletes associated WorkoutExercises
    db.session.delete(exercise)
    db.session.commit()
    return make_response({}, 204)


#    ----- WorkoutExercise Routes -----


# Add an exercise to a workout
@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises', methods=['POST'])
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return make_response({'error': 'Workout not found'}, 404)

    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return make_response({'error': 'Exercise not found'}, 404)

    data = request.get_json(silent=True) or {}
    # Inject URL parameters so WorkoutExercisesSchema validates them cleanly
    data['workout_id'] = workout_id
    data['exercise_id'] = exercise_id

    try:
        validated_data = workout_exercise_schema.load(data)
        new_workout_exercise = WorkoutExercise(**validated_data)
        db.session.add(new_workout_exercise)
        db.session.commit()
        return make_response(workout_exercise_schema.dump(new_workout_exercise), 201)
    except ValidationError as err:
        return make_response({'errors': err.messages}, 400)
    except (ValueError, IntegrityError) as err:
        db.session.rollback()
        return make_response({'errors': [str(err)]}, 400)


if __name__ == '__main__':
    app.run(port=5555, debug=True)