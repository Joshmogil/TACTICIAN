# TACTICIAN

This repository contains two related projects:

- **FastAPI backend** under `app/` for generating workout plans, authenticating
  users and storing workout history.  Several utilities in `app/ai/` use
  Google\'s generative models to create and adjust weekly workout plans.
- **groove** iOS application under `groove/` built with SwiftUI that displays a
  user\'s weekly workout schedule from JSON files.

Example workout weeks are stored in the root of the repository as CSV/JSON
files.

## Requirements

- Python 3.11+
- The packages listed in `requirements.txt`

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the API

Launch the FastAPI server with:

```bash
uvicorn app.app:app --reload
```

The interactive documentation will be available at
`http://localhost:8000/docs` once the server starts.

## Docker

A `Dockerfile` is provided for container based deployments:

```bash
docker build -t tactician .
docker run -p 8080:8080 tactician
```

## fly.io Deployment

The repository includes a sample `fly.toml` for deploying the API to Fly.io.
After installing `flyctl` you can deploy with:

```bash
fly launch --no-deploy  # creates the app
fly deploy              # builds the Dockerfile and deploys
```

## Project Layout

```
.
├── app/                 # FastAPI application and AI helpers
├── groove/              # SwiftUI client app
├── Dockerfile           # container build for the API
├── fly.toml             # Fly.io configuration
├── requirements.txt
└── week_1*.csv / json   # example workout weeks
```
