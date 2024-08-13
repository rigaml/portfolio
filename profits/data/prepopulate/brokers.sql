INSERT INTO "profits_broker" ("short_name", "name", "created")
SELECT 'ING', 'ING', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "short_name" = 'ING');

INSERT INTO "profits_broker" ("short_name", "name", "created")
SELECT 'HAL_T', 'HAL_T', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "short_name" = 'HAL_T');

INSERT INTO "profits_broker" ("short_name", "name", "created")
SELECT 'HAL_I', 'HAL_I', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "short_name" = 'HAL_I');

INSERT INTO "profits_broker" ("short_name", "name", "created")
SELECT 'II_R', 'II_R', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "short_name" = 'II_R');

INSERT INTO "profits_broker" ("short_name", "name", "created")
SELECT 'II_So', 'II_So', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "short_name" = 'II_So');

INSERT INTO "profits_broker" ("short_name", "name", "created")
SELECT 'II_Sa', 'II_Sa', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "short_name" = 'II_Sa');

INSERT INTO "profits_broker" ("short_name", "name", "created")
SELECT 'T_T', 'T_T', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "short_name" = 'T_T');

INSERT INTO "profits_broker" ("short_name", "name", "created")
SELECT 'T_I', 'T_I', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_broker" WHERE "short_name" = 'T_I');