FROM node:20 AS build
WORKDIR /app
COPY . ./

ARG GITHUB_CLIENT_ID
ARG GOOGLE_CLIENT_ID

RUN echo "REACT_APP_GITHUB_CLIENT_ID=$GITHUB_CLIENT_ID" > .env && \
    echo "REACT_APP_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID" >> .env

RUN npm install
RUN npm run build

FROM node:20-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/build ./build

EXPOSE 3000
CMD ["serve", "-s", "build", "-l", "5002"]
