import os
os.environ['DATABASE_URI'] = 'sqlite:///:memory:'
from datetime import date
import pytest

from app import app
from models import db, Workout, Exercise, WorkoutExercise


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()

        w1 = Workout(date=date(2026, 11, 18), duration_minutes=45, notes="Upper body")
        e1 = Exercise(name="Push-ups", category="strength", equipment_needed=False)
        db.session.add_all([w1, e1])
        db.session.commit()

        we1 = WorkoutExercise(
            workout_id=w1.id,
            exercise_id=e1.id,
            sets=3,
            reps=15,
            duration_seconds=None,
        )
        db.session.add(we1)
        db.session.commit()

        yield app.test_client()

        db.session.remove()
        db.drop_all()


class TestWorkoutRoutes:
    def test_get_all_workouts(self, client):
        response = client.get('/workouts')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['notes'] == "Upper body"
        assert 'workout_exercises' not in data[0]

    def test_get_workout_by_id_includes_exercises_and_join_data(self, client):
        response = client.get('/workouts/1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == 1
        assert len(data['exercises']) == 1
        assert data['exercises'][0]['name'] == "Push-ups"
        assert len(data['workout_exercises']) == 1
        assert data['workout_exercises'][0]['sets'] == 3
        assert data['workout_exercises'][0]['reps'] == 15

    def test_get_workout_not_found(self, client):
        response = client.get('/workouts/999')
        assert response.status_code == 404
        assert response.get_json() == {'error': 'Workout not found'}

    def test_create_workout_success(self, client):
        payload = {
            "date": "2026-11-20",
            "duration_minutes": 60,
            "notes": "Cardio endurance",
        }
        response = client.post('/workouts', json=payload)
        assert response.status_code == 201
        data = response.get_json()
        assert data['id'] == 2
        assert data['duration_minutes'] == 60

    def test_create_workout_invalid_payload(self, client):
        payload = {
            "date": "2026-11-20",
            "duration_minutes": -10,
        }
        response = client.post('/workouts', json=payload)
        assert response.status_code == 400
        assert 'errors' in response.get_json()

    def test_delete_workout_cascades_workout_exercises(self, client):
        response = client.delete('/workouts/1')
        assert response.status_code == 204
        assert client.get('/workouts/1').status_code == 404
        with app.app_context():
            assert WorkoutExercise.query.count() == 0


class TestExerciseRoutes:
    def test_get_all_exercises(self, client):
        response = client.get('/exercises')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['name'] == "Push-ups"

    def test_get_exercise_by_id_includes_workouts(self, client):
        response = client.get('/exercises/1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == "Push-ups"
        assert len(data['workouts']) == 1
        assert data['workouts'][0]['id'] == 1

    def test_get_exercise_not_found(self, client):
        response = client.get('/exercises/999')
        assert response.status_code == 404

    def test_create_exercise_success(self, client):
        payload = {
            "name": "Rowing Machine",
            "category": "cardio",
            "equipment_needed": True,
        }
        response = client.post('/exercises', json=payload)
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == "Rowing Machine"

    def test_create_exercise_duplicate_name_fails(self, client):
        payload = {
            "name": "Push-ups",
            "category": "strength",
            "equipment_needed": False,
        }
        response = client.post('/exercises', json=payload)
        assert response.status_code == 400
        assert 'errors' in response.get_json()

    def test_delete_exercise_cascades_workout_exercises(self, client):
        response = client.delete('/exercises/1')
        assert response.status_code == 204
        assert client.get('/exercises/1').status_code == 404
        with app.app_context():
            assert WorkoutExercise.query.count() == 0


class TestWorkoutExerciseRoute:
    def test_add_exercise_to_workout_success(self, client):
        ex_res = client.post('/exercises', json={
            "name": "Plank",
            "category": "strength",
            "equipment_needed": False,
        })
        exercise_id = ex_res.get_json()['id']

        response = client.post(
            f'/workouts/1/exercises/{exercise_id}/workout_exercises',
            json={"sets": 3, "reps": None, "duration_seconds": 60},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['workout_id'] == 1
        assert data['exercise_id'] == exercise_id
        assert data['duration_seconds'] == 60

    def test_add_exercise_to_missing_workout_returns_404(self, client):
        response = client.post(
            '/workouts/999/exercises/1/workout_exercises',
            json={"sets": 3, "reps": 10},
        )
        assert response.status_code == 404

    def test_add_exercise_invalid_metrics_returns_400(self, client):
        ex_res = client.post('/exercises', json={
            "name": "Burpees",
            "category": "hiit",
            "equipment_needed": False,
        })
        exercise_id = ex_res.get_json()['id']

        response = client.post(
            f'/workouts/1/exercises/{exercise_id}/workout_exercises',
            json={"sets": 3, "reps": -2, "duration_seconds": None},
        )
        assert response.status_code == 400
        assert 'errors' in response.get_json()
