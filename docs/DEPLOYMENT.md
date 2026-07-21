# Deployment Guide

This guide explains how to run the **Autonomous AI Agent** using Docker.

## Prerequisites

Before deploying the application, ensure the following tools are installed:

- Docker Desktop (Windows/macOS)
- Docker Engine & Docker Compose (Linux)

Verify the installation:

```bash
docker --version
docker compose version
```

---

## Clone the Repository

```bash
git clone https://github.com/Aryan1021/autonomous-ai-agent
cd autonomous-ai-agent
```

---

## Configure Environment Variables

Create a `.env` file in the project root.

You can copy the example configuration:

```bash
cp .env.example .env
```

On Windows, manually create a `.env` file and copy the contents of `.env.example`.

Update the following variable:

```env
GEMINI_API_KEY=your_api_key_here
```

---

## Build the Docker Image

```bash
docker compose build
```

---

## Start the Application

```bash
docker compose up
```

Or run it in detached mode:

```bash
docker compose up -d
```

---

## Access the Application

FastAPI API:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```

ReDoc:

```
http://localhost:8000/redoc
```

---

## Stop the Application

```bash
docker compose down
```

---

## Rebuild After Code Changes

```bash
docker compose up --build
```

---

## View Logs

```bash
docker compose logs
```

Follow logs continuously:

```bash
docker compose logs -f
```

---

## Troubleshooting

### Port already in use

Stop the process using port 8000 or change the port mapping in `docker-compose.yml`.

---

### Invalid Gemini API Key

Verify that:

- `.env` exists
- `GEMINI_API_KEY` is correct
- The API key is active

---

### Container won't start

Check the logs:

```bash
docker compose logs
```

---

## Project Structure

```
autonomous-ai-agent/
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── requirements.txt
├── app.py
│
├── agent/
├── api/
├── core/
├── docs/
├── output/
├── tests/
└── ...
```

---

## Deployment Checklist

- Docker installed
- Environment variables configured
- Docker image built successfully
- Container running
- FastAPI accessible
- Swagger UI accessible
- API requests working

Deployment is complete.