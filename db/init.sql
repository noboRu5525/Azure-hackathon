CREATE DATABASE records;
use records;

CREATE TABLE account(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(40) COLLATE utf8mb4_unicode_ci NOT NULL,
    password VARCHAR(20) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    startDate DATE,
    systemName VARCHAR(255) NOT NULL,
    makeDay INT NOT NULL,
    features TEXT NOT NULL,
    languages VARCHAR(255) NOT NULL,
    tools VARCHAR(255) NOT NULL,
    color VARCHAR(30),
    FOREIGN KEY (user_id) REFERENCES account(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE learning_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES account(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_id INT NOT NULL,
    days_range VARCHAR(50) NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    task_progress INT NOT NULL DEFAULT 0, -- デフォルト値を0.0に設定
    FOREIGN KEY (plan_id) REFERENCES learning_plans(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE task_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    detail TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE task_executions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    execution_date TIMESTAMP NULL DEFAULT NULL, -- NULLを許容し、デフォルト値をNULLに設定
    execution_time INT NOT NULL DEFAULT 0, -- デフォルト値を0に設定
    user_memo TEXT NULL DEFAULT NULL, -- NULLを許容し、デフォルト値をNULLに設定
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


INSERT INTO account
	(name, password)
VALUES
	('azure','azure');