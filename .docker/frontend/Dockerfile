FROM oven/bun:1 AS dev

WORKDIR /app

COPY package.json ./
RUN bun install

# Source is mounted at runtime via volume for HMR
EXPOSE 5173

CMD ["bun", "run", "dev", "--host"]
