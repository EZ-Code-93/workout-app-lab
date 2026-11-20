#!/usr/bin/env python3

from datetime import date
from app import app
from models import *

def seed_database():
    with app.app_context():
        print("Clearing existing data...")
        WorkoutExercise.query.delete()
        Workout.query.delete()
        Exercise.query.delete()
        db.session.commit()

        print("Seeding exercises...")
        pushups = Exercise(
            name="Push-ups",
            category="strength",
            equipment_needed=False
        )
        squats = Exercise(
            name="Barbell Squats",
            category="strength",
            equipment_needed=True
        )
        running = Exercise(
            name="Treadmill Run",
            category="cardio",
            equipment_needed=True
        )
        plank = Exercise(
            name="Forearm Plank",
            category="strength",
            equipment_needed=False
        )
        yoga_flow = Exercise(
            name="Sun Salutation Flow",
            category="flexibility",
            equipment_needed=False
        )

        db.session.add_all([pushups, squats, running, plank, yoga_flow])
        db.session.commit()

        print("Seeding workouts...")
        workout_1 = Workout(
            date=date(2026, 11, 15),
            duration_minutes=45,
            notes="Upper body and core focus."
        )
        workout_2 = Workout(
            date=date(2026, 11, 17),
            duration_minutes=60,
            notes="Leg day plus steady-state cardio."
        )
        workout_3 = Workout(
            date=date(2026, 11, 19),
            duration_minutes=30,
            notes="Active recovery and mobility."
        )

        db.session.add_all([workout_1, workout_2, workout_3])
        db.session.commit()

        print("Seeding workout exercises...")
        we_1 = WorkoutExercise(
            workout_id=workout_1.id,
            exercise_id=pushups.id,
            sets=4,
            reps=15,
            duration_seconds=0
        )
        we_2 = WorkoutExercise(
            workout_id=workout_1.id,
            exercise_id=plank.id,
            sets=3,
            reps=0,
            duration_seconds=60
        )
        we_3 = WorkoutExercise(
            workout_id=workout_2.id,
            exercise_id=squats.id,
            sets=5,
            reps=8,
            duration_seconds=0
        )
        we_4 = WorkoutExercise(
            workout_id=workout_2.id,
            exercise_id=running.id,
            sets=1,
            reps=0,
            duration_seconds=1200
        )
        we_5 = WorkoutExercise(
            workout_id=workout_3.id,
            exercise_id=yoga_flow.id,
            sets=3,
            reps=5,
            duration_seconds=600
        )

        db.session.add_all([we_1, we_2, we_3, we_4, we_5])
        db.session.commit()

        print("Database seeded successfully!")


if __name__ == "__main__":
    seed_database()


	