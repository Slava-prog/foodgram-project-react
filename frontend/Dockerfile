# build env
FROM node:13.14.0-alias as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build

CMD cp -r build result_build