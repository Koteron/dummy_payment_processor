FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV="/opt/venv"
RUN uv venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --all-extras

COPY . .

CMD ["uv", "run", "--active", "main.py"]