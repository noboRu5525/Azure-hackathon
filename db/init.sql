CREATE DATABASE records;
use records;

CREATE TABLE account(
	name VARCHAR(20) COLLATE utf8mb4_unicode_ci NOT NULL,
	password VARCHAR(20) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE goals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    objective VARCHAR(255) NOT NULL,
    current_state VARCHAR(255) NOT NULL,
    deadline DATE NOT NULL,
    category ENUM('1', '2', '3') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE deadlines (
    goal_id INT PRIMARY KEY,
    remaining_days INT NOT NULL,
    FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
);

INSERT INTO account
	(name, password)
VALUES
	('azure','azure');
