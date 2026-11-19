from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from marshmallow import Schema, fields, validate, validates_schema, ValidationError

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

    @validates('sets')
    def validate_sets(self, key, value):
        if value is not None and (not isinstance(value, int) or value <= 0):
            raise ValueError("Sets must be a positive integer greater than 0.")
        return value

    @validates('reps', 'duration_seconds')
    def validate_non_negative_metrics(self, key, value):
        if value is not None and (not isinstance(value, int) or value < 0):
            raise ValueError(f"{key} must be a non-negative integer (0 or greater).")
        return value

class WorkoutExerciseSchema(Schema):
    id = fields.Int()
    workout_id = fields.Int()
    exercise_id = fields.Int()
    reps = fields.Int()
    sets = fields.Int()
    duration_seconds = fields.Int()
    workout = fields.Nested(lambda: WorkoutSchema(exclude=('workout_exercises', 'exercises')))
    exercise = fields.Nested(lambda: ExerciseSchema(exclude=('workout_exercises', 'workouts')))



VALID_CATEGORIES = ['strength', 'cardio', 'flexibility', 'balance', 'hiit']

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

    @validates('name')
    def validate_name(self, key, value):
        if not value or not isinstance(value, str) or not value.strip():
            raise ValueError("Exercise name must be a non-empty string.")
        return value.strip()

    @validates('category')
    def validate_category(self, key, value):
        if not value or not isinstance(value, str) or not value.strip():
            raise ValueError("Category must be a non-empty string.")
        normalized = value.strip().lower()
        if normalized not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(VALID_CATEGORIES)}.")
        return normalized

    @validates('equipment_needed')
    def validate_equipment_needed(self, key, value):
        if not isinstance(value, bool):
            raise ValueError("equipment_needed must be a boolean (True or False).")
        return value

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

    @validates('duration_minutes')
    def validate_duration_minutes(self, key, value):
        if value is None or not isinstance(value, int) or value <= 0:
            raise ValueError("Duration minutes must be a positive integer greater than 0.")
        return value

    @validates('date')
    def validate_date(self, key, value):
        if value is None:
            raise ValueError("Workout date is required.")
        if isinstance(value, str):
            try:
                value = date.fromisoformat(value)
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format.")
        if not isinstance(value, date):
            raise ValueError("Invalid date object.")
        return value

class WorkoutSchema(Schema):
    id = fields.Int()
    date = fields.Date()
    duration_minutes = fields.Int()
    notes = fields.Text()
    workout_exercises = fields.List(fields.Nested(lambda: WorkoutExerciseSchema(exclude=('workout',))))
    exercises = fields.List(fields.Nested(lambda: ExerciseSchema(exclude=('workouts', 'workout_exercises'))))

