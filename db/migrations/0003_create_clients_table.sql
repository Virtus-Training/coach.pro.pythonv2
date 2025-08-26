DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS nutrition_profiles;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS clients;

CREATE TABLE clients (
    id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    sex TEXT NOT NULL CHECK (sex IN ('Homme','Femme','Autre')),
    birthdate DATE NOT NULL,
    height_cm REAL NOT NULL CHECK (height_cm > 0),
    weight_kg REAL NOT NULL CHECK (weight_kg > 0),
    objective TEXT,
    injuries TEXT,
    email TEXT,
    phone TEXT,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s','now')),
    UNIQUE(first_name, last_name, birthdate)
);

CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id TEXT,
    session_date TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
);

CREATE TABLE nutrition_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id TEXT,
    calories_target INTEGER CHECK (calories_target > 0),
    protein_target REAL CHECK (protein_target >= 0),
    carbs_target REAL CHECK (carbs_target >= 0),
    fats_target REAL CHECK (fats_target >= 0),
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
);

CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id TEXT,
    amount REAL NOT NULL CHECK (amount >= 0),
    issued_on TEXT NOT NULL,
    paid INTEGER NOT NULL DEFAULT 0 CHECK (paid IN (0,1)),
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
);
