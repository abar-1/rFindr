-- rFindr Supabase schema (idempotent)

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    email VARCHAR UNIQUE,
    research_interests VARCHAR,
    major VARCHAR,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE INDEX IF NOT EXISTS ix_users_name ON users (name);
CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);
CREATE INDEX IF NOT EXISTS ix_users_research_interests ON users (research_interests);
CREATE INDEX IF NOT EXISTS ix_users_major ON users (major);

CREATE TABLE IF NOT EXISTS professors (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    department VARCHAR,
    research_areas TEXT,
    email VARCHAR UNIQUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE INDEX IF NOT EXISTS ix_professors_name ON professors (name);
CREATE INDEX IF NOT EXISTS ix_professors_department ON professors (department);
CREATE INDEX IF NOT EXISTS ix_professors_research_areas ON professors (research_areas);
CREATE INDEX IF NOT EXISTS ix_professors_email ON professors (email);

CREATE TABLE IF NOT EXISTS user_embeddings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    embedding vector(384) NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_user_embeddings_user_id ON user_embeddings (user_id);

CREATE TABLE IF NOT EXISTS professor_embeddings (
    id SERIAL PRIMARY KEY,
    professor_id INTEGER NOT NULL REFERENCES professors (id) ON DELETE CASCADE,
    embedding vector(384) NOT NULL,
    chunk TEXT
);

CREATE INDEX IF NOT EXISTS ix_professor_embeddings_professor_id ON professor_embeddings (professor_id);

CREATE TABLE IF NOT EXISTS chat_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    query VARCHAR NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    matched_professors INTEGER[]
);

CREATE INDEX IF NOT EXISTS ix_chat_logs_user_id ON chat_logs (user_id);

-- Upgrade legacy tables created without pgvector / chunk column
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'professor_embeddings'
          AND column_name = 'embedding'
          AND udt_name <> 'vector'
    ) THEN
        ALTER TABLE professor_embeddings
            ALTER COLUMN embedding TYPE vector(384)
            USING embedding::vector(384);
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'professor_embeddings'
          AND column_name = 'chunk'
    ) THEN
        ALTER TABLE professor_embeddings ADD COLUMN chunk TEXT;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'user_embeddings'
          AND column_name = 'embedding'
          AND udt_name <> 'vector'
    ) THEN
        ALTER TABLE user_embeddings
            ALTER COLUMN embedding TYPE vector(384)
            USING embedding::vector(384);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS professor_embeddings_embedding_hnsw_idx
    ON professor_embeddings USING hnsw (embedding vector_cosine_ops);

GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE professors ENABLE ROW LEVEL SECURITY;
ALTER TABLE professor_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_logs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS users_all ON users;
CREATE POLICY users_all ON users FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS user_embeddings_all ON user_embeddings;
CREATE POLICY user_embeddings_all ON user_embeddings FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS professors_all ON professors;
CREATE POLICY professors_all ON professors FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS professor_embeddings_all ON professor_embeddings;
CREATE POLICY professor_embeddings_all ON professor_embeddings FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS chat_logs_all ON chat_logs;
CREATE POLICY chat_logs_all ON chat_logs FOR ALL USING (true) WITH CHECK (true);

CREATE OR REPLACE FUNCTION top_professor_matches(user_embedding vector(384))
RETURNS TABLE (
    name text,
    email text,
    similarity double precision
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        p.name,
        p.email,
        (1 - (pe.embedding <=> user_embedding))::double precision AS similarity
    FROM professor_embeddings pe
    JOIN professors p ON p.id = pe.professor_id
    ORDER BY pe.embedding <=> user_embedding
    LIMIT 30;
$$;

CREATE OR REPLACE FUNCTION debug_count_embeddings()
RETURNS bigint
LANGUAGE sql
STABLE
AS $$
    SELECT count(*)::bigint FROM professor_embeddings;
$$;

CREATE OR REPLACE FUNCTION debug_whoami()
RETURNS text
LANGUAGE sql
STABLE
AS $$
    SELECT current_user::text;
$$;

GRANT EXECUTE ON FUNCTION top_professor_matches(vector) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION debug_count_embeddings() TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION debug_whoami() TO anon, authenticated, service_role;
