# 💖 E-Love (Backend)

Welcome to **E-Love Chat Microservice**! 🎮❤️ This microservice is designed for E-Love application in order to prevent a big number of different dependencies. He's responsible for storing business-logic that is related with users chats, dialogs, etc.

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed for this backend service:

- E-Love frontend
- E-Love fe-api gateway
- Python Interpreter (version 3.10)
- Docker installed & Docker Desktop application
- Poetry
- Taskfile

### Why Use Poetry?

Poetry is a dependency management and packaging tool for Python. It provides a more comprehensive and user-friendly approach compared to pip,
by handling dependencies in a lock file, managing virtual environments, and simplifying the publishing process.

### Taskfile

Taskfile is a tool for defining and running project-specific tasks. It simplifies complex command sequences into simple task invocations.

To install Taskfile:

Install Taskfile using the official installation method - `https://taskfile.dev/`

### Installation

1. Clone the repo:

   ```sh
   git clone https://github.com/yourusername/e-love.git
   ```

---

IMPORTANT INFO

2nd and 3d parts below were automated by .vscode task-script. (doesn't work for now)
So please start our application in VSCODE from `chat-service` folder.
If this task hasn't worked, please use the next steps below this section.
(FYI, composing containers task isn't included in the script)

---

2. Navigate to the project directory:

   ```sh
   cd e-love-chat-service
   ```

3. Run dependencies installation & other stuff using Taskfile:

   ```sh
   poetry shell
   ```

   ```sh
   poetry install
   ```

   ```sh
   task compose-up
   ```

### More detailed instruction

If you're having problems this with installation, please check our docs installation page by this link - https://www.notion.so/Correct-application-startup-using-Docker-venv-e2770cf1799e4a62b23f6f3637e23b45?pvs=4

### Development

To run the app in development mode:

1. Open your Docker Desktop and search for e-love-chat-service container.

2. Run e-love-chat-service container.

### Building for Production

To build the app for production:

```sh
# Add instructions here when ready
```

### Running Tests

#### Unit Tests

```sh
# Add instructions here when ready
```

## 🛠️ Technologies Used (add another later)

- **Python**: Programming language for the backend.
- **Poetry**: Dependency management and packaging tool for Python.
- **Taskfile**: Simplifies running complex project-specific tasks.
- **Dotenv**: Manage environment variables.
- **Docker**: Manage microservices environment, etc.
