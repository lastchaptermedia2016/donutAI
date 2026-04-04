-- AI Settings Table
-- Stores user preferences for AI personality, voice, and model parameters

CREATE TABLE IF NOT EXISTS ai_settings (
    user_id TEXT PRIMARY KEY,
    personality_tone TEXT NOT NULL DEFAULT 'warm',
    response_length TEXT NOT NULL DEFAULT 'balanced',
    formality_level INTEGER NOT NULL DEFAULT 5 CHECK (formality_level >= 1 AND formality_level <= 10),
    emotion TEXT NOT NULL DEFAULT 'neutral',
    tts_voice TEXT NOT NULL DEFAULT 'autumn',
    tts_speed REAL NOT NULL DEFAULT 1.0 CHECK (tts_speed >= 0.5 AND tts_speed <= 2.0),
    tts_provider TEXT NOT NULL DEFAULT 'groq',
    llm_temperature REAL NOT NULL DEFAULT 0.7 CHECK (llm_temperature >= 0.1 AND llm_temperature <= 1.0),
    llm_max_tokens INTEGER NOT NULL DEFAULT 1024 CHECK (llm_max_tokens >= 256 AND llm_max_tokens <= 4096),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE ai_settings ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own settings
CREATE POLICY "Users can view own AI settings" ON ai_settings
    FOR SELECT
    USING (true);  -- Allow public read for now (single user mode)

CREATE POLICY "Users can update own AI settings" ON ai_settings
    FOR UPDATE
    USING (true);  -- Allow public write for now (single user mode)

CREATE POLICY "Users can insert own AI settings" ON ai_settings
    FOR INSERT
    WITH CHECK (true);  -- Allow public insert for now (single user mode)

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_ai_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
CREATE TRIGGER ai_settings_updated_at_trigger
    BEFORE UPDATE ON ai_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_ai_settings_updated_at();

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_ai_settings_user_id ON ai_settings(user_id);