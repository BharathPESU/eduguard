# ════════════════════════════════════════════════════════════
# EduGuard AI — Frontend Dockerfile
# Stage 1: Build  (Node 20 + Vite)
# Stage 2: Serve  (nginx:alpine)
# ════════════════════════════════════════════════════════════

# ── Stage 1: Build ────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Install deps
COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

# Copy source and build
# VITE_API_URL is injected at build time via --build-arg
ARG VITE_API_URL=https://eduguard-backend-HASH-ew.a.run.app
ENV VITE_API_URL=${VITE_API_URL}

COPY . .
RUN npm run build


# ── Stage 2: Serve ────────────────────────────────────────
FROM nginx:1.27-alpine AS runner

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Custom nginx config for React SPA (copied from frontend root)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy Vite build output
COPY --from=builder /app/dist /usr/share/nginx/html

# Cloud Run uses PORT env var
ENV PORT=8080
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
