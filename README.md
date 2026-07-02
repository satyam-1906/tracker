# GPS Tracker Backend

A FastAPI backend for a real-time GPS tracking application. It integrates with **Supabase** for database storage and uses the **CallMeBot API** to send warning notifications when a tracked device comes within a set radius of a specific user.

## Features

- **Webhook Endpoint (`/webhook`)**: Receives real-time location payload (latitude, longitude, deviceId) from tracking devices.
- **Batched Data Ingestion**: Webhook payloads are temporarily queued in memory and written to the Supabase database in batches every 5 seconds to optimize database performance.
- **Geofencing & Alerts**: Uses the Haversine formula to compute the distance between the tracking device and the main user (`user_c7c898ad`). If the device enters the configured alarm radius, an alert notification is sent via CallMeBot.
- **CORS Support**: Configured to work seamlessly with frontend hosts on Railway and local development.
- **Database Integration**: Standardized integration with Supabase for:
  - Storing raw historical telemetry (`tracking_data`).
  - Maintaining user list and last known locations (`Users`).
  - Configuring and activating proximity alerts (`Alarms`).

---

## Technical Architecture & Code Walkthrough

### 1. `webhook.py`
This is the core FastAPI application entrypoint.
- **Batched Inserts**: A background thread runs `calling()` recursively every 5 seconds using `threading.Timer`. It flushes the in-memory array `data` to the `tracking_data` and `Users` tables in Supabase.
- **Distance Calculation**: The `haversine()` function calculates the great-circle distance between two points on Earth using their latitudes and longitudes.
- **Alarm / Alert Logic**: `warn(payload)` runs checks for active alarms. If the tracking device is within `distance` threshold of `user_c7c898ad`, it triggers a CallMeBot API call (`https://api.callmebot.com/text.php`) to send a text alert. To prevent spamming, it deactivates the alarm immediately and utilizes a 30-second timer to re-enable it.

### 2. `database.py`
Contains the database interface using the `supabase-py` SDK.
- **Credentials**: Hardcoded connection credentials (`SUPABASE_URL` and `SUPABASE_KEY`) connect to the Supabase backend.
- **Operations**:
  - `put_data(data)`: Performs batched inserts of tracking coordinates and updates the latest coordinates on the `Users` table.
  - `add_user()`: Checks for newly discovered devices in raw telemetry and provisions them in the `Users` table with placeholder coordinates.
  - `last_known_coords()` / `get_users()`: Fetches online devices and their coordinates.
  - `get_alarms()` / `set_alarm(data)` / `delete_alarm(data)`: Manages alarm configurations.
  - `my_location()`: Queries the coordinates of the primary target device (`user_c7c898ad`).
  - `alarm_activation_state(device_id)` / `set_alarm_activation_state(...)`: Manages the alarm trigger status.

---

## Running the Backend Locally

### Prerequisites
- Python 3.10 or higher installed.

### Step-by-Step Guide
1. **Clone or navigate** to the project directory:
   ```bash
   cd tracker
   ```

2. **Create a Python Virtual Environment**:
   ```bash
   # On Windows (Command Prompt/PowerShell)
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Server**:
   Launch the FastAPI application with Uvicorn in reload mode (so it auto-updates on code changes):
   ```bash
   uvicorn webhook:app --reload --port 8000
   ```

5. **Verify Local Run**:
   Open `http://127.0.0.1:8000/` in your browser. You should see:
   ```json
   {"status": "healthy"}
   ```

---

## Deploying and Running on Railway

Railway reads the `Procfile` in the repository root to understand how to build and execute the application.

### The Procfile
The repository contains a `Procfile` with the following configuration:
```procfile
web: uvicorn webhook:app --host 0.0.0.0 --port $PORT
```
This tells Railway to run the application using `uvicorn`, listening on all interfaces (`0.0.0.0`) and bound to the dynamic port allocated via the `$PORT` environment variable.

### Step-by-Step Deployment
1. **Push your code to GitHub**:
   Create a GitHub repository and push your project files (including `webhook.py`, `database.py`, `Procfile`, and `requirements.txt`).

2. **Deploy via Railway**:
   - Log into your [Railway Dashboard](https://railway.app/).
   - Click **+ New Project** and select **Deploy from GitHub repo**.
   - Choose your repository.
   - Railway will automatically detect the Python environment and build/run your app using the `Procfile` command.

3. **Configure Domains & CORS**:
   - In Railway, go to your service's **Settings** tab.
   - Under **Networking**, click **Generate Domain** or add a custom domain to obtain your public endpoint.
   - *Note on CORS*: If your frontend URL changes, open `webhook.py` and modify the `origins` list:
     ```python
     origins = [
         'https://your-new-frontend-url.up.railway.app',
         'http://127.0.0.1:5500'
     ]
     ```

## Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET`/`HEAD` | `/` | Health check endpoint |
| `POST` | `/webhook` | Receives coordinate payload from devices and updates telemetry |
| `GET` | `/getMarker` | Retrieves last known coordinates for all tracked devices |
| `POST` | `/newUser` | Scans telemetry and adds missing users to the database |
| `GET` | `/getAlarms` | Retrieves list of all alarms |
| `POST` | `/setAlarm` | Creates a new distance warning alarm |
| `POST` | `/deleteAlarm` | Deletes a distance warning alarm |
| `GET` | `/getUsers` | Retrieves all registered device IDs |
