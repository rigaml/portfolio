INSERT INTO "profits_broker" ("name", "full_name", "created_at")
SELECT 'ING', 'ING', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "name" = 'ING');

INSERT INTO "profits_broker" ("name", "full_name", "created_at")
SELECT 'HAL_T', 'HAL_Trading', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "name" = 'HAL_T');

INSERT INTO "profits_broker" ("name", "full_name", "created_at")
SELECT 'HAL_I', 'HAL_ISA', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "name" = 'HAL_ISA');

INSERT INTO "profits_broker" ("name", "full_name", "created_at")
SELECT 'II_T', 'II_Trading', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "name" = 'II_T');

INSERT INTO "profits_broker" ("name", "full_name", "created_at")
SELECT 'II_So', 'II_Sofia', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "name" = 'II_So');

INSERT INTO "profits_broker" ("name", "full_name", "created_at")
SELECT 'II_Sa', 'II_Sara', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "name" = 'II_Sa');

INSERT INTO "profits_broker" ("name", "full_name", "created_at")
SELECT 'T212_T', 'T212_Trading', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "name" = 'T212_T');

INSERT INTO "profits_broker" ("name", "full_name", "created_at")
SELECT 'T212_ISA', 'T212_ISA', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "name" = 'T212_ISA');