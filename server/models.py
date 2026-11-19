from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from marshmallow import Schema, fields

db = SQLAlchemy()

# Define Models here
class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    __table_args__ = (
        db.CheckConstraint('reps > 0', name='check_reps_positive'),
        db.CheckConstraint('sets > 0', name='check_sets_positive'),
        db.CheckConstraint('duration_seconds > 0', name='check_duration_seconds_positive')
    )



class WorkoutExerciseSchema(Schema):
    id = fields.Int()
    workout_id = fields.Int()
    exercise_id = fields.Int()
    reps = fields.Int()
    sets = fields.Int()
    duration_seconds = fields.Int()
    workout = fields.Nested(lambda: WorkoutSchema(exclude=('workout_exercises', 'exercises')))
    exercise = fields.Nested(lambda: ExerciseSchema(exclude=('workout_exercises', 'workouts')))



class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship('WorkoutExercise', back_populates='exercise', cascade='all, delete-orphan')
    workouts = association_proxy('workout_exercises', 'workout')

    __table_args__ = (
        db.CheckConstraint('name != ""', name='check_name_not_empty'),
        db.CheckConstraint('category != ""', name='check_category_not_empty')
    )



class ExerciseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    category = fields.Str()
    equipment_needed = fields.Bool()
    workout_exercises = fields.List(fields.Nested(lambda: WorkoutExerciseSchema(exclude=('exercise',))))
    workouts = fields.List(fields.Nested(lambda: WorkoutSchema(exclude=('exercises', 'workout_exercises'))))



class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    workout_exercises = db.relationship('WorkoutExercise', back_populates='workout', cascade='all, delete-orphan')
    exercises = association_proxy('workout_exercises', 'exercise')

    __table_args__ = (
        db.CheckConstraint('duration_minutes > 0', name='check_duration_positive')
    )



class WorkoutSchema(Schema):
    id = fields.Int()
    date = fields.Date()
    duration_minutes = fields.Int()
    notes = fields.Text()
    workout_exercises = fields.List(fields.Nested(lambda: WorkoutExerciseSchema(exclude=('workout',))))
    exercises = fields.List(fields.Nested(lambda: ExerciseSchema(exclude=('workouts', 'workout_exercises'))))

