-- Ejercicio 4 (Serie II) - SQL e integridad referencial
-- Requiere haber cargado antes el esquema y los datos de docs/database/database.sql
-- Ejecutar, por ejemplo:
--   psql "postgresql://helpdesk:helpdesk@localhost:5433/helpdesk" -f docs/database/queries_parcial2.sql

-- =======================================================================
-- a) Tickets abiertos con el nombre del solicitante (JOIN)
-- =======================================================================
SELECT
    t.id,
    t.title,
    u.name AS requester_name
FROM tickets t
JOIN users u ON u.id = t.requester_id
WHERE t.status = 'open'
ORDER BY t.id;

-- =======================================================================
-- b) Conteo de tickets por técnico asignado, agrupado por id y nombre,
--    excluyendo técnicos con conteo cero (HAVING) y orden descendente
-- =======================================================================
SELECT
    u.id AS technician_id,
    u.name AS technician_name,
    COUNT(t.id) AS ticket_count
FROM users u
LEFT JOIN tickets t ON t.assignee_id = u.id
WHERE u.role = 'technician'
GROUP BY u.id, u.name
HAVING COUNT(t.id) > 0
ORDER BY ticket_count DESC;

-- =======================================================================
-- c) Tickets sin comentarios (NOT EXISTS)
-- =======================================================================
SELECT
    t.id,
    t.title
FROM tickets t
WHERE NOT EXISTS (
    SELECT 1 FROM comments c WHERE c.ticket_id = t.id
)
ORDER BY t.id;

-- =======================================================================
-- d) Demostración de ON DELETE CASCADE sobre ticket_history,
--    envuelta en BEGIN/ROLLBACK para no alterar los datos reales.
--    Se usa el ticket 4 ("Teclado defectuoso"), que tiene 3 eventos
--    de historial cargados en el seed de database.sql.
-- =======================================================================
BEGIN;

-- Conteo inicial: debe ser mayor que cero (3 eventos para el ticket 4)
SELECT COUNT(*) AS history_count_before
FROM ticket_history
WHERE ticket_id = 4;

-- Al borrar el ticket, ON DELETE CASCADE borra también su historial
DELETE FROM tickets WHERE id = 4;

-- Conteo tras el DELETE: debe ser cero
SELECT COUNT(*) AS history_count_after_delete
FROM ticket_history
WHERE ticket_id = 4;

ROLLBACK;

-- Conteo tras el ROLLBACK: debe volver a su valor original (3),
-- demostrando que los datos permanecen intactos al finalizar.
SELECT COUNT(*) AS history_count_after_rollback
FROM ticket_history
WHERE ticket_id = 4;
