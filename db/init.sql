CREATE DATABASE records;
use records;

CREATE TABLE account(
	name VARCHAR(20) COLLATE utf8mb4_unicode_ci NOT NULL,
	password VARCHAR(20) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO account
	(name, password)
VALUES
	('azure','azure');
