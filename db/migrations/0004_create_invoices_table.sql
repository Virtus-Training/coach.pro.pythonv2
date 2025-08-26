DROP TABLE IF EXISTS invoices;

CREATE TABLE invoices (
    id TEXT PRIMARY KEY,
    client_id TEXT,
    number TEXT NOT NULL UNIQUE,
    label TEXT,
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0),
    status TEXT NOT NULL CHECK (status IN ('Payée','Non payée')),
    issued_on DATE NOT NULL,
    paid_on DATE,
    pdf_path TEXT,
    template TEXT NOT NULL CHECK (template IN ('classic','modern','minimalist')),
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
);
