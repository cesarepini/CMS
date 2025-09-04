-- Clients table
CREATE TABLE IF NOT EXISTS Clients (
    client_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT, zip_code TEXT, city TEXT,
    country TEXT NOT NULL CHECK(LENGTH(country)=2), -- lookup table for countries in further migration
    email TEXT, phone TEXT,
    vat_number TEXT, -- relevant for financials
    payment_term INTEGER,  -- relevant for financials
    notes TEXT,
    is_active INTEGER DEFAULT 1 CHECK(is_active IN (0,1)),
    created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL, deactivated_at INTEGER,
    UNIQUE (name, address)
);

-- Cases table //TODO: ipr type!
CREATE TABLE IF NOT EXISTS Cases (
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_type TEXT DEFAULT 'KA' CHECK(case_type IN ('KA', 'DV', 'SM')),
    procedure_type TEXT DEFAULT 'prosecution' CHECK(procedure_type IN ('prosecution', 'opposition', 'general counselling')), 
    ipr_type TEXT DEFAULT 'PAT' CHECK(ipr_type IN ('PAT', 'TM', 'DES', 'UM')),
    client_id INTEGER NOT NULL, client_ref TEXT NOT NULL,
    title TEXT,
    jurisdiction TEXT CHECK(LENGTH(jurisdiction) = 2), -- lookup table for offices in further migration
    filing_date INTEGER, filing_number TEXT,
    status TEXT CHECK(status IN ('filed', 'pending', 'granted', 'refused', 'withdrawn', 'expired')), -- hardcoded for now, lookup table after in further migration
    notes TEXT,
    is_open INTEGER DEFAULT 1 CHECK(is_open IN (0,1)),
    created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL, closed_at INTEGER,
    CHECK((is_open=1 AND closed_at IS NULL) OR (is_open=0 AND closed_at IS NOT NULL)),
    FOREIGN KEY (client_id) REFERENCES Clients(client_id) ON DELETE RESTRICT,
    UNIQUE (client_id, client_ref) -- <- ensure uniqueness of client_ref for client
);

-- Deadlines table
CREATE TABLE IF NOT EXISTS Deadlines (
    deadline_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    due_date INTEGER NOT NULL,
    type TEXT NOT NULL DEFAULT 'statutory' CHECK(type IN ('statutory', 'client', 'internal')), -- add later on a rule table for statuatory deadlines
    status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending', 'Done', 'Overdue')),
    completed INTEGER DEFAULT 0 CHECK(completed IN (0,1)),
    created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL, completed_at INTEGER,
    CHECK(
        (status != 'Done' AND completed=0 AND completed_at IS NULL) OR
        (status = 'Done' AND completed=1 AND completed_at IS NOT NULL)
    ),
    FOREIGN KEY (case_id) REFERENCES Cases(case_id) ON DELETE RESTRICT
);