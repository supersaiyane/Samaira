# =========================
# Docs Service (HonKit)
# =========================
FROM node:20-alpine

WORKDIR /docs

# Install HonKit
COPY docs/package*.json ./
RUN npm install

# Copy book.json and markdown docs
COPY docs/ ./

# Default command -> serve docs
EXPOSE 4000
CMD ["npm", "run", "serve"]
