-- Clients table
CREATE TABLE IF NOT EXISTS clients (
    client_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_code TEXT NOT NULL CHECK(LENGTH(client_code)=3),
    name TEXT NOT NULL,
    address TEXT, zip_code TEXT, city TEXT,
    country TEXT NOT NULL CHECK(LENGTH(country)=2), -- lookup table for countries in further migration
    email TEXT, phone TEXT,
    vat_number TEXT, -- relevant for financials
    payment_term INTEGER,  -- relevant for financials
    notes TEXT,
    is_active INTEGER DEFAULT 1 CHECK(is_active IN (0,1)),
    created_at TEXT NOT NULL CHECK(LENGTH(created_at)=19),
    updated_at TEXT NOT NULL CHECK(LENGTH(updated_at)=19),
    deactivated_at TEXT CHECK(LENGTH(deactivated_at)=19 OR deactivated_at IS NULL)
);

-- Cases table //TODO: ipr type!
CREATE TABLE IF NOT EXISTS cases (
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_type TEXT DEFAULT 'KA' CHECK(case_type IN ('KA', 'DV', 'SM')),
    procedure_type TEXT DEFAULT 'prosecution' CHECK(procedure_type IN ('prosecution', 'opposition', 'general counselling')), 
    ipr_type TEXT DEFAULT 'PAT' CHECK(ipr_type IN ('PAT', 'TM', 'DES', 'UM')),
    client_id INTEGER NOT NULL, client_ref TEXT NOT NULL,
    title TEXT,
    jurisdiction TEXT CHECK(LENGTH(jurisdiction) = 2), -- lookup table for offices in further migration
    filing_date TEXT CHECK(LENGTH(filing_date)=19 OR filing_date IS NULL), filing_number TEXT,
    status TEXT CHECK(status IN ('filed', 'pending', 'granted', 'refused', 'withdrawn', 'expired')), -- hardcoded for now, lookup table after in further migration
    notes TEXT,
    is_open INTEGER DEFAULT 1 CHECK(is_open IN (0,1)),
    created_at TEXT NOT NULL CHECK(LENGTH(created_at)=19),
    updated_at TEXT NOT NULL CHECK(LENGTH(updated_at)=19),
    closed_at TEXT CHECK(LENGTH(closed_at)=19 or closed_at IS NULL),
    CHECK((is_open=1 AND closed_at IS NULL) OR (is_open=0 AND closed_at IS NOT NULL)),
    FOREIGN KEY (client_id) REFERENCES Clients(client_id) ON DELETE RESTRICT,
    UNIQUE (client_id, client_ref) -- <- ensure uniqueness of client_ref for client
);

-- Deadlines table
CREATE TABLE IF NOT EXISTS deadlines (
    deadline_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    due_date INTEGER NOT NULL CHECK(LENGTH(due_date)=10),
    deadline_type TEXT NOT NULL DEFAULT 'statutory' CHECK(deadline_type IN ('statutory', 'client', 'internal')), -- add later on a rule table for statuatory deadlines
    status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending', 'Done', 'Overdue')),
    completed INTEGER DEFAULT 0 CHECK(completed IN (0,1)),
    created_at TEXT NOT NULL CHECK(LENGTH(created_at)=19),
    updated_at TEXT NOT NULL CHECK(LENGTH(updated_at)=19),
    completed_at TEXT CHECK(LENGTH(completed_at)=19 OR completed_at IS NULL),
    CHECK(
        (status != 'Done' AND completed=0 AND completed_at IS NULL) OR
        (status = 'Done' AND completed=1 AND completed_at IS NOT NULL)
    ),
    FOREIGN KEY (case_id) REFERENCES Cases(case_id) ON DELETE RESTRICT
);

-- Audit field table: for fields in the the db --
CREATE TABLE IF NOT EXISTS audit_records(
    audit_field_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action in ('insert', 'update', 'delete')),
    table_record_id INTEGER NOT NULL,
    new_value TEXT NOT NULL,
    timestamp TEXT NOT NULL CHECK(LENGTH(timestamp)=19),
    hash TEXT NOT NULL,
    previous_hash TEXT
);

--Audit log: for importing migrations, backups...
CREATE TABLE IF NOT EXISTS audit_logs(
    audit_log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_level TEXT NOT NULL,
    action TEXT NOT NULL,
    description TEXT NOT NULL,
    timestamp TEXT NOT NULL CHECK(LENGTH(timestamp)=19),
    hash TEXT NOT NULL,
    previous_hash TEXT
);