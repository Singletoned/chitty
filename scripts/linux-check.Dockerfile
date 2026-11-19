FROM ghcr.io/astral-sh/uv:0.13.5 AS uv
FROM node:22.23.5-bookworm
COPY --from=uv /uv /uvx /usr/local/bin/
USER node
RUN mkdir -p /home/node/.cache/uv /home/node/.npm && uv python install 3.12
WORKDIR /home/node
