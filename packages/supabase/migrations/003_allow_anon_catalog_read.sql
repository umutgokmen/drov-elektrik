-- Allow anonymous users to read catalog tables (public engineering data)
-- This enables the app to work without login for browsing

CREATE POLICY "Anyone can read box_series"
  ON box_series FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Anyone can read box_models"
  ON box_models FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Anyone can read hole_sizes"
  ON hole_sizes FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Anyone can read switchgear_catalog"
  ON switchgear_catalog FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Anyone can read cover_element_catalog"
  ON cover_element_catalog FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Anyone can read salt_malzeme"
  ON salt_malzeme FOR SELECT
  TO anon
  USING (true);
