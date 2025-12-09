# Pynidus Documentation

Pynidus is a robust Python framework for building scalable, maintainable, and modular microservices. Inspired by NestJS, it leverages Python's type hints and decorators to provide a structured development experience on top of FastAPI.

## Table of Contents

- [Core Concepts](core.md)
  - Modules
  - Controllers
  - Providers
  - Dependency Injection
- [Configuration](configuration.md)
  - Environment Variables
  - ConfigService
- [Database](database.md)
  - SQLAlchemy Integration
  - Transactional Management
- [Security](security.md)
  - Role-Based Access Control
  - OAuth2 & JWT
- [Microservices](microservices.md)
  - Event-Driven Architecture
  - RabbitMQ & ZeroMQ Transports
  - TRAM Pattern (Transactional Outbox)

## Installation

```bash
uv add pynidus
```

Or with extras:

```bash
uv add "pynidus[security,rabbitmq,zeromq]"
```

## Quick Start

See the [README](../README.md) for a "Hello World" example.
