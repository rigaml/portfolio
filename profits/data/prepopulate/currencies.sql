INSERT INTO "profits_currency" ("iso_code", "description", "created")
SELECT 'GBP', 'GBP', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_currency" WHERE "iso_code" = 'GBP');

INSERT INTO "profits_currency" ("iso_code", "description", "created")
SELECT 'USD', 'USD', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_currency" WHERE "iso_code" = 'USD');

INSERT INTO "profits_currency" ("iso_code", "description", "created")
SELECT 'EUR', 'EUR', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "profits_currency" WHERE "iso_code" = 'EUR');