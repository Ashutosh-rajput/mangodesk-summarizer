# MangoDesk Document Summarizer

[![Status](https://img.shields.io/badge/status-active-success.svg)](https://github.com/Ashutosh-rajput/mangodesk-summarizer)
[![GitHub Issues](https://img.shields.io/github/issues/Ashutosh-rajput/mangodesk-summarizer.svg)](https://github.com/Ashutosh-rajput/mangodesk-summarizer/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/Ashutosh-rajput/mangodesk-summarizer.svg)](https://github.com/Ashutosh-rajput/mangodesk-summarizer/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

An intelligent document summarization tool powered by Google's Gemini LLM and built with FastAPI and LangChain. Upload a document, provide custom instructions, and get a tailored summary in seconds.

### ✨ **[Live Demo](https://mangodesk-summarizer-b7n0.onrender.com/)** `https://mangodesk-summarizer-b7n0.onrender.com/`✨


*(Feel free to replace this with a real screenshot of your app)*

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Development Setup](#local-development-setup)
- [Running with Docker](#running-with-docker)
- [API Endpoints](#api-endpoints)
- [Deployment](#deployment)
- [Project Structure](#project-structure)

---

## Features

*   **📄 Document Upload:** Supports `.txt`, `.pdf`, and `.docx` file uploads.
*   **🧠 AI-Powered Summarization:** Utilizes Google's Gemini model via LangChain for high-quality, concise summaries.
*   **🗣️ Custom Instructions:** Guide the AI with custom prompts (e.g., "Summarize in bullet points for executives," "Highlight only action items").
*   **✏️ Edit Summaries:** Refine and edit the generated summary with further instructions.
*   **📧 Email Integration:** Send the final summary directly to any email address.
*   **💾 Downloadable Content:** Download the summary as a `.txt` file.
*   **🚀 Modern Web Interface:** A clean, single-page frontend built with vanilla HTML, CSS, and JavaScript.
*   **🐳 Dockerized:** Fully containerized for easy setup and deployment.
*   **☁️ Cloud-Ready:** Deployed and running live on Render.

---

## Tech Stack

*   **Backend:** FastAPI, Python 3.12
*   **AI/LLM:** Google Gemini, LangChain, LangGraph
*   **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
*   **Server:** Uvicorn
*   **Containerization:** Docker
*   **Deployment:** Render, GitHub Actions for CI

---

## Getting Started

### Prerequisites

*   Python 3.11+
*   An active Google AI (Gemini) API Key. You can get one from [Google AI Studio](https://aistudio.google.com/app/apikey).
*   A Gmail account with 2-Step Verification and an App Password for the email feature.
*   [Docker](https://www.docker.com/products/docker-desktop/) (for containerized setup).

### Local Development Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Ashutosh-rajput/mangodesk-summarizer.git
    cd mangodesk-summarizer
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` file:**
    Create a file named `.env` in the project root and add your secrets.
    ```ini
    # Your Google AI API Key for Gemini
    GOOGLE_API_KEY="your_google_api_key_here"

    # Your Gmail address that will send the email
    GMAIL_SENDER_EMAIL="your-email@gmail.com"

    # The 16-character App Password you generate from your Google Account
    GMAIL_APP_PASSWORD="xxxx yyyy zzzz wwww"
    ```

5.  **Run the application:**
    The server will start on `http://127.0.0.1:8000`.
    ```bash
    uvicorn main:app --reload
    ```

6.  **Open your browser** and navigate to `http://127.0.0.1:8000`.

---

## Running with Docker

This is the recommended way to run the application for consistency.

1.  **Build the Docker image:**
    ```bash
    docker build -t mangodesk-summarizer .
    ```

2.  **Run the Docker container:**
    Pass your environment variables directly to the container using the `-e` flag.
    ```bash
    docker run -d \
      -p 8000:80 \
      -e GOOGLE_API_KEY="your_google_api_key_here" \
      -e GMAIL_SENDER_EMAIL="your-email@gmail.com" \
      -e GMAIL_APP_PASSWORD="xxxx yyyy zzzz wwww" \
      --name summarizer-app \
      mangodesk-summarizer
    ```

3.  **Access the application** at with frontend `http://localhost:8000`.
4.  **For swagger docs** `http://localhost:8000/docs`

---

## API Endpoints

The API is self-documenting. Once the application is running, you can access the interactive Swagger UI documentation at `http://localhost:8000/docs`.

| Method | Endpoint          | Description                                         |
|--------|-------------------|-----------------------------------------------------|
| `GET`  | `/`               | Serves the HTML frontend.                           |
| `POST` | `/summary`        | Upload a file and generate a summary.               |
| `POST` | `/edit-summary`   | Edit the currently stored summary with a prompt.    |
| `GET`  | `/download-txt`   | Download the current summary as a `.txt` file.      |
| `POST` | `/send-summary`   | Send the current summary to a specified email.      |

---

## Deployment

This application is configured for continuous deployment on **Render**. The deployment process is triggered automatically on every push to the `main` branch.

The project also includes a GitHub Action workflow (`.github/workflows/build-and-push.yml`) that builds the Docker image and pushes it to the GitHub Container Registry (GHCR), demonstrating a complete CI pipeline.

---

## Project Structure
