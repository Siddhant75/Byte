# FOSS AI Companion Workflow Specification
## Project Overview
This document outlines the architecture, components, and phased workflow for building a stateful, memory-aware AI companion (Tamagotchi-style) using entirely Free and Open-Source Software (FOSS). The project is designed to be built iteratively using a CLI-based AI assistant (e.g., Gemini CLI).

## Core Architecture & Components

### 1. Frontend Layer (The "Cozy" Interface)
* **Framework:** Electron (Node.js/HTML/CSS/JS) for a lightweight, cross-platform desktop application.
* **Animation Engine:** Layered SVG (Native) for high-performance, FOSS-friendly state representations. This allows for smooth transitions between "sleeping," "happy," and "hungry" using dynamic CSS and path transformations.

### 2. Backend & State Manager (The "Nervous System")
* **Framework:** Python with FastAPI. Acts as the bridge between the UI and the AI models.
* **Database:** SQLite. Handles the deterministic state machine. Tracks numeric variables: `level`, `hunger`, `mood`, `energy`, and `experience_points`.
* **Time-Decay Engine:** Implemented using `APScheduler` (AsyncIOScheduler) in `main.py`. It runs a periodic background job (every 5 minutes) to decrease `hunger`, `energy`, and `happiness` via the `decay_stats()` function in `database.py`.

### 3. Memory Engine (The "Hippocampus")
* **Database:** ChromaDB (Local).
* **Function:** Stores vectorized representations of user interactions. Enables Retrieval-Augmented Generation (RAG) so the companion remembers past conversations and user preferences.

### 4. Brain & Inference (The "Cortex")
* **Engine:** Ollama or Llama.cpp running locally.
* **Model:** Open-weights SLM (e.g., Llama-3-8B or Phi-3-Mini).
* **Dynamic Prompting:** A specialized pipeline that injects current SQLite states and ChromaDB context into the system prompt before generating a response.

---

## UI Strategy: Layered SVG Approach

To maintain a lightweight and premium aesthetic without external dependencies (like Rive), we use a "Layered SVG" architecture:

1.  **Base Layer:** Static geometry for the body, feet, and surroundings (desk/computer).
2.  **Expressive Layer:** Mouths and eyes that swap paths or transform based on state:
    *   **Happy:** Upward arc/V-shape mouth.
    *   **Sad:** Inverted arc mouth + slanted ears.
    *   **Hungry:** Flat line mouth + slightly rotated ears.
    *   **Sleeping:** Horizontal line eyes + dimmed opacity.
3.  **Environmental Layer:** CSS-driven atmospheric elements:
    *   **Glow:** Radial gradients that pulse based on Energy.
    *   **Particles:** Floating pixel-code elements for the coder aesthetic.
4.  **Integration:** The `renderStats` function in `renderer.js` toggles CSS classes (e.g., `.is-sleeping`, `.hungry`) on the root `<svg>` or `<body>` to trigger these visual transitions.

---

## Development Phases

### Phase 1: Foundation & Scaffolding
* **Component 1.1: Project Structure.** Scaffolding the monorepo structure (separating `/frontend`, `/backend`, `/memory`, and `/docs`).
* **Component 1.2: Base Backend.** Setting up the Python FastAPI server with a health-check endpoint.
* **Component 1.3: Base Frontend.** Initializing a minimal Electron application that can render a basic canvas and fetch data from the FastAPI backend.

### Phase 2: Core State Machine & APIs
* **Component 2.1: SQLite Initialization.** Creating the database schema for the companion's stats.
* **Component 2.2: State Management APIs.** Creating CRUD endpoints to retrieve current stats and update them (e.g., a `/feed` or `/play` endpoint).
* **Component 2.3: Time-Decay Background Job.** COMPLETED. Using `APScheduler` to run `decay_stats()` every 5 minutes. Includes database migration logic to handle adding new stat columns (`hunger`, `energy`, `happiness`) to existing deployments.

### Phase 3: The Memory Engine
* **Component 3.1: ChromaDB Integration.** Embedding a local vector store into the Python backend.
* **Component 3.2: Interaction Logging.** Writing middleware that captures user interactions, embeds the text using a lightweight local embedding model, and stores it in the vector database.
* **Component 3.3: Context Retrieval.** Building the search function to fetch relevant past interactions based on a new user query.

### Phase 4: Agent Logic & Inference
* **Component 4.1: Local LLM Connection.** Hooking up FastAPI to a local instance of Ollama/Llama.cpp via REST or native bindings.
* **Component 4.2: Dynamic System Prompts.** Creating the plain-text templating system that dynamically injects SQLite stats and ChromaDB memories into the LLM's instructions.
* **Component 4.3: Action Parsing.** COMPLETED. The LLM can now output structured data via `[ACTIONS: {"log_minutes": X, "set_activity": "Y"}]` tags. The backend parses these tags, updates the SQLite state, and strips the tags from the user-facing chat.

### Phase 5: UI Integration & Animation
* **Component 5.1: State Polling/WebSockets.** Connecting the Electron frontend to the FastAPI backend to continuously sync the companion's status.
* **Component 5.2: State Machine Mapping.** Mapping the numerical SQLite stats to specific visual animation states (e.g., mapping `mood < 30` to a "sad" idle animation).
* **Component 5.3: Chat Interface.** Building the UI component for the user to chat with and command the companion.

---

## Pending Work & Next Steps

### 1. Functional Enhancements (The "Intelligence" Gap)
* **[TAG REFINEMENT] Component 4.4:** Refine the stripping of `[SYSTEM_EVENT]` and `[ACTIONS]` tags to ensure they never leak into the UI during streaming. (Partially Completed).
* **[VOICE INTERFACE]:** Potential addition of a local TTS (e.g., Piper) and STT (e.g., Whisper.cpp) engine for a hands-free experience.

### 2. Visual & Aesthetic Overhaul (The "Cozy" Factor)
* **[ANIMATION SYSTEM] Component 5.2:** Refine the **Layered SVG** character. Implement specialized state machine transitions for "Idle," "Eating," "Sleeping," and "Happy" using CSS Keyframes and SVG path morphing.
* **[PREMIUM UI DESIGN]:** Redesign the Electron interface using modern CSS principles:
    * Glassmorphism effects for the chat window.
    * Custom typography (Inter/Outfit).
    * Smooth SVG-based progress bars for stats.
    * Dynamic background colors that shift based on the companion's mood or time of day.

### 3. Stability & Optimization
* **[LOCAL LLM TUNING]:** Optimize system prompts to reduce latency and prevent "hallucinations" regarding current pet stats.
* **[PERSISTENCE FIXES]:** Ensure the Electron window remembers its position and the backend gracefully handles Ollama connection failures.

---

## How to Run

### 1. Prerequisites
*   **Python 3.10+**
*   **Node.js & npm**
*   **Ollama:** Install from [ollama.com](https://ollama.com) and run `ollama pull llama3`.

### 2. Backend Setup
```powershell
# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
python backend/main.py
```

### 3. Frontend Setup
```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the Electron application
npm start
```

### 4. Memory Management
The system will automatically create a `memory_db` folder and a `pet_state.db` file in the root and backend directories respectively. To reset the pet, simply delete these files.
