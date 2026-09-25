-- Esquema PostgreSQL del proyecto HelpDesk EDU
-- Ejecutar contra una base de datos vacía, p. ej.:
--   psql "postgresql://helpdesk:helpdesk@localhost:5433/helpdesk" -f docs/database/database.sql

DROP TABLE IF EXISTS ticket_history CASCADE;
DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TYPE IF EXISTS ticket_status;
DROP TYPE IF EXISTS user_role;

CREATE TYPE user_role AS ENUM ('requester', 'technician', 'admin');
CREATE TYPE ticket_status AS ENUM ('open', 'in_progress', 'resolved', 'closed');

CREATE TABLE users (
    id         SERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL UNIQUE,
    role       user_role NOT NULL
);

CREATE TABLE tickets (
    id             SERIAL PRIMARY KEY,
    title          TEXT NOT NULL,
    description    TEXT NOT NULL,
    status         ticket_status NOT NULL DEFAULT 'open',
    -- exige que el usuario referenciado exista cuando el valor no es NULL
    requester_id   INTEGER NOT NULL REFERENCES users(id),
    assignee_id    INTEGER REFERENCES users(id)
);

-- Beneficia consultas que filtran/agrupan por status (por ejemplo,
-- "tickets abiertos" o reportes agregados) cuando la selectividad y el
-- plan de ejecución lo justifican.
CREATE INDEX idx_tickets_status ON tickets(status);

CREATE TABLE comments (
    id          SERIAL PRIMARY KEY,
    ticket_id   INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    author_id   INTEGER NOT NULL REFERENCES users(id),
    body        TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ticket_history (
    id          SERIAL PRIMARY KEY,
    ticket_id   INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------
-- Datos de ejemplo (seed) usados por docs/database/queries_parcial2.sql
-- ---------------------------------------------------------------------

INSERT INTO users (name, email, role) VALUES
    ('Ana Solicitante',   'ana@helpdesk.edu',   'requester'),
    ('Bruno Solicitante', 'bruno@helpdesk.edu', 'requester'),
    ('Luis Tecnico',      'luis@helpdesk.edu',  'technician'),
    ('Marta Tecnica',     'marta@helpdesk.edu', 'technician');

-- ids esperados: 1=Ana, 2=Bruno, 3=Luis, 4=Marta

INSERT INTO tickets (title, description, status, requester_id, assignee_id) VALUES
    ('Impresora no enciende', 'La impresora del segundo piso no enciende', 'open',        1, 3),
    ('VPN caída',             'No conecta la VPN corporativa',             'open',        2, NULL),
    ('Monitor parpadea',      'Pantalla intermitente',                     'in_progress', 1, 3),
    ('Teclado defectuoso',    'No responden algunas teclas',               'resolved',    2, 4),
    ('Sin acceso a correo',   'No puede iniciar sesión en el correo',      'closed',      1, 4);

-- ids esperados: 1=Impresora, 2=VPN, 3=Monitor, 4=Teclado, 5=Correo

INSERT INTO comments (ticket_id, author_id, body) VALUES
    (1, 3, 'Se revisó el cable de poder, sigue sin encender'),
    (3, 1, 'El parpadeo ocurre solo en la mañana');

-- El ticket 2 (VPN) y el ticket 4 (Teclado) quedan intencionalmente sin
-- comentarios para poder probar la consulta (c) de queries_parcial2.sql.

INSERT INTO ticket_history (ticket_id, description) VALUES
    (1, 'Ticket creado'),
    (1, 'Asignado a Luis Tecnico'),
    (3, 'Ticket creado'),
    (3, 'Asignado a Luis Tecnico'),
    (4, 'Ticket creado'),
    (4, 'Asignado a Marta Tecnica'),
    (4, 'Marcado como resuelto');
