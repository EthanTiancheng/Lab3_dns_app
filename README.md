# Lab3_dns_app
Simplified authoritative server for a network of applications
# DNS App (AS / FS / US) — Simplified Authoritative Server Demo

This repo contains a minimal 3-service application for a simplified DNS workflow:

- **AS**: Authoritative Server (UDP 53533)
- **FS**: Fibonacci Server (HTTP 9090)
- **US**: User Server (HTTP 8080)

`docker-compose` brings up all services and a private Docker network for them to communicate.

## Repo Structure

