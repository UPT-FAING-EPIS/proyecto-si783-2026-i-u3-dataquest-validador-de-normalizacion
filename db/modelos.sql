-- ============================================================
-- VALIDADOR DE NORMALIZACIÓN DE BASES DE DATOS RELACIONALES
-- Script de base de datos para Supabase (PostgreSQL 16)
-- ============================================================
-- Instrucciones:
--   1. Abre tu proyecto en https://supabase.com
--   2. Ve a SQL Editor → New Query
--   3. Pega este script completo y ejecuta
-- ============================================================


-- ============================================================
-- 1. TABLA DE PERFILES
--    Extiende auth.users con datos públicos del usuario.
--    Se crea automáticamente al registrarse.
-- ============================================================

CREATE TABLE IF NOT EXISTS public.perfiles (
    id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    nombre      TEXT,
    avatar_url  TEXT,
    creado_en   TIMESTAMPTZ DEFAULT now()
);

-- Trigger: crea el perfil automáticamente al registrar un usuario
CREATE OR REPLACE FUNCTION public.crear_perfil_nuevo_usuario()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.perfiles (id, nombre)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'nombre', split_part(NEW.email, '@', 1))
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.crear_perfil_nuevo_usuario();


-- ============================================================
-- 2. TABLA DE PRESENCIA (COMUNIDAD EN TIEMPO REAL)
--    Registra qué usuarios están conectados actualmente.
--    Se actualiza con Supabase Realtime (canal de presencia).
-- ============================================================

CREATE TABLE IF NOT EXISTS public.presencia (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    nombre          TEXT,
    conectado_en    TIMESTAMPTZ DEFAULT now(),
    ultima_actividad TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 3. TABLA DE HISTORIAL DE VALIDACIONES
--    Guarda cada análisis realizado por el usuario.
-- ============================================================

CREATE TABLE IF NOT EXISTS public.historial_validaciones (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    fecha            TIMESTAMPTZ DEFAULT now(),

    -- Información del esquema analizado
    nombre_esquema   TEXT NOT NULL,
    formato_entrada  TEXT CHECK (formato_entrada IN ('sql', 'csv', 'xls', 'txt', 'texto_pegado')),

    -- Resultado del análisis
    nivel_inicial    TEXT CHECK (nivel_inicial    IN ('sin_normalizar', '1fn', '2fn', '3fn')),
    nivel_objetivo   TEXT CHECK (nivel_objetivo   IN ('1fn', '2fn', '3fn')),
    nivel_final      TEXT CHECK (nivel_final      IN ('sin_normalizar', '1fn', '2fn', '3fn')),

    -- Detalle del análisis (almacenado como JSON)
    esquema_original JSONB,   -- estructura interna antes de normalizar
    esquema_final    JSONB,   -- estructura interna tras aplicar sugerencias
    dependencias     JSONB,   -- dependencias funcionales detectadas
    violaciones      JSONB,   -- violaciones encontradas por nivel
    sugerencias      JSONB    -- sugerencias presentadas + cuáles fueron aplicadas
);

-- Índice para consultas rápidas por usuario ordenadas por fecha
CREATE INDEX IF NOT EXISTS idx_historial_user_fecha
    ON public.historial_validaciones (user_id, fecha DESC);


-- ============================================================
-- 4. ROW LEVEL SECURITY (RLS)
--    Cada usuario solo puede ver y modificar sus propios datos.
-- ============================================================

-- Perfiles
ALTER TABLE public.perfiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuario ve su propio perfil"
    ON public.perfiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Usuario actualiza su propio perfil"
    ON public.perfiles FOR UPDATE
    USING (auth.uid() = id);

-- Presencia (todos pueden ver quién está conectado)
ALTER TABLE public.presencia ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Todos pueden ver la presencia"
    ON public.presencia FOR SELECT
    USING (true);

CREATE POLICY "Usuario gestiona su propia presencia"
    ON public.presencia FOR ALL
    USING (auth.uid() = user_id);

-- Historial
ALTER TABLE public.historial_validaciones ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuario ve su propio historial"
    ON public.historial_validaciones FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Usuario inserta en su historial"
    ON public.historial_validaciones FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuario elimina su propio historial"
    ON public.historial_validaciones FOR DELETE
    USING (auth.uid() = user_id);


-- ============================================================
-- 5. REALTIME
--    Habilitar Realtime en la tabla de presencia para
--    detectar usuarios conectados en tiempo real.
-- ============================================================

ALTER PUBLICATION supabase_realtime ADD TABLE public.presencia;


-- ============================================================
-- 6. PERMISOS PARA EL ROL ANON Y AUTHENTICATED
-- ============================================================

-- Perfiles
GRANT SELECT, UPDATE ON public.perfiles TO authenticated;

-- Presencia
GRANT SELECT ON public.presencia TO anon, authenticated;
GRANT INSERT, UPDATE, DELETE ON public.presencia TO authenticated;

-- Historial
GRANT SELECT, INSERT, DELETE ON public.historial_validaciones TO authenticated;
