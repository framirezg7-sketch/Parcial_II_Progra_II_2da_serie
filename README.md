# HelpDesk EDU

Sistema de gestión de tickets de soporte técnico (HelpDesk) desarrollado como
proyecto de estudio para el curso de Programación II. Implementa una
arquitectura por capas (dominio, servicios y repositorios) que separa las
reglas de negocio de los detalles de persistencia y notificación.

## Descripción general

El sistema modela el ciclo de vida de un ticket de soporte: creación,
asignación a un técnico, comentarios, historial de eventos y notificaciones
asociadas a cada cambio de estado. La persistencia es intercambiable: existe
una implementación en memoria (para pruebas y demostraciones) y una
implementación sobre SQLAlchemy compatible tanto con SQLite como con
PostgreSQL.

## Arquitectura

```
app/
├── domain/
│   └── errors.py         Jerarquía de excepciones de dominio
├── models/
│   └── entities.py       Entidades: User, Ticket, Comment, HistoryEvent
├── repositories/
│   ├── base.py           Contratos (ABC): TicketRepository, UserRepository
│   ├── memory.py         Implementación en memoria
│   └── sqlalchemy.py     Modelos ORM y repositorio SQLAlchemy
└── services/
    ├── users.py          UserService
    ├── tickets.py        TicketService (reglas de negocio)
    └── notifications.py  Contrato Notifier e implementaciones

docs/database/
├── database.sql              Esquema PostgreSQL y datos de ejemplo
└── queries_parcial2.sql      Consultas SQL del Segundo Parcial

tests/                         Pruebas automatizadas (pytest)
```

La capa de servicios (`TicketService`, `UserService`) depende únicamente de
los contratos abstractos `TicketRepository`, `UserRepository` y `Notifier`,
sin conocer detalles de SQLAlchemy ni de un canal de notificación concreto.
Este diseño permite verificar toda la lógica de negocio mediante repositorios
en memoria y notificadores de prueba, sin requerir una base de datos real.

## Tecnologías utilizadas

- Python 3.11+
- SQLAlchemy 2.x (ORM)
- PostgreSQL (persistencia relacional) y SQLite en memoria (pruebas)
- pytest (pruebas automatizadas)
- uv (gestión de entorno y dependencias)
- Docker / Docker Compose (contenedor de PostgreSQL)

## Requisitos previos

- Python 3.11 o superior
- [uv](https://docs.astral.sh/uv/)
- Docker y Docker Compose (únicamente para el ejercicio que requiere PostgreSQL)

## Instalación

```bash
uv sync
```

## Ejecución de las pruebas

```bash
uv run pytest -q
```

## Documentación de la entrega

La documentación específica de la entrega del Segundo Parcial —instrucciones
de ejecución, generación de evidencias, publicación en GitHub, descripción de
la solución de cada ejercicio, resultados y limitaciones— se encuentra en
[`README_parcial2.md`](README_parcial2.md).

## Autor

Alex Ramírez — Ingeniería en Sistemas de Información
