from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from marshmallow import Schema, fields

db = SQLAlchemy()

# Define Models here
class WorkoutExercises(db.Model):
    __tablename__ = 'workout_exercises'

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=False)

    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')



class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False)

    workout_exercises = db.relationship('WorkoutExercises', back_populates='exercise', cascade='all, delete-orphan')
    workouts = association_proxy('workout_exercises', 'workout')



class ExerciseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    category = fields.Str()
    equipment_needed = fields.Bool()
    workout_exercises = fields.List(fields.Nested(lambda: WorkoutExercisesSchema(exclude=('exercise',))))
    workouts = fields.List(fields.Nested(lambda: WorkoutSchema(exclude=('exercises',))))



class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=False)

    workout_exercises = db.relationship('WorkoutExercises', back_populates='workout', cascade='all, delete-orphan')
    exercises = association_proxy('workout_exercises', 'exercise')



class WorkoutSchema(Schema):
    id = fields.Int()
    date = fields.Date()
    duration_minutes = fields.Int()
    notes = fields.Text()
    workout_exercises = fields.List(fields.Nested(lambda: WorkoutExercisesSchema(exclude=('workout',))))
    exercises = fields.List(fields.Nested(lambda: ExerciseSchema(exclude=('workouts',))))

