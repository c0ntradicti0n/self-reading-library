FROM node:14-alpine AS deps

RUN apk add --no-cache libc6-compat

USER node
WORKDIR /app

COPY layout_viewer_made/*.* ./
RUN yarn install --frozen-lockfile

CMD ["yarn", "run", "dev"]