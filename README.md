# Litestar & SQLAlchemy REST API

This project is a simple To-Do List REST API built with the [Litestar](https://litestar.dev/) and [SQLAlchemy 2.0](https://www.sqlalchemy.org/). It serves as a practical example for understanding core concepts like dependency injection, database transaction management, and Dockerization in a modern Python web application.

This project was originally based on the excellent [Litestar tutorial by Teclado](https://www.youtube.com/watch?v=o8gWK1wqro0) and has been expanded to highlight key development patterns and lessons learned.

## Features

-   **Create To-Do Items**: `POST /todo`
-   **List All To-Do Items**: `GET /todos`
-   **Async First**: Built with `asyncio` and `asyncpg` / `aiosqlite`.
-   **Database Integration**: Uses SQLAlchemy 2.0 ORM with Litestar's plugin.
-   **Data Validation**: Leverages Litestar's DTOs, built on Pydantic.
-   **Containerized**: Fully configured to run with Docker.
-   **Interactive API Docs**: Automatic Swagger UI at `/schema/swagger`.

## Getting Started

Follow these instructions to get the project running on your local machine for development and testing.

### Prerequisites

You will need the following software installed on your system:

1.  [Git](https://git-scm.com/downloads)
2.  [Python 3.11+](https://www.python.org/downloads/)
3.  [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Installation & Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/pbrazeale/litestar_REST_API.git
cd litestar_REST_API
```

#### 2. Choose Your Runtime Method

You can run this application using Docker (recommended for consistency) or a local Python virtual environment.

---

### Option A: Running with Docker (Recommended)

This is the simplest and most reliable way to run the application, as it ensures a consistent environment.

1.  **Build the Docker Image:**
    This command builds a Docker image named `litestar-api` based on the instructions in the `Dockerfile`.

    ```bash
    docker build -t litestar-api .
    ```

2.  **Run the Docker Container:**
    This command starts a container from the image, connecting it to your local project files for a seamless live development experience.

    ```bash
    docker run --rm -p 8000:80 -v "$(pwd):/app" litestar-api
    ```

    **Command Breakdown:**

    *   `--rm`: Automatically removes the container when it stops. This is good practice for development to avoid a build-up of old containers.

    *   `-p 8000:80`: Maps port `8000` on your host machine to port `80` inside the container (the port exposed in the `Dockerfile`). This lets you access the API at `http://localhost:8000`.

    *   `-v "$(pwd):/app"`: This mounts the entire current project directory on your host (`$(pwd)`) into the `/app` directory inside the container. This is a critical step for two reasons:
        1.  **Hot-Reloading:** When you save changes to `app.py` or any other project file, the Litestar server inside the container will automatically detect them and restart, applying your changes instantly.
        2.  **Data Persistence:** This ensures that the `db.sqlite` database file created by the application is written to your local project folder, not just inside the temporary container. **This means your data will still be there after you stop and restart the container.** Without this volume mount, any data you add to the database would be lost.

### Option B: Running with a Local Virtual Environment

This method is useful if you prefer not to use Docker or want to manage dependencies directly.

1.  **Create and Activate a Virtual Environment:**
    ```bash
    # For macOS / Linux
    python3 -m venv .venv
    source .venv/bin/activate

    # For Windows
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application:**
    The Litestar CLI will start a development server with hot-reloading enabled.

    ```bash
    litestar run --reload
    ```

### 3. Verify the Application is Running

-   Open your browser to **[http://127.0.0.1:8000/todos](http://127.0.0.1:8000/todos)**
-   Explore the interactive API documentation at **[http://127.0.0.1:8000/schema/swagger](http://127.0.0.1:8000/schema/swagger)**

---

## API Usage Examples

You can use the Swagger UI or a tool like `curl` to interact with the API.

### Create a To-Do Item

```bash
curl -X POST "http://127.0.0.1:8000/todo" \
     -H "Content-Type: application/json" \
     -d '{"task": "Learn Litestar transaction management", "user_id": 1}'
```

**Expected Response:**

```json
{
  "id": 1,
  "task": "Learn Litestar transaction management",
  "user_id": 1
}
```

### Get All To-Do Items

```bash
curl -X GET "http://127.0.0.1:8000/todos"
```

**Expected Response:**

```json
[
  {
    "id": 1,
    "task": "Learn Litestar transaction management",
    "user_id": 1
  }
]
```

---

## Lessons Learned & Key Concepts

This project demonstrates several important patterns for building robust APIs.

### 1. Explicit vs. Implicit Transaction Management

A critical part of a database application is managing transactions (commit/rollback). The Litestar SQLAlchemy plugin offers two ways to do this, and using both simultaneously will cause an error.

-   **Implicit Method (Plugin-driven):** The plugin can automatically commit the session before sending a response using the `autocommit_before_send_handler`. This is simple but hides the transaction logic.
-   **Explicit Method (Dependency-driven):** You can define a dependency that wraps your handler in a transaction block (`async with db_session.begin():`). This is more verbose but makes the transaction boundaries clear and explicit in your code.

**This repository uses the explicit method, as it is generally preferred for clarity and easier debugging.**

The `provide_transaction` dependency manages the session lifecycle. Note how it also includes `try...except` to catch specific database errors and convert them into a clean HTTP response.

```python
# app.py

async def provide_transaction(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncSession, None]:
    try:
        # This block starts a transaction and automatically
        # commits it if the block succeeds, or rolls it back
        # if an exception occurs.
        async with db_session.begin():
            yield db_session
    except IntegrityError as exc:
        # Catches database integrity errors (e.g., duplicate primary key)
        # and returns a user-friendly HTTP 409 Conflict error.
        raise ClientException(
            status_code=HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

# To make this work, we MUST remove the autocommit handler from the plugin config.
# This prevents a "double commit" error.

db_config = SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///db.sqlite",
    # ...
    # before_send_handler=autocommit_before_send_handler, # <-- THIS LINE IS REMOVED
)

app = Litestar(
    # ...
    dependencies={"transaction": provide_transaction},
    # ...
)
```

### 2. Data Transfer Objects (DTOs)

Litestar uses DTOs to control how data is serialized (outgoing responses) and deserialized (incoming requests). In this project, `WriteDTO` prevents a client from being able to specify the `id` of a new To-Do item, as the database should generate it.

```python
# app.py

class WriteDTO(SQLAlchemyDTO[ToDo]):
    # This config tells the DTO to ignore the 'id' field
    # when processing incoming data for creating a new ToDo.
    config = SQLAlchemyDTOConfig(exclude={"id"})

@post("/todo", dto=WriteDTO)
async def create_todo(data: ToDo, transaction: AsyncSession) -> ToDo:
    # 'data' is an instance of the ToDo model, created from
    # the request payload, with the 'id' field excluded.
    transaction.add(data)
    await transaction.flush() # Flushes to the DB to get the generated ID
    return data
```

## Next Steps

This project provides a solid foundation. You can fork it and try implementing:

-   [ ] **Update** (`PUT /todo/{item_id}`) and **Delete** (`DELETE /todo/{item_id}`) endpoints.
-   [ ] Per-item lookups (`GET /todo/{item_id}`).
-   [ ] A `User` model and a relationship between `User` and `ToDo`.
-   [ ] User authentication to protect the endpoints.
-   [ ] More advanced error handling.