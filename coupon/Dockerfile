FROM node:18-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Expose port
EXPOSE 8002

CMD ["node", "src/index.js"]
