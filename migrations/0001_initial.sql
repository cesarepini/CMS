-- Clients table
CREATE TABLE IF NOT EXISTS clients (
    client_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_code TEXT NOT NULL UNIQUE CHECK(LENGTH(client_code)=3),
    name TEXT NOT NULL CHECK(LENGTH(name) > 0),
    address TEXT, 
    zip_code TEXT, 
    city TEXT,
    country TEXT NOT NULL CHECK(LENGTH(country)=2),
    email TEXT CHECK(email IS NULL OR (LENGTH(email) > 0 AND email LIKE '%_@_%._%')),
    phone TEXT,
    vat_number TEXT,
    payment_term INTEGER,
    notes TEXT,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1)),
    created_at TEXT NOT NULL CHECK(DATETIME(created_at) IS NOT NULL),
    updated_at TEXT NOT NULL CHECK(DATETIME(updated_at) IS NOT NULL),
    deactivated_at TEXT CHECK(deactivated_at IS NULL OR DATETIME(deactivated_at) IS NOT NULL)
);

-- Cases table
CREATE TABLE IF NOT EXISTS cases (
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_type TEXT DEFAULT 'KA' CHECK(case_type IN ('KA', 'DV', 'SM')),
    procedure_type TEXT DEFAULT 'prosecution' CHECK(procedure_type IN ('prosecution', 'opposition', 'general counselling') or procedure_type IS NULL), 
    ipr_type TEXT DEFAULT 'PAT' CHECK(ipr_type IN ('PAT', 'TM', 'DES', 'UM') or ipr_type IS NULL),
    client_id INTEGER NOT NULL, 
    client_ref TEXT NOT NULL CHECK(LENGTH(client_ref) > 0) COLLATE NOCASE,
    title TEXT CHECK(title IS NULL OR LENGTH(title)>0),
    jurisdiction TEXT CHECK(jurisdiction IS NULL OR LENGTH(jurisdiction) = 2),
    filing_date TEXT CHECK(filing_date IS NULL OR DATE(filing_date) IS NOT NULL),
    filing_number TEXT CHECK(filing_number IS NULL OR LENGTH(filing_number)>0),
    status TEXT CHECK(status IN ('filed', 'pending', 'granted', 'refused', 'withdrawn', 'expired') or status IS NULL),
    notes TEXT CHECK(notes IS NULL OR LENGTH(notes)>0),
    is_open INTEGER DEFAULT 1 CHECK(is_open IN (0,1)),
    created_at TEXT NOT NULL CHECK(DATETIME(created_at) IS NOT NULL),
    updated_at TEXT NOT NULL CHECK(DATETIME(updated_at) IS NOT NULL),
    closed_at TEXT CHECK(closed_at IS NULL OR DATETIME(closed_at) IS NOT NULL),
    CHECK((is_open=1 AND closed_at IS NULL) OR (is_open=0 AND closed_at IS NOT NULL)),
    FOREIGN KEY (client_id) REFERENCES Clients(client_id) ON DELETE RESTRICT,
    UNIQUE (client_id, client_ref)
);

-- Deadlines table
CREATE TABLE IF NOT EXISTS deadlines (
    deadline_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    description TEXT NOT NULL CHECK(LENGTH(description) > 0),
    due_date TEXT NOT NULL CHECK(DATE(due_date) IS NOT NULL),
    deadline_type TEXT NOT NULL DEFAULT 'statutory' CHECK(deadline_type IN ('statutory', 'client', 'internal')),
    status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending', 'Done', 'Overdue')),
    completed INTEGER DEFAULT 0 CHECK(completed IN (0,1)),
    created_at TEXT NOT NULL CHECK(DATETIME(created_at) IS NOT NULL),
    updated_at TEXT NOT NULL CHECK(DATETIME(updated_at) IS NOT NULL),
    completed_at TEXT CHECK(completed_at IS NULL OR DATETIME(completed_at) IS NOT NULL),
    CHECK(
        (status != 'Done' AND completed=0 AND completed_at IS NULL) OR
        (status = 'Done' AND completed=1 AND completed_at IS NOT NULL)
    ),
    FOREIGN KEY (case_id) REFERENCES Cases(case_id) ON DELETE RESTRICT
);

-- Audit field table: for fields in the the db --
CREATE TABLE IF NOT EXISTS audit_records(
    audit_field_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL CHECK(LENGTH(table_name)>0),
    action TEXT NOT NULL CHECK(action in ('insert', 'update', 'delete')),
    table_record_id INTEGER NOT NULL,
    new_value TEXT NOT NULL CHECK(LENGTH(new_value)>0),
    timestamp TEXT NOT NULL CHECK(DATETIME(timestamp) IS NOT NULL),
    hash TEXT NOT NULL CHECK(LENGTH(hash)>0),
    previous_hash TEXT CHECK(LENGTH(previous_hash)>0)
);

--Audit log: for importing migrations, backups...
CREATE TABLE IF NOT EXISTS audit_logs(
    audit_log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_level TEXT NOT NULL CHECK(LENGTH(log_level)>0),
    action TEXT NOT NULL CHECK(LENGTH(action)>0),
    description TEXT NOT NULL CHECK(LENGTH(description)>0),
    timestamp TEXT NOT NULL CHECK(DATETIME(timestamp) IS NOT NULL), -- Enforces a valid datetime format
    hash TEXT NOT NULL CHECK(LENGTH(hash)>0),
    previous_hash TEXT CHECK(LENGTH(previous_hash)>0)
);