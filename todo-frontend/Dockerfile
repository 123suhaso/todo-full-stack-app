# Stage 1: Build React app
FROM node:20 AS builder
WORKDIR /app

# Copy package files
COPY package*.json ./

# Upgrade npm to latest stable version
RUN npm install -g npm@11.5.2

# Install dependencies with retry and alternate registry to avoid 429
RUN npm install --fetch-retries=5 --fetch-retry-mintimeout=2000 --registry=https://registry.npmmirror.com

# Copy all source files
COPY . .

# Build the app (Vite outputs to /app/dist)
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Remove default Nginx content
RUN rm -rf /usr/share/nginx/html/*

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
