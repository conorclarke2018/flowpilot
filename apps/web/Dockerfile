FROM node:22-slim

RUN corepack enable

WORKDIR /repo

COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./
COPY apps/web/package.json apps/web/package.json

RUN pnpm install --frozen-lockfile

COPY apps/web apps/web

WORKDIR /repo/apps/web

EXPOSE 5173

CMD ["pnpm", "dev", "--host"]
