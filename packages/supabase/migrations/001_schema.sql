-- Drov Elektrik - Database Schema
-- All tables with RLS enabled

-- ==================== CATALOG TABLES ====================

-- Box series (6 series with validation rules)
CREATE TABLE box_series (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  edge_margin INTEGER NOT NULL DEFAULT 15,
  hole_clearance INTEGER NOT NULL DEFAULT 5,
  default_hole_diameter INTEGER NOT NULL DEFAULT 20,
  max_hole_diameter INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE box_series ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated users can read box_series"
  ON box_series FOR SELECT
  TO authenticated
  USING (true);

-- Box models (~34 models)
CREATE TABLE box_models (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  series_id TEXT NOT NULL REFERENCES box_series(id),
  internal_length INTEGER NOT NULL,
  internal_width INTEGER NOT NULL,
  internal_depth INTEGER NOT NULL,
  mounting_plate_x INTEGER NOT NULL,
  mounting_plate_y INTEGER NOT NULL,
  max_holes_long INTEGER NOT NULL,
  max_holes_short INTEGER NOT NULL,
  rail_count INTEGER NOT NULL DEFAULT 1,
  max_terminals INTEGER NOT NULL,
  ip_rating TEXT,
  has_earth_plate BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE box_models ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated users can read box_models"
  ON box_models FOR SELECT
  TO authenticated
  USING (true);

-- Hole sizes (M20, M25, M32, M40, M50)
CREATE TABLE hole_sizes (
  id TEXT PRIMARY KEY,
  diameter INTEGER NOT NULL,
  clearance INTEGER NOT NULL,
  name TEXT NOT NULL,
  code TEXT NOT NULL
);

ALTER TABLE hole_sizes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated users can read hole_sizes"
  ON hole_sizes FOR SELECT
  TO authenticated
  USING (true);

-- Switchgear catalog
CREATE TABLE switchgear_catalog (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  brand TEXT NOT NULL DEFAULT 'Generic',
  din_modules INTEGER NOT NULL DEFAULT 0,
  width NUMERIC NOT NULL,
  height NUMERIC NOT NULL,
  depth NUMERIC NOT NULL,
  current_rating INTEGER[],
  coil_voltage INTEGER[],
  contact_count INTEGER,
  pole_count INTEGER NOT NULL DEFAULT 1,
  mounting TEXT NOT NULL DEFAULT 'din_rail',
  cross_section NUMERIC,
  output_voltage NUMERIC,
  output_current NUMERIC,
  positions INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE switchgear_catalog ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated users can read switchgear_catalog"
  ON switchgear_catalog FOR SELECT
  TO authenticated
  USING (true);

-- Cover element catalog
CREATE TABLE cover_element_catalog (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  cutout_diameter INTEGER,
  bezel_diameter INTEGER,
  cutout_width INTEGER,
  cutout_height INTEGER,
  bezel_width INTEGER,
  bezel_height INTEGER,
  depth_behind_panel INTEGER NOT NULL,
  color TEXT NOT NULL,
  function TEXT,
  voltage INTEGER[],
  positions INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE cover_element_catalog ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated users can read cover_element_catalog"
  ON cover_element_catalog FOR SELECT
  TO authenticated
  USING (true);

-- Salt malzeme (standard included components)
CREATE TABLE salt_malzeme (
  id SERIAL PRIMARY KEY,
  part_name TEXT NOT NULL,
  part_code TEXT NOT NULL,
  quantity INTEGER NOT NULL DEFAULT 1,
  description TEXT NOT NULL
);

ALTER TABLE salt_malzeme ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated users can read salt_malzeme"
  ON salt_malzeme FOR SELECT
  TO authenticated
  USING (true);

-- ==================== USER TABLES ====================

-- User profiles (linked to auth.users)
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name TEXT,
  company TEXT,
  role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin', 'engineer')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public profiles are viewable by authenticated users"
  ON profiles FOR SELECT
  TO authenticated
  USING (true);
CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  TO authenticated
  USING (auth.uid() = id);

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO profiles (id, full_name, company)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    COALESCE(NEW.raw_user_meta_data->>'company', '')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_new_user();

-- Configurations (saved user configurations)
CREATE TABLE configurations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  box_model_id TEXT NOT NULL REFERENCES box_models(id),
  name TEXT,
  terminals INTEGER NOT NULL DEFAULT 0,
  holes_top JSONB NOT NULL DEFAULT '{"count": 0, "size": "M20"}'::jsonb,
  holes_bottom JSONB NOT NULL DEFAULT '{"count": 0, "size": "M20"}'::jsonb,
  holes_left JSONB NOT NULL DEFAULT '{"count": 0, "size": "M20"}'::jsonb,
  holes_right JSONB NOT NULL DEFAULT '{"count": 0, "size": "M20"}'::jsonb,
  switchgear JSONB NOT NULL DEFAULT '[]'::jsonb,
  cover_elements JSONB NOT NULL DEFAULT '[]'::jsonb,
  notes TEXT,
  drawing_number TEXT UNIQUE,
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'production')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE configurations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can read own configurations"
  ON configurations FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);
CREATE POLICY "Admins can read all configurations"
  ON configurations FOR SELECT
  TO authenticated
  USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin'));
CREATE POLICY "Users can insert own configurations"
  ON configurations FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own configurations"
  ON configurations FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own draft configurations"
  ON configurations FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id AND status = 'draft');

-- Auto-generate drawing number
CREATE OR REPLACE FUNCTION generate_drawing_number()
RETURNS TRIGGER AS $$
DECLARE
  next_num INTEGER;
BEGIN
  SELECT COALESCE(MAX(CAST(SUBSTRING(drawing_number FROM 'DRV-(\d+)') AS INTEGER)), 0) + 1
  INTO next_num
  FROM configurations
  WHERE drawing_number IS NOT NULL;

  NEW.drawing_number := 'DRV-' || LPAD(next_num::TEXT, 5, '0');
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_drawing_number
  BEFORE INSERT ON configurations
  FOR EACH ROW
  WHEN (NEW.drawing_number IS NULL)
  EXECUTE FUNCTION generate_drawing_number();

CREATE TRIGGER update_configuration_timestamp
  BEFORE UPDATE ON configurations
  FOR EACH ROW
  EXECUTE FUNCTION generate_drawing_number();

-- Generated files (references to Supabase Storage)
CREATE TABLE generated_files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  configuration_id UUID NOT NULL REFERENCES configurations(id) ON DELETE CASCADE,
  file_type TEXT NOT NULL CHECK (file_type IN ('pdf', 'dxf', 'step', 'label')),
  storage_path TEXT NOT NULL,
  file_name TEXT NOT NULL,
  file_size INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE generated_files ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can read own generated files"
  ON generated_files FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM configurations c
      WHERE c.id = configuration_id AND c.user_id = auth.uid()
    )
  );
CREATE POLICY "Users can insert own generated files"
  ON generated_files FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM configurations c
      WHERE c.id = configuration_id AND c.user_id = auth.uid()
    )
  );

-- ==================== INDEXES ====================

CREATE INDEX idx_box_models_series ON box_models(series_id);
CREATE INDEX idx_configurations_user ON configurations(user_id);
CREATE INDEX idx_configurations_status ON configurations(status);
CREATE INDEX idx_configurations_drawing_number ON configurations(drawing_number);
CREATE INDEX idx_generated_files_config ON generated_files(configuration_id);
CREATE INDEX idx_switchgear_category ON switchgear_catalog(category);
CREATE INDEX idx_cover_elements_category ON cover_element_catalog(category);
