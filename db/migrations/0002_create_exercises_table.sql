DROP TABLE IF EXISTS session_exercises;
DROP TABLE IF EXISTS exercises;

CREATE TABLE exercises (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    slug TEXT UNIQUE,
    primary_muscle TEXT NOT NULL CHECK (primary_muscle IN (
        'Pectoraux','Dorsaux','Épaules','Biceps','Triceps','Trapèzes','Lombaires','Abdominaux','Obliques','Quadriceps','Ischio-jambiers','Fessiers','Mollets','Avant-bras','Cou','Corps entier'
    )),
    secondary_muscles TEXT,
    equipment TEXT CHECK (equipment IS NULL OR equipment IN (
        'Barre','Haltères','Kettlebell','Poulie/Câble','Machine guidée','Smith','Élastiques','TRX/Anneaux','Poids du corps','Banc/Step/Box','Swiss Ball','Médecine ball','Sled/Prowler'
    )),
    pattern TEXT CHECK (pattern IS NULL OR pattern IN (
        'Squat','Hinge','Fente','Push horizontal','Push vertical','Tirage horizontal','Tirage vertical','Gainage','Anti-rotation','Rotation','Locomotion/Carry','Saut/Pliométrie','Conditioning','Mobilité'
    )),
    difficulty INTEGER CHECK (difficulty BETWEEN 1 AND 5),
    tempo TEXT,
    rep_range TEXT,
    rpe_default REAL CHECK (rpe_default BETWEEN 0 AND 10),
    rest_s_default INTEGER CHECK (rest_s_default >= 0),
    cues TEXT,
    image_path TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s','now')),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE TABLE session_exercises (
    session_id INTEGER NOT NULL,
    exercise_id TEXT NOT NULL,
    sets INTEGER NOT NULL CHECK (sets > 0),
    repetitions INTEGER NOT NULL CHECK (repetitions > 0),
    weight REAL CHECK (weight >= 0),
    PRIMARY KEY (session_id, exercise_id),
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
);
