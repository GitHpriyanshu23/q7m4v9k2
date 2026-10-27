FROM node:22-alpine AS frontend
WORKDIR /build
COPY package*.json ./
RUN npm ci
COPY index.html tsconfig.json vite.config.ts ./
COPY public ./public
COPY src ./src
RUN npm run build

FROM python:3.13-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home appuser
COPY backend ./backend
COPY data ./data
COPY --from=frontend /build/dist ./dist
USER appuser
EXPOSE 8000
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
