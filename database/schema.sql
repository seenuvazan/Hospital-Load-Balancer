CREATE TABLE servers (
    server_id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    server_type VARCHAR(40) NOT NULL,
    load INTEGER NOT NULL,
    max_capacity INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    avg_response_ms INTEGER NOT NULL
);

CREATE TABLE requests (
    request_id VARCHAR(32) PRIMARY KEY,
    type VARCHAR(20) NOT NULL,
    priority INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    source_name VARCHAR(120) NOT NULL,
    target_module VARCHAR(80) NOT NULL
);

CREATE TABLE patients (
    patient_id VARCHAR(32) PRIMARY KEY,
    patient_name VARCHAR(120) NOT NULL,
    condition_level VARCHAR(30) NOT NULL,
    assigned_module VARCHAR(30) NOT NULL
);

CREATE TABLE logs (
    log_id SERIAL PRIMARY KEY,
    request_id VARCHAR(32) NOT NULL REFERENCES requests(request_id),
    server_id VARCHAR(32) NOT NULL REFERENCES servers(server_id),
    decision TEXT NOT NULL,
    priority INTEGER NOT NULL,
    request_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
