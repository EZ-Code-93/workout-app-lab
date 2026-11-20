# Workout Tracker REST API

A Flask and SQLAlchemy RESTful API for tracking workouts, exercises, and exercise performance metrics (`sets`, `reps`, and `duration_seconds`). Built with SQLite, Flask-Migrate (Alembic), Marshmallow serialization/validation, and a full `pytest` unit test suite.

---

## Tech Stack & Requirements

* **Python Version:** `3.10.22`
* **Dependency Manager:** `pipenv`
* **Database:** SQLite (`app.db`)

### Core Python Dependencies
* `Flask` — Web framework and REST routing
* `Flask-SQLAlchemy` — ORM models, relationships, and association proxies
* `Flask-Migrate` — Alembic database schema migrations
* `marshmallow` — Request payload validation and JSON serialization
* `pytest` — Automated unit and integration test runner

---

## Project Structure

```text
workout-app-lab/
├── Pipfile
├── Pipfile.lock
├── README.md
└── server/
    ├── app.py              # Flask application and REST API endpoints
    ├── models.py           # SQLAlchemy models, constraints, validations, and Marshmallow schemas
    ├── seed.py             # Database seeding script with sample workouts and exercises
    ├── migrations/         # Alembic migration versions
    ├── pytest.ini
    └── tests/
        ├── test_app.py     # Endpoint and HTTP status code unit tests
        └── test_models.py  # Model constraint, validation, and schema unit tests
```

---

## Getting Started (Local Setup)

### 1. Fork & Clone the Repository
```bash
git clone https://github.com/EZ-Code-93/workout-app-lab.git
cd workout-app-lab
```

### 2. Install Dependencies with Python 3.10.22
Ensure Python `3.10.22` is installed on your system (e.g., via `pyenv` or Homebrew), then create the virtual environment and install all packages:

```bash
pipenv install --python 3.10.22
pipenv shell
```

### 3. Initialize & Migrate the Database
Navigate into the `server/` directory and apply the database migrations to generate `app.db`:

```bash
cd server
export FLASK_APP=app.py
flask db upgrade
```
*(Note: If you are setting up migrations from scratch on a fresh clone without a `migrations/` folder, run `flask db init`, `flask db migrate -m "Initial migration"`, and `flask db upgrade`.)*

### 4. Seed the Database
Populate `app.db` with sample exercises, workouts, and workout exercise logs:

```bash
python seed.py
```

### 5. Run the Flask Server
Start the development server on port `5555`:

```bash
python app.py
```
The API will be available at `http://127.0.0.1:5555`.

---

## Running the Test Suite

The test suite uses an isolated in-memory SQLite database so running tests will not alter your local `app.db` data.

From inside the `server/` directory (with your `pipenv shell` active), run:

```bash
PYTHONPATH=. pytest -v
```

---

## API Endpoints

### Workouts

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/workouts` | List all workouts |
| `GET` | `/workouts/<int:id>` | Get a single workout with its associated exercises and `sets`/`reps`/`duration_seconds` details |
| `POST` | `/workouts` | Create a new workout (`date`, `duration_minutes`, optional `notes`) |
| `DELETE` | `/workouts/<int:id>` | Delete a workout and cascade-delete its associated `workout_exercises` entries |

### Exercises

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/exercises` | List all exercises |
| `GET` | `/exercises/<int:id>` | Get a single exercise and its associated workouts |
| `POST` | `/exercises` | Create a new exercise (`name`, `category`, `equipment_needed`) |
| `DELETE` | `/exercises/<int:id>` | Delete an exercise and cascade-delete its associated `workout_exercises` entries |

### Workout Exercises (Join Resource)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises` | Attach an existing exercise to a workout with `sets`, `reps`, and/or `duration_seconds` |

---

## Example Requests

### Create a Workout (`POST /workouts`)
```json
{
  "date": "2026-11-20",
  "duration_minutes": 45,
  "notes": "Upper body strength session"
}
```

### Create an Exercise (`POST /exercises`)
```json
{
  "name": "Dumbbell Bench Press",
  "category": "strength",
  "equipment_needed": true
}
```
*(Valid categories: `strength`, `cardio`, `flexibility`, `balance`, `hiit`)*

### Add an Exercise to a Workout (`POST /workouts/1/exercises/1/workout_exercises`)
```json
{
  "sets": 4,
  "reps": 10,
  "duration_seconds": 0
}
```
