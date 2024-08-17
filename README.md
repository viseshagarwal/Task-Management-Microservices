# TaskSync - Task Management Microservices

This repository contains a task management application implemented using a microservices architecture. The project consists of two microservices:

1. **Task Service** - Developed using FastAPI.
2. **User Service** - Developed using Node.js and Express.js.

These microservices are interconnected and work together to manage tasks and user information.

## Project Structure

```
Task-Management-Microservices/
│
├── FastAPI-App/          # FastAPI-based service for managing tasks
│   ├── main.py           # Main application file
│   ├── requirements.txt  # Python dependencies
│   ├── Procfile          # For deployment (Heroku or similar)
│   ├── static/           # Static files (images, HTML)
│   └── templates/        # HTML templates (login, signup, etc.)
│
├── NodeJS-App/           # Node.js and Express.js-based service for user management
│   ├── app.js            # Main application file
│   ├── package.json      # Node.js dependencies
│   ├── routes/           # Express routes (API endpoints)
│   ├── models/           # Data models
│   └── views/            # HTML views (login, register, etc.)
│
└── README.md             # This README file
```

## Technologies Used

### Task Service (FastAPI)

- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.
- **Pydantic**: Data validation and settings management using Python type annotations.

### User Service (Node.js and Express.js)

- **Node.js**: JavaScript runtime built on Chrome's V8 JavaScript engine.
- **Express.js**: Fast, unopinionated, minimalist web framework for Node.js.

## Setup Instructions

### Prerequisites

- Python (for FastAPI service).
- Node.js and npm (for Express.js service).

### Clone the Repository

```bash
git clone https://github.com/viseshagarwal/Task-Management-Microservices.git
cd Task-Management-Microservices
```

## Setting Up MongoDB

### Create a MongoDB Cluster

Set up a MongoDB cluster using MongoDB Atlas or a local MongoDB installation.

### Create an Admin User

Create an admin user with the necessary privileges to manage the database.

### 3. Create a `FastAPI-Task-Management` Collection

Create a collection within your MongoDB database named `tasks`.

### 4. Update MongoDB URI

In the `FastAPI-App` service, update the MongoDB URI in the `Settings` class within `main.py`. This URI should include the correct connection details, including the username, password, and database name. For example:

```python
MONGO_DETAILS: str = ( f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.xyz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
```

Replace `cluster0.mongodb.net` with your actual MongoDB credentials and cluster address.

### Install Dependencies

For FastAPI service:

```bash
cd FastAPI-App
pip install -r requirements.txt
```

For Node.js service:

```bash
cd NodeJS-App
npm install
```

## Running the Microservices

For FastAPI service:

```bash
cd FastAPI-App
uvicorn main:app --reload
```

For Node.js service:

```bash
cd NodeJS-App
node app.js
```

## API Endpoints

### Task Service (FastAPI)

- `GET /tasks/`: Fetch all tasks.
- `POST /tasks/`: Create a new task.
- `PUT /tasks/{id}/`: Update an existing task.
- `DELETE /tasks/{id}/`: Delete a task.

### User Service (Express.js)

- `GET /users/`: Fetch all users.
- `POST /users/`: Create a new user.
- `PUT /users/{id}/`: Update an existing user.
- `DELETE /users/{id}/`: Delete a user.

## Inter-Service Communication

The microservices communicate with each other via REST APIs. For example, the Task Service might call the User Service to retrieve user information when creating a task. Ensure that both services are running for full functionality.

## Setup Service URLs

### Update FastAPI URL in `server.js`

In the `NodeJS-App` service, open the `server.js` file. Locate the constant `FASTAPI_BASE_URL` and update it with the deployed FastAPI service URL. For example:

```javascript
const FASTAPI_BASE_URL = "http://localhost:5000/";
```

### Update Node.js URL in `main.py`

In the `FastAPI-App` service, open the `main.py` file. Locate the `NODE_API_URL` variable and update it with the deployed Node.js service URL. For example:

```python
NODE_API_URL = "http://localhost:3000/"
```

## Access the Services

- **FastAPI Service**:
  - API Documentation: [http://localhost:5000/docs](http://localhost:5000/docs)
  - Web Interface: [http://localhost:5000/static/index.html](http://localhost:5000/static/index.html)
- **Node.js Service**:
  - Access via [http://localhost:3000/](http://localhost:3000/)
