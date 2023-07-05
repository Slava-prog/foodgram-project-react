# build env
FROM node:13.14.0-slim as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build
RUN npm install --global http-server

CMD ["npx", "-y", "http-server", "-p", "8000", "/app/build"]
