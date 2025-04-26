# Build frontend
FROM node:18 as frontend
WORKDIR /app
COPY frontend ./frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Backend
FROM python:3.10-slim
WORKDIR /app
COPY backend ./backend
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy frontend into backend
COPY --from=frontend /app/frontend/dist ./frontend_dist
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000
CMD ["/docker-entrypoint.sh"]