FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_BACKEND_URL=$NEXT_PUBLIC_BACKEND_URL
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

ENV NODE_ENV=production
EXPOSE 3000

CMD ["npm", "start"]
