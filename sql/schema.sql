CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    request_id UUID NOT NULL,
    model_version TEXT NOT NULL,
    latency_ms FLOAT NOT NULL,
    input_data JSONB NOT NULL,
    prediction TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);