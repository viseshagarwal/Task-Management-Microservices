const express = require("express");
const axios = require("axios");
const bodyParser = require("body-parser");
const path = require("path");

// Create an instance of Express
const app = express();
app.use(express.static(path.join(__dirname, "public")));

// Middleware to parse JSON bodies
app.use(bodyParser.json());

// Base URL for the FastAPI application
const FASTAPI_BASE_URL =
  "https://secret-woodland-62864-9a8c48b1742f.herokuapp.com/";

// Middleware for Authentication
const authenticate = (req, res, next) => {
  const token = req.headers["authorization"]?.split(" ")[1];
  if (!token) {
    return res.status(401).json({ message: "No token provided" });
  }
  req.token = token; // Pass the token to the request object
  next();
};

app.post("/api/login", async (req, res) => {
  try {
    const { username, password } = req.body;
    const response = await axios.post(
      `${FASTAPI_BASE_URL}token`,
      new URLSearchParams({
        username,
        password,
      }),
      {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      }
    );
    res.status(response.status).json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ message: error.message });
  }
});

// Create a task
app.post("/api/tasks", authenticate, async (req, res) => {
  try {
    const response = await axios.post(`${FASTAPI_BASE_URL}tasks/`, req.body, {
      headers: { Authorization: `Bearer ${req.token}` },
    });
    res.status(response.status).json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ message: error.message });
  }
});

// Read tasks
app.get("/api/tasks", authenticate, async (req, res) => {
  try {
    const response = await axios.get(`${FASTAPI_BASE_URL}tasks/`, {
      headers: { Authorization: `Bearer ${req.token}` },
      params: req.query, // Pass query parameters directly
    });
    res.status(response.status).json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ message: error.message });
  }
});

// Read a single task by ID
app.get("/api/tasks/:taskId", authenticate, async (req, res) => {
  try {
    const response = await axios.get(
      `${FASTAPI_BASE_URL}tasks/${req.params.taskId}`,
      {
        headers: { Authorization: `Bearer ${req.token}` },
      }
    );
    res.status(response.status).json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ message: error.message });
  }
});

// Update a task
app.put("/api/tasks/:taskId", authenticate, async (req, res) => {
  try {
    const response = await axios.put(
      `${FASTAPI_BASE_URL}tasks/${req.params.taskId}`,
      req.body,
      {
        headers: { Authorization: `Bearer ${req.token}` },
      }
    );
    res.status(response.status).json(response.data);
  } catch (error) {
    console.error("Update Task Error:", error.response?.data || error.message);
    res.status(error.response?.status || 500).json({ message: error.message });
  }
});

// Delete a task
app.delete("/api/tasks/:taskId", authenticate, async (req, res) => {
  try {
    const response = await axios.delete(
      `${FASTAPI_BASE_URL}tasks/${req.params.taskId}`,
      {
        headers: { Authorization: `Bearer ${req.token}` },
      }
    );
    res.status(response.status).json(response.data);
  } catch (error) {
    console.error("Delete Task Error:", error.response?.data || error.message);
    res.status(error.response?.status || 500).json({ message: error.message });
  }
});

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.get("/tasks", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "tasks.html"));
});

// Start the server
const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
