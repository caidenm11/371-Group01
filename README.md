Here's an example of a `README.md` with instructions on how to create a virtual environment and install the dependencies from `requirements.txt`:

```markdown
# Game Project with Pygame

This project is a Python-based game using Pygame. It includes both client-server functionality, allowing you to either host a game or join an existing server.

## Setting Up the Development Environment

To get started with this project, follow these steps:

### 1. Clone the repository

First, clone the project repository to your local machine:

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

This will create a new folder named `venv` in your project directory.

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

With the virtual environment activated, install all the required dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

This will install Pygame and any other dependencies listed in the `requirements.txt` file.

### 5. Running the Game

You can now run the game by using the appropriate entry point.

- To start a new game and host a server:
  ```bash
  python main.py --host
  ```

- To join an existing server:
  ```bash
  python main.py --join <server_address>
  ```

### 6. Deactivate the Virtual Environment

Once you’re done working on the project, you can deactivate the virtual environment:

```bash
deactivate
```

This will return you to your global Python environment.
