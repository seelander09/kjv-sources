-- Enhanced Database Schema for KJV Sources with Mathematical Analysis
-- This extends your existing schema with word-level analysis capabilities

-- Books table (extended)
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    osis_name TEXT UNIQUE NOT NULL,
    testament TEXT NOT NULL CHECK (testament IN ('OT', 'NT')),
    number INT NOT NULL,
    word_count INT DEFAULT 0,
    is_sevened BOOLEAN DEFAULT FALSE,
    mathematical_properties JSONB
);

-- Chapters table (extended)
CREATE TABLE IF NOT EXISTS chapters (
    id SERIAL PRIMARY KEY,
    book_id INT NOT NULL REFERENCES books(id),
    chapter INT NOT NULL,
    word_count INT DEFAULT 0,
    is_sevened BOOLEAN DEFAULT FALSE,
    mathematical_properties JSONB,
    UNIQUE (book_id, chapter)
);

-- Verses table (extended from your existing structure)
CREATE TABLE IF NOT EXISTS verses (
    id SERIAL PRIMARY KEY,
    chapter_id INT NOT NULL REFERENCES chapters(id),
    verse INT NOT NULL,
    osis_ref TEXT UNIQUE NOT NULL,
    canonical_reference TEXT NOT NULL,
    text_full TEXT NOT NULL,
    word_count INT,
    sources TEXT[],
    source_count INT,
    primary_source TEXT,
    source_sequence TEXT,
    source_percentages JSONB,
    redaction_indicators TEXT[],
    text_J TEXT, text_E TEXT, text_P TEXT, text_R TEXT,
    metadata JSONB,
    mathematical_properties JSONB,
    UNIQUE (chapter_id, verse)
);

-- Words table (new - for word-level analysis)
CREATE TABLE IF NOT EXISTS words (
    id SERIAL PRIMARY KEY,
    verse_id INT REFERENCES verses(id),
    word TEXT NOT NULL,
    position_global INT NOT NULL,
    position_in_verse INT NOT NULL,
    position_in_chapter INT NOT NULL,
    position_in_book INT NOT NULL,
    word_length INT NOT NULL,
    is_capitalized BOOLEAN NOT NULL,
    is_number BOOLEAN NOT NULL,
    is_proper_name BOOLEAN NOT NULL,
    source_attribution TEXT[],
    mathematical_properties JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Word patterns table (new - for mathematical pattern analysis)
CREATE TABLE IF NOT EXISTS word_patterns (
    id SERIAL PRIMARY KEY,
    word TEXT NOT NULL,
    total_count INT NOT NULL,
    first_occurrence INT NOT NULL,
    last_occurrence INT NOT NULL,
    is_sevened BOOLEAN NOT NULL,
    is_777 BOOLEAN NOT NULL,
    is_70x7 BOOLEAN NOT NULL,
    is_77 BOOLEAN NOT NULL,
    is_343 BOOLEAN NOT NULL,
    is_490 BOOLEAN NOT NULL,
    is_980 BOOLEAN NOT NULL,
    position_patterns JSONB,
    pattern_analysis JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Verse chunks table (for RAG/vector search)
CREATE TABLE IF NOT EXISTS verse_chunks (
    id SERIAL PRIMARY KEY,
    start_osis TEXT NOT NULL,
    end_osis TEXT NOT NULL,
    text TEXT NOT NULL,
    span_tokens INT,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Global analysis table (new - for storing overall mathematical analysis)
CREATE TABLE IF NOT EXISTS global_analysis (
    id SERIAL PRIMARY KEY,
    total_words INT NOT NULL,
    is_7_power BOOLEAN NOT NULL,
    is_823543 BOOLEAN NOT NULL,
    word_count_analysis JSONB,
    book_analysis JSONB,
    chapter_analysis JSONB,
    verse_analysis JSONB,
    analysis_date TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_words_position_global ON words(position_global);
CREATE INDEX IF NOT EXISTS idx_words_word ON words(word);
CREATE INDEX IF NOT EXISTS idx_words_verse_id ON words(verse_id);
CREATE INDEX IF NOT EXISTS idx_word_patterns_word ON word_patterns(word);
CREATE INDEX IF NOT EXISTS idx_word_patterns_count ON word_patterns(total_count);
CREATE INDEX IF NOT EXISTS idx_verses_osis_ref ON verses(osis_ref);
CREATE INDEX IF NOT EXISTS idx_verses_sources ON verses USING GIN(sources);
CREATE INDEX IF NOT EXISTS idx_verse_chunks_embedding ON verse_chunks USING ivfflat (embedding vector_cosine_ops);

-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;
