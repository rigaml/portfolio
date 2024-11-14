INSERT INTO "profits_broker" ("name", "full_name", "created_at")
SELECT 'ING', 'ING', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "name" = 'ING');

INSERT INTO "profits_broker" ("name", "full_name", "created_at")
SELECT 'HAL', 'HAL', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "name" = 'HAL');

INSERT INTO "profits_broker" ("name", "full_name", "created_at")
SELECT 'II', 'II', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "name" = 'II');

INSERT INTO "profits_broker" ("name", "full_name", "created_at")
SELECT 'T212', 'T212', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "name" = 'T212');