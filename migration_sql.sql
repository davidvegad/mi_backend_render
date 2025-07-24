-- Migración manual para nuevos modelos de analytics
-- Ejecutar después de activar el entorno virtual con: python manage.py dbshell

-- Crear tabla ProfileView
CREATE TABLE links_profileview (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES links_profile(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT DEFAULT '',
    referrer VARCHAR(200),
    device_type VARCHAR(20) DEFAULT '',
    country VARCHAR(100) DEFAULT '',
    country_code VARCHAR(2) DEFAULT ''
);

-- Crear índices para ProfileView
CREATE INDEX links_profileview_profile_timestamp_idx ON links_profileview(profile_id, timestamp DESC);
CREATE INDEX links_profileview_timestamp_idx ON links_profileview(timestamp);

-- Crear tabla LinkClick
CREATE TABLE links_linkclick (
    id SERIAL PRIMARY KEY,
    link_id INTEGER NOT NULL REFERENCES links_link(id) ON DELETE CASCADE,
    profile_id INTEGER NOT NULL REFERENCES links_profile(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT DEFAULT '',
    referrer VARCHAR(200),
    device_type VARCHAR(20) DEFAULT '',
    country VARCHAR(100) DEFAULT '',
    country_code VARCHAR(2) DEFAULT ''
);

-- Crear índices para LinkClick
CREATE INDEX links_linkclick_link_timestamp_idx ON links_linkclick(link_id, timestamp DESC);
CREATE INDEX links_linkclick_profile_timestamp_idx ON links_linkclick(profile_id, timestamp DESC);
CREATE INDEX links_linkclick_timestamp_idx ON links_linkclick(timestamp);

-- Crear tabla AnalyticsCache
CREATE TABLE links_analyticscache (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES links_profile(id) ON DELETE CASCADE,
    cache_key VARCHAR(100) NOT NULL,
    time_range VARCHAR(10) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE(profile_id, cache_key, time_range)
);

-- Crear índices para AnalyticsCache
CREATE INDEX links_analyticscache_profile_cache_time_idx ON links_analyticscache(profile_id, cache_key, time_range);
CREATE INDEX links_analyticscache_expires_at_idx ON links_analyticscache(expires_at);

-- Insertar datos de prueba (opcional)
-- INSERT INTO links_profileview (profile_id, device_type, country, country_code) 
-- SELECT id, 'mobile', 'España', 'ES' FROM links_profile LIMIT 5;