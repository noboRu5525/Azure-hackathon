CREATE DATABASE records;
use records;

CREATE TABLE account(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) COLLATE utf8mb4_unicode_ci NOT NULL,
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
    FOREIGN KEY (plan_id) REFERENCES learning_plans(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE task_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    detail TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


INSERT INTO account
	(name, password)
VALUES
	('azure','azure');

CREATE TABLE colors (
    color_id INT AUTO_INCREMENT PRIMARY KEY,
    hex_value CHAR(7) NOT NULL,
    description VARCHAR(255)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO colors (hex_value, description) VALUES
('#F7928C', 'Light Red'),
('#F9C76F', 'Mustard Yellow'),
('#FFE48A', 'Pale Yellow'),
('#E8E87D', 'Light Green'),
('#9FE897', 'Mint Green'),
('#48E6E3', 'Aqua'),
('#16C0F1', 'Sky Blue'),
('#61A5FF', 'Cornflower Blue');

-- プロジェクトテーブルへのcolor_idカラムの追加
ALTER TABLE projects ADD COLUMN color_id INT, ADD FOREIGN KEY (color_id) REFERENCES colors(color_id);

INSERT INTO projects (
    user_id,
    startDate,
    systemName,
    makeDay,
    features,
    languages,
    tools,
    color_id
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, (SELECT color_id FROM colors WHERE hex_value = '%s')
)
