# syntax=docker/dockerfile:1
# NekoCafe Member Service — Multi-stage Node.js build

# Stage 1: Build dependencies
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install --production --ignore-scripts
COPY . .

# Stage 2: Production runtime
FROM node:20-alpine AS runtime

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Install dumb-init for signal handling
RUN apk add --no-cache dumb-init=1.2.5-r3

WORKDIR /app

# Copy production artifacts
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package*.json ./
COPY --from=build /app/src ./src

# Set ownership
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8081

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:8081/healthz', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "src/index.js"]
