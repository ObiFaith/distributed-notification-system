# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package.json and lock file
COPY package*.json ./

# Install all dependencies including dev
RUN npm install

# Copy everything
COPY . .

# Compile TypeScript (will create dist/)
RUN npm run build

# Stage 2: Production
FROM node:18-alpine

WORKDIR /app

# Copy only package.json for prod dependencies
COPY package*.json ./

RUN npm ci --only=production

# Copy built files from builder
COPY --from=builder /app/dist ./dist

# Expose NestJS port
EXPOSE 3002

# Start the app
CMD ["node", "dist/main.js"]
