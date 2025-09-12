FROM node:20 AS build

WORKDIR /app

# Install deps
COPY frontend/package*.json ./
RUN npm install

# Build React app
COPY frontend/ .
RUN npm run build

# Production server (nginx)
FROM nginx:1.25-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
