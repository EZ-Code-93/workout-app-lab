from datetime import date
import pytest
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app import app
from models import (
    db,
    Workout,
    Exercise,
    WorkoutExercise,
    WorkoutSchema,
    ExerciseSchema,
    WorkoutExerciseSchema,
)


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


class TestModelsAndConstraints:
    def test_create_valid_models_and_relationships(self, client):
        with app.app_context():
            workout = Workout(date=date(2026, 11, 19), duration_minutes=45, notes="Chest & Triceps")
            exercise = Exercise(name="Bench Press", category="strength", equipment_needed=True)
            db.session.add_all([workout, exercise])
            db.session.commit()

            # Use None for unused duration_seconds so reps > 0 and duration_seconds > 0 constraints pass
            we = WorkoutExercise(
                workout_id=workout.id,
                exercise_id=exercise.id,
                sets=4,
                reps=10,
                duration_seconds=None,
            )
            db.session.add(we)
            db.session.commit()

            # Verify association_proxy shortcuts
            assert len(workout.exercises) == 1
            assert workout.exercises[0].name == "Bench Press"
            assert len(exercise.workouts) == 1
            assert exercise.workouts[0].duration_minutes == 45

    def test_cascade_delete_workout_removes_join_rows(self, client):
        with app.app_context():
            workout = Workout(date=date(2026, 11, 19), duration_minutes=30, notes="Core")
            exercise = Exercise(name="Plank", category="strength", equipment_needed=False)
            db.session.add_all([workout, exercise])
            db.session.commit()

            # Use None for unused reps on a timed plank exercise
            we = WorkoutExercise(
                workout_id=workout.id,
                exercise_id=exercise.id,
                sets=3,
                reps=None,
                duration_seconds=60,
            )
            db.session.add(we)
            db.session.commit()

            db.session.delete(workout)
            db.session.commit()

            assert WorkoutExercise.query.count() == 0
            assert Exercise.query.count() == 1

    def test_workout_duration_validation(self, client):
        with app.app_context():
            with pytest.raises(ValueError, match="Duration minutes must be a positive integer"):
                Workout(date=date(2026, 11, 19), duration_minutes=0, notes="Invalid")

            with pytest.raises(ValueError, match="Duration minutes must be a positive integer"):
                Workout(date=date(2026, 11, 19), duration_minutes=-15, notes="Negative")

    def test_exercise_validations_and_unique_constraint(self, client):
        with app.app_context():
            with pytest.raises(ValueError, match="Exercise name must be a non-empty string"):
                Exercise(name="   ", category="strength", equipment_needed=False)

            with pytest.raises(ValueError, match="Category must be one of"):
                Exercise(name="Jump Rope", category="invalid_category", equipment_needed=True)

            ex1 = Exercise(name="Pull-ups", category="strength", equipment_needed=True)
            ex2 = Exercise(name="Pull-ups", category="strength", equipment_needed=True)
            db.session.add(ex1)
            db.session.commit()

            db.session.add(ex2)
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_workout_exercise_validations_and_constraints(self, client):
        with app.app_context():
            workout = Workout(date=date(2026, 11, 19), duration_minutes=40, notes="Full body")
            exercise = Exercise(name="Kettlebell Swing", category="hiit", equipment_needed=True)
            db.session.add_all([workout, exercise])
            db.session.commit()

            with pytest.raises(ValueError, match="Sets must be a positive integer"):
                WorkoutExercise(workout_id=workout.id, exercise_id=exercise.id, sets=0, reps=10)

            with pytest.raises(ValueError, match="reps must be a positive integer greater than 0 or None."):
                WorkoutExercise(workout_id=workout.id, exercise_id=exercise.id, sets=3, reps=-5)

            # Verify SQLite CheckConstraint rejects 0 when passed directly
            bad_we = WorkoutExercise(
                workout_id=workout.id,
                exercise_id=exercise.id,
                sets=3,
                reps=0,
                duration_seconds=None,
            )
            db.session.add(bad_we)
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()


class TestSchemas:
    def test_workout_schema_serialization_no_recursion(self, client):
        with app.app_context():
            workout = Workout(date=date(2026, 11, 19), duration_minutes=50, notes="Leg day")
            exercise = Exercise(name="Squats", category="strength", equipment_needed=True)
            db.session.add_all([workout, exercise])
            db.session.commit()

            we = WorkoutExercise(
                workout_id=workout.id,
                exercise_id=exercise.id,
                sets=4,
                reps=8,
                duration_seconds=None,
            )
            db.session.add(we)
            db.session.commit()

            dumped = WorkoutSchema().dump(workout)
            assert dumped['id'] == workout.id
            assert dumped['date'] == '2026-11-19'
            assert len(dumped['exercises']) == 1
            assert len(dumped['workout_exercises']) == 1
            assert dumped['workout_exercises'][0]['reps'] == 8

    def test_workout_exercise_schema_rejects_negative_metrics(self):
        schema = WorkoutExerciseSchema()
        with pytest.raises(ValidationError):
            schema.load({
                "workout_id": 1,
                "exercise_id": 1,
                "sets": 3,
                "reps": -1,
                "duration_seconds": None,
            })

    def test_exercise_schema_validation(self):
        schema = ExerciseSchema()
        with pytest.raises(ValidationError):
            schema.load({
                "name": "",
                "category": "not_a_category",
                "equipment_needed": False,
            })
