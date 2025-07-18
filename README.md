# LiteStar API

This proejct was built with [teclado's tutorial](https://www.youtube.com/watch?v=o8gWK1wqro0).

## Software Requiremetns

1. Python [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Docker Desktop [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
    - To learn more about Docker Boot.Dev has an excellent course:[https://www.boot.dev/courses/learn-docker](https://www.boot.dev/courses/learn-docker)

## LiteStar Notes
### To Run:
```bash
docker build -t litestar-api .
docker run -p 8000:80 -v "$(pwd):/app" litestar-api
```

Runs on: http://127.0.0.1:8000

Can test through: http://127.0.0.1:8000/schema/swagger

## Requirements
[Documentation](https://pypi.org/project/psycopg2/) I used `psycopg2-binary` instead of `psycopg2`.
