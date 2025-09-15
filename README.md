# Microservices-Based Learning Management System (Django + FastAPI)

MicroLearn is a **containerized Learning Management System (LMS)** that demonstrates **microservices architecture** using **Django REST Framework** as the core monolith, **FastAPI services** for AI grading and payment handling, and **RabbitMQ** as the asynchronous message broker.
The platform allows students to subscribe to plans, enroll in courses, track progress, and take quizzes, while admins manage courses, modules, and subscription plans.

---

## Deployment Architecture

MicroLearn is deployed with **Docker containers** on a VPS, by a **central Nginx reverse proxy** that routes requests to the Django API.
The system consists of **Django (monolith)**, **FastAPI microservices**, and **RabbitMQ** for async communication.

### Request & Event Flow

**Step 1: Client Request (REST API)**

* Student or Admin interacts with Django API (auth, courses, subscriptions, quizzes).
* All persistent business data lives inside Django.

**Step 2: Payment Flow**

* Student subscribes to a plan → Django calls Stripe Checkout.
* Stripe sends webhook → Payment Worker (FastAPI).
* Payment Worker publishes `payment_event` to RabbitMQ.
* Django consumes event → updates subscription/payment status.

**Step 3: Quiz Flow**

* Student submits quiz attempt via Django API.
* Django persists the attempt → publishes `quiz_submitted` event to RabbitMQ.
* AI Grader (FastAPI) consumes the event → calls LLM → returns {score, passed, feedback}.
* AI Grader publishes `quiz_graded` event to RabbitMQ.
* Django consumes it → updates QuizAttempt → unlocks progress if passed.

---

## Architecture Diagram

```
[ Client ]
    |
    v
[ Central Nginx Reverse Proxy ]
    |
    v
[ Django Monolith ] <----> [ PostgreSQL ]
     |   ^  ^
     |   |  |
     |   |  └── consumes quiz_graded, payment_event
     |   |
     └── publishes quiz_submitted, handles subscriptions
            |
            v
        [ RabbitMQ ]
            |
   ---------------------
   |                   |
   v                   v
[ FastAPI AI Grader ]  [ FastAPI Payment Worker ]
   - consumes quiz_submitted   - consumes Stripe webhooks
   - grades with AI            - publishes payment_event
   - publishes quiz_graded
```

---

## Database Schema (High-Level)

<img width="3662" height="2656" alt="drawSQL-image-export-2025-09-15" src="https://github.com/user-attachments/assets/417627b6-3052-4315-99c2-768b91edf5d0" />

---

## Microservices Breakdown

### Django (Main Monolith)

* Authentication & Users (JWT).
* Subscription plans & subscriptions.
* Course management (categories, modules, lessons).
* Progress tracking (lesson progress, enrollments).
* Quiz data (Quiz, Question, Attempt, Answer).
* Publishes `quiz_submitted` to RabbitMQ.
* Consumes `quiz_graded` and `payment_event` to update records.

### FastAPI – AI Grader

* Stateless service.
* Listens for `quiz_submitted` events.
* Builds LLM prompt from quiz + answers.
* Publishes `quiz_graded` event with:

  ```json
  {
    "quiz_attempt_id": 42,
    "score": 4,
    "passed": true,
    "feedback": "Great understanding, missed one detail"
  }
  ```

### FastAPI – Payment Worker

* Listens for Stripe webhooks.
* Publishes `payment_event` to RabbitMQ.
* No persistence, Django updates Subscription/Payment tables.

### RabbitMQ

* Connects Django and FastAPI asynchronously.
* Events:

  * `quiz_submitted` → FastAPI AI Grader.
  * `quiz_graded` → Django.
  * `payment_event` → Django.

---

## Features

* **Microservices Architecture** – Django as source of truth, FastAPI services for async tasks.
* **Asynchronous Communication** – RabbitMQ event-driven flow.
* **Stripe Payments** – Secure subscription checkout & updates.
* **AI-Powered Quiz Grading** – LLM evaluates answers with feedback.
* **Progress Tracking** – Unlock quizzes and mark courses completed.
* **Admin Dashboard** – Manage categories, courses, lessons, quizzes, and subscriptions.
* **Containerized Deployment** – Docker + Nginx for production readiness.

---

## Technologies Used

| Technology   | Purpose                                       |
| ------------ | --------------------------------------------- |
| Django + DRF | Monolith API, business logic, persistence     |
| FastAPI      | Stateless microservices (AI grading, payment) |
| RabbitMQ     | Event-driven communication                    |
| PostgreSQL   | Relational DB for all persistent data         |
| Stripe       | Payment gateway                               |
| S3           | Video hosting for lessons                     |
| Nginx        | Reverse proxy + static/media serving          |
| Docker       | Containerization & deployment                 |

---

## Demo

* Swagger Docs (Django): [https://microlearn.mo-magdy.com/api/v1/schema/swagger-ui/](https://microlearn.mo-magdy.com/api/v1/schema/swagger-ui/)
* Postman Collection: [View Here](https://documenter.getpostman.com/view/38857071/2sB3HqHJX3)
