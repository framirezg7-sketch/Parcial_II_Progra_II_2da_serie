# Segundo Parcial — Programación II

**Universidad Mariano Gálvez de Guatemala**
**Facultad de Ingeniería en Sistemas de Información**

| | |
|---|---|
| Asignatura | Programación II |
| Catedrático | Ing. Richard Ortiz Sasvin |
| Estudiante | Alex Ramírez |
| Evaluación | Segundo Parcial — Serie II (práctica sobre HelpDesk EDU) |
| Contenido | Semanas 7 a 11 — Python, PostgreSQL, SQLAlchemy |
| Fecha | 24 de septiembre de 2026 |

## Índice

1. [Introducción](#1-introducción)
2. [Objetivos](#2-objetivos)
3. [Organización del repositorio](#3-organización-del-repositorio)
4. [Desarrollo de los ejercicios](#4-desarrollo-de-los-ejercicios)
5. [Instrucciones de ejecución](#5-instrucciones-de-ejecución)
6. [Instrucciones para pruebas y evidencia](#6-instrucciones-para-pruebas-y-evidencia)
7. [Publicación del repositorio en GitHub](#7-publicación-del-repositorio-en-github)
8. [Resultados obtenidos](#8-resultados-obtenidos)
9. [Conclusiones y limitaciones](#9-conclusiones-y-limitaciones)

## 1. Introducción

El presente documento constituye la entrega correspondiente a la Serie II del
Segundo Parcial del curso de Programación II, la cual consiste en cinco
ejercicios prácticos (2 puntos cada uno) desarrollados sobre el proyecto
HelpDesk EDU trabajado durante las semanas 7 a 11 del curso. Cada ejercicio
aborda un principio distinto de la programación orientada a objetos y del
manejo de datos: encapsulamiento, relaciones entre objetos, polimorfismo,
integridad referencial en bases de datos relacionales y persistencia con un
ORM.

## 2. Objetivos

- Aplicar encapsulamiento mediante propiedades de solo lectura y validación
  de datos en el dominio.
- Modelar relaciones entre objetos de dominio a través de servicios de
  aplicación, sin exponer detalles internos de otros servicios.
- Implementar jerarquías de excepciones propias y polimorfismo mediante
  contratos (interfaces) para el envío de notificaciones.
- Diseñar consultas SQL que demuestren integridad referencial, incluyendo el
  comportamiento de `ON DELETE CASCADE`.
- Persistir y consultar datos agregados utilizando SQLAlchemy sobre distintos
  motores de base de datos (SQLite y PostgreSQL).

## 3. Organización del repositorio

El proyecto está organizado en capas de dominio, servicios y repositorios
(ver detalle en [`README.md`](README.md)). Cada ejercicio de la Serie II se
desarrolló en una rama independiente y fue integrado a `main` mediante un
commit de fusión, conservando el historial de cada rama:

```
main
 ├─ merge Feature_etiquetasEncapsuladas
 ├─ merge Feature_observadoresRelaciones
 ├─ merge Feature_excepcionesPolimorfismo
 ├─ merge Feature_sqlIntegridadReferencial
 └─ merge Feature_consultaAgregadaSqlAlchemy
```

Este historial puede verificarse con:

```bash
git log --oneline --graph --all
```

## 4. Desarrollo de los ejercicios

### 4.1 Etiquetas y encapsulamiento

**Archivos:** `app/models/entities.py`

Se agregó a la entidad `Ticket` una colección interna de etiquetas
(`_tags`), declarada como `field(default_factory=list, init=False,
repr=False)` para que cada instancia mantenga su propia lista, sin exponerla
en el constructor ni en la representación del objeto. El acceso público se
realiza mediante:

- La propiedad de solo lectura `tags`, que devuelve una tupla inmutable.
- El método `add_tag(tag)`, que normaliza el valor (`strip().lower()`),
  rechaza cadenas vacías lanzando `ValidationError` y evita duplicados.

Al no existir un método `setter` para `tags`, cualquier intento de
asignación directa (`ticket.tags = [...]`) produce un `AttributeError`,
garantizando que la única vía de modificación sea `add_tag()`.

**Pruebas:** `tests/test_tags.py` — normalización y rechazo de duplicados,
rechazo de valores en blanco, independencia de las etiquetas entre distintas
instancias de `Ticket`, y rechazo de la reasignación pública de `tags`.

### 4.2 Observadores y relaciones entre objetos

**Archivos:** `app/services/tickets.py`

Se implementó `TicketService.watchers(ticket_id)`, que devuelve la lista de
usuarios interesados en un ticket: el solicitante y, si existe, el técnico
asignado, sin repetir usuarios que compartan el mismo identificador. El
método reutiliza `self.require(ticket_id)` para obtener el ticket y
`self._users.require(id)` para resolver cada usuario, sin acceder de forma
directa al repositorio de usuarios ni a servicios ajenos a `TicketService`.

**Pruebas:** `tests/test_watchers.py` — ticket sin técnico asignado, ticket
con técnico distinto al solicitante, propagación de `TicketNotFoundError`
para un ticket inexistente, y deduplicación cuando el solicitante y el
técnico asignado corresponden al mismo usuario.

### 4.3 Excepciones y polimorfismo

**Archivos:** `app/domain/errors.py`, `app/services/tickets.py`,
`app/services/notifications.py`

Se creó `DuplicateAssignmentError`, subclase de `DomainError`, que se lanza
desde `assign()` cuando se intenta asignar un ticket al mismo técnico que ya
lo tiene asignado. La validación ocurre antes de modificar el historial o de
emitir notificaciones, preservando el estado previo del ticket ante una
operación inválida.

Adicionalmente, se implementó `WebhookNotifier` como una nueva
implementación del contrato `Notifier`, que simula el envío a un canal
externo almacenando los payloads en `sent_payloads`, sin realizar llamadas
HTTP ni imprimir en consola. Al inyectarse por el parámetro `notifier` ya
existente en `TicketService`, no fue necesario introducir condicionales por
tipo de notificador, demostrando polimorfismo a través del contrato común.

**Pruebas:** `tests/test_assign_and_notifications.py` — excepción al
reasignar al mismo técnico sin alterar historial ni notificaciones,
reasignación válida a un técnico distinto tras el rechazo, y verificación del
payload recibido por `WebhookNotifier` en una operación válida.

### 4.4 SQL e integridad referencial

**Archivos:** `docs/database/database.sql`, `docs/database/queries_parcial2.sql`

Sobre el esquema de PostgreSQL definido en `database.sql` (tablas `users`,
`tickets`, `comments` y `ticket_history`, con las claves foráneas
correspondientes y `ON DELETE CASCADE` en `comments` y `ticket_history`), se
elaboraron las cuatro consultas solicitadas en `queries_parcial2.sql`:

- **a)** Tickets abiertos junto con el nombre del solicitante, mediante `JOIN`.
- **b)** Conteo de tickets por técnico asignado, agrupado por id y nombre,
  excluyendo técnicos sin tickets asignados mediante `HAVING` y ordenado de
  forma descendente.
- **c)** Tickets sin comentarios, mediante `NOT EXISTS`.
- **d)** Demostración de `ON DELETE CASCADE` sobre `ticket_history`: dentro
  de una transacción (`BEGIN`/`ROLLBACK`) se muestra el conteo inicial de
  eventos de historial de un ticket, su eliminación al borrar el ticket
  padre, y la recuperación del conteo original tras el `ROLLBACK`.

### 4.5 Consulta agregada y persistencia con SQLAlchemy

**Archivos:** `app/repositories/sqlalchemy.py`, `tests/test_sqlalchemy_repository.py`

Se agregó el método `count_by_status() -> dict[str, int]` a
`SqlAlchemyTicketRepository`, construido con
`select(TicketORM.status, func.count()).group_by(TicketORM.status)`, sin
modificar la interfaz abstracta `TicketRepository`. El método devuelve
únicamente los estados presentes en la base de datos y un diccionario vacío
cuando no existen tickets registrados.

**Pruebas:** se crean tres tickets (dos en un estado y uno en otro) y se
confirma la transacción (`commit`); el reporte se consulta luego desde una
**sesión nueva** sobre el mismo motor SQLite en memoria, configurado con
`StaticPool` para que todas las sesiones de la prueba compartan la misma
conexión. Esto demuestra que los datos quedaron persistidos y no son
simplemente un efecto de la sesión original. Se incluye también el caso de
una base de datos vacía.

## 5. Instrucciones de ejecución

Requisitos: Python 3.11 o superior y [uv](https://docs.astral.sh/uv/).

```bash
# Instalar dependencias (crea el entorno virtual automáticamente)
uv sync
```

El proyecto corresponde a una capa de dominio y servicios (no expone una
interfaz de línea de comandos ni una API web); su ejecución se demuestra a
través de las pruebas automatizadas (sección 6) o mediante uso interactivo de
sus componentes, por ejemplo:

```bash
uv run python
```
```python
from app.repositories.memory import InMemoryTicketRepository, InMemoryUserRepository
from app.services.users import UserService
from app.services.tickets import TicketService
from app.models.entities import Role

users = UserService(InMemoryUserRepository())
solicitante = users.create("Ana Solicitante", "ana@helpdesk.edu", Role.REQUESTER)

tickets = TicketService(InMemoryTicketRepository(), users)
ticket = tickets.create("Impresora no enciende", "No enciende la impresora", solicitante.id)
print(ticket)
```

### Base de datos PostgreSQL (requerida para el ejercicio 4)

```bash
docker compose up -d
psql "postgresql://helpdesk:helpdesk@localhost:5433/helpdesk" -f docs/database/database.sql
psql "postgresql://helpdesk:helpdesk@localhost:5433/helpdesk" -f docs/database/queries_parcial2.sql
```

El archivo `docker-compose.yml` publica el puerto `5432` del contenedor en el
puerto `5433` del equipo anfitrión; por ello la conexión desde el host se
realiza contra `localhost:5433`.

## 6. Instrucciones para pruebas y evidencia

### Pruebas automatizadas (ejercicios 1, 2, 3 y 5)

```bash
uv run pytest -q
```

Para conservar una evidencia detallada de la ejecución:

```bash
uv run pytest -v > evidencias/pytest_main_local.txt
```

El archivo [`evidencias/pytest_main_local.txt`](evidencias/pytest_main_local.txt)
contiene la evidencia de la ejecución de las 13 pruebas automatizadas del
proyecto (4 del ejercicio 1, 4 del ejercicio 2, 3 del ejercicio 3 y 2 del
ejercicio 5), todas satisfactorias. Como evidencia complementaria, se
recomienda adjuntar una captura de pantalla de la terminal al ejecutar
`uv run pytest -v`.

### Consultas SQL (ejercicio 4)

1. Levantar PostgreSQL y cargar el esquema, conforme a la sección 5.
2. Ejecutar `docs/database/queries_parcial2.sql` y conservar la salida de la
   terminal como evidencia, por ejemplo:

   ```bash
   psql "postgresql://helpdesk:helpdesk@localhost:5433/helpdesk" \
        -f docs/database/queries_parcial2.sql \
        > evidencias/queries_parcial2_salida.txt
   ```
3. Verificar en la salida obtenida que:
   - El conteo inicial de eventos de historial del ticket utilizado en la
     demostración sea mayor que cero.
   - El conteo, inmediatamente después del `DELETE`, sea cero (efecto del
     `ON DELETE CASCADE`).
   - El conteo, después del `ROLLBACK`, vuelva a coincidir con el valor
     inicial, confirmando que los datos permanecen intactos al finalizar.

## 7. Publicación del repositorio en GitHub

El repositorio local ya contiene la estructura de ramas y fusiones descrita
en la sección 3. Para publicarlo:

1. Crear un repositorio vacío en GitHub (sin README, `.gitignore` ni
   licencia iniciales, ya provistos en este proyecto).
2. Agregar el remoto y publicar todas las ramas junto con el historial de
   fusiones:

   ```bash
   git remote add origin https://github.com/<usuario>/<repositorio>.git
   git push -u origin main
   git push origin --all
   ```
3. Verificar en GitHub que las cinco ramas `Feature_*` estén presentes y que
   `main` refleje los cinco commits de fusión correspondientes.
4. Compartir el enlace del repositorio como parte de la entrega.

## 8. Resultados obtenidos

| Ejercicio | Resultado |
|---|---|
| 1. Etiquetas y encapsulamiento | 4/4 pruebas satisfactorias |
| 2. Observadores y relaciones entre objetos | 4/4 pruebas satisfactorias |
| 3. Excepciones y polimorfismo | 3/3 pruebas satisfactorias |
| 4. SQL e integridad referencial | Consultas verificadas contra el esquema; pendiente de ejecución en PostgreSQL para adjuntar la salida como evidencia (ver sección 6) |
| 5. Consulta agregada y persistencia con SQLAlchemy | 2/2 pruebas satisfactorias |

**Total de pruebas automatizadas ejecutadas:** 13/13 satisfactorias
(`uv run pytest -q`).

## 9. Conclusiones y limitaciones

El desarrollo de los cinco ejercicios permitió reforzar conceptos de diseño
orientado a objetos aplicados a un caso realista: separación de capas entre
dominio, servicios y persistencia; uso de excepciones propias para expresar
reglas de negocio; polimorfismo a través de contratos en lugar de
condicionales por tipo; e integridad referencial tanto a nivel de base de
datos (`ON DELETE CASCADE`) como de las pruebas automatizadas que la
verifican.

Como limitación de esta entrega, las consultas del ejercicio 4 fueron
diseñadas y validadas sintáctica y lógicamente contra el esquema de
`database.sql`, pero no se cuenta en este documento con la salida de una
ejecución real contra PostgreSQL; se recomienda ejecutar los pasos de la
sección 6 y adjuntar dicha salida antes de la entrega final. El resto de los
ejercicios (1, 2, 3 y 5) cuentan con evidencia completa de ejecución mediante
pruebas automatizadas.
