FROM node:13.12.0-alpine
WORKDIR /app

COPY package.json package.json
COPY package-lock.json package-lock.json

RUN npm ci

COPY . ./
RUN npm run build
RUN npm install --global http-server
CMD cp -r build result_build
VOLUME /result_build
