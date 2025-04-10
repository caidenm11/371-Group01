# Knight Club

This project is a Python-based game using Pygame. It supports both hosting and joining games over a LAN (Local Area Network), making it easy to play multiplayer with others on the same network.

---

## Setting Up the Development Environment

To get started with this project, follow these steps:

### 1. Clone the Repository

Clone the project repository to your local machine:

```bash
git clone https://github.com/caidenm11/371-Group01.git
cd 371-Group01
```

### 2. Create a Virtual Environment

A virtual environment helps to manage dependencies and keep them isolated from your system environment.

- **On macOS/Linux**:
  ```bash
  python3 -m venv venv
  ```

- **On Windows**:
  ```bash
  python -m venv venv
  ```

### 3. Activate the Virtual Environment

- **On macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

- **On Windows**:
  ```bash
  venv\Scripts\activate
  ```

Once activated, you should see `(venv)` in your terminal prompt.

### 4. Install Project Dependencies

With the virtual environment activated, install all the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Game

To launch the game, use the following command:

```bash
python startclient.py
```

This will launch the main menu of the game.

---

## Hosting and Joining a LAN Game

Follow these steps to host and join a multiplayer game over LAN:

### Hosting the Game

1. On the host machine, launch the game:
   ```bash
   python startclient.py
   ```

2. In the game menu, click **Start Server**.  
   This starts a local server on your machine.

3. Then click **Connect to Server** to initiate a connection to the server you just started.

4. Click **Refresh** to scan for available LAN servers.

5. Select the server from the list and click **Join Selected**.

6. Once all players have joined, click **Start Game** to begin the session.

### Joining the Game from Another Computer on LAN

1. On the client machine (on the same network), run:
   ```bash
   python startclient.py
   ```

2. Click **Connect to Server**.

3. Click **Refresh** to discover available LAN servers.

4. Select the host’s server and click **Join Selected**.

5. Wait for the host to start the game.

---

## Deactivating the Virtual Environment

When you're done working on the project:

```bash
deactivate
```

This will return you to your global Python environment.
