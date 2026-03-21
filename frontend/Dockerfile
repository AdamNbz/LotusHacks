# ============================================================
# Dockerfile - LotusHacks Frontend (React + Vite)
# Multi-stage build: Build → Serve with nginx
# ============================================================

# --- Stage 1: Build ---
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files first for layer caching
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code and build
COPY . .

# Build arg for API URL (inject at build time)
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# --- Stage 2: Serve with nginx ---
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
