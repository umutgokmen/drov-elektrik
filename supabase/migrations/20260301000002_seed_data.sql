-- Drov Elektrik - Seed Data
-- Catalog data for all series, box models, hole sizes, switchgear, cover elements

-- ==================== BOX SERIES ====================
INSERT INTO box_series (id, name, description, edge_margin, hole_clearance, default_hole_diameter, max_hole_diameter) VALUES
  ('ejb',  'EJB',  'Ex-proof Junction Box',            15, 5,  20, NULL),
  ('esp',  'ESP',  'Ex-proof Small Panel',              12, 4,  20, NULL),
  ('esa',  'ESA',  'Ex-proof Standard Assembly',        15, 5,  20, NULL),
  ('esx',  'ESX',  'Ex-proof Stainless Steel',          20, 8,  20, NULL),
  ('ejbx', 'EJBX', 'Ex-proof Junction Box Extended',    25, 25, 20, NULL),
  ('ejc',  'EJC',  'Ex-proof Junction Compact (IP66)',  20, 8,  20, 25);

-- ==================== BOX MODELS ====================

-- EJB Series
INSERT INTO box_models (id, name, series_id, internal_length, internal_width, internal_depth, mounting_plate_x, mounting_plate_y, max_holes_long, max_holes_short, rail_count, max_terminals) VALUES
  ('ejb21', 'EJB 21', 'ejb', 169, 179, 160, 180, 140, 10, 8,  1, 30),
  ('ejb31', 'EJB 31', 'ejb', 249, 258, 294, 325, 225, 28, 20, 2, 52),
  ('ejb51', 'EJB 51', 'ejb', 390, 388, 370, 460, 260, 44, 24, 2, 80),
  ('ejb61', 'EJB 61', 'ejb', 500, 470, 360, 560, 360, 72, 48, 3, 92),
  ('ejb63', 'EJB 63', 'ejb', 500, 470, 360, 560, 360, 36, 24, 3, 92),
  ('ejb71', 'EJB 71', 'ejb', 600, 530, 410, 650, 410, 90, 59, 3, 110),
  ('ejb73', 'EJB 73', 'ejb', 600, 530, 410, 650, 410, 40, 16, 3, 110),
  ('ejb91', 'EJB 91', 'ejb', 700, 650, 510, 750, 440, 112, 70, 3, 140),
  ('ejb93', 'EJB 93', 'ejb', 700, 650, 510, 750, 440, 48, 30, 3, 140);

-- ESP Series
INSERT INTO box_models (id, name, series_id, internal_length, internal_width, internal_depth, mounting_plate_x, mounting_plate_y, max_holes_long, max_holes_short, rail_count, max_terminals) VALUES
  ('esp1', 'ESP 1', 'esp', 120, 80,  60,  100, 60,  3,  2,  1, 7),
  ('esp2', 'ESP 2', 'esp', 150, 100, 80,  130, 80,  4,  3,  1, 11),
  ('esp3', 'ESP 3', 'esp', 200, 150, 100, 180, 110, 7,  5,  1, 21),
  ('esp4', 'ESP 4', 'esp', 300, 200, 120, 280, 160, 11, 7,  2, 40),
  ('esp5', 'ESP 5', 'esp', 400, 300, 150, 380, 240, 15, 11, 2, 60);

-- ESA Series
INSERT INTO box_models (id, name, series_id, internal_length, internal_width, internal_depth, mounting_plate_x, mounting_plate_y, max_holes_long, max_holes_short, rail_count, max_terminals) VALUES
  ('esa1', 'ESA 1', 'esa', 300, 300, 180, 340, 220, 14, 14, 2, 50),
  ('esa2', 'ESA 2', 'esa', 400, 350, 200, 440, 260, 22, 18, 2, 70),
  ('esa3', 'ESA 3', 'esa', 250, 200, 150, 270, 220, 18, 12, 1, 28),
  ('esa4', 'ESA 4', 'esa', 350, 300, 200, 370, 320, 24, 20, 2, 52),
  ('esa5', 'ESA 5', 'esa', 450, 400, 250, 470, 420, 32, 28, 2, 76),
  ('esa6', 'ESA 6', 'esa', 550, 450, 300, 570, 470, 42, 32, 3, 96);

-- ESX Series (Stainless Steel)
INSERT INTO box_models (id, name, series_id, internal_length, internal_width, internal_depth, mounting_plate_x, mounting_plate_y, max_holes_long, max_holes_short, rail_count, max_terminals) VALUES
  ('esx1',  'ESX 1',  'esx', 400, 400, 220, 440, 280, 22, 22, 2, 60),
  ('esx2',  'ESX 2',  'esx', 500, 450, 250, 550, 320, 30, 26, 3, 90),
  ('esx15', 'ESX 15', 'esx', 150, 150, 80,  130, 130, 4,  4,  1, 16),
  ('esx20', 'ESX 20', 'esx', 200, 200, 100, 180, 180, 6,  6,  1, 24),
  ('esx30', 'ESX 30', 'esx', 300, 250, 150, 280, 230, 8,  6,  2, 40),
  ('esx40', 'ESX 40', 'esx', 400, 300, 200, 380, 280, 10, 8,  2, 56);

-- EJBX Series
INSERT INTO box_models (id, name, series_id, internal_length, internal_width, internal_depth, mounting_plate_x, mounting_plate_y, max_holes_long, max_holes_short, rail_count, max_terminals) VALUES
  ('ejbx1', 'EJBX 1', 'ejbx', 200, 160, 120, 240, 180, 8,  6,  1, 20),
  ('ejbx2', 'EJBX 2', 'ejbx', 300, 230, 150, 340, 260, 16, 10, 2, 40),
  ('ejbx3', 'EJBX 3', 'ejbx', 400, 310, 200, 450, 340, 24, 14, 2, 60),
  ('ejbx4', 'EJBX 4', 'ejbx', 500, 400, 250, 560, 440, 32, 18, 3, 80);

-- EJC Series (IP66)
INSERT INTO box_models (id, name, series_id, internal_length, internal_width, internal_depth, mounting_plate_x, mounting_plate_y, max_holes_long, max_holes_short, rail_count, max_terminals, ip_rating, has_earth_plate) VALUES
  ('ejc01', 'EJC 01', 'ejc', 150, 150, 80,  160, 160, 4,  4, 1, 16, 'IP66', TRUE),
  ('ejc02', 'EJC 02', 'ejc', 200, 150, 80,  210, 160, 6,  4, 1, 24, 'IP66', TRUE),
  ('ejc03', 'EJC 03', 'ejc', 200, 200, 100, 210, 210, 6,  6, 1, 30, 'IP66', TRUE),
  ('ejc04', 'EJC 04', 'ejc', 300, 200, 120, 310, 210, 10, 6, 2, 50, 'IP66', TRUE);

-- ==================== HOLE SIZES ====================
INSERT INTO hole_sizes (id, diameter, clearance, name, code) VALUES
  ('M20', 20, 5,  'M20 Kablo Rakoru', 'M20-GL'),
  ('M25', 25, 6,  'M25 Kablo Rakoru', 'M25-GL'),
  ('M32', 32, 8,  'M32 Kablo Rakoru', 'M32-GL'),
  ('M40', 40, 10, 'M40 Kablo Rakoru', 'M40-GL'),
  ('M50', 50, 12, 'M50 Kablo Rakoru', 'M50-GL');

-- ==================== SWITCHGEAR CATALOG ====================
INSERT INTO switchgear_catalog (id, name, category, brand, din_modules, width, height, depth, current_rating, pole_count) VALUES
  ('fuse-nh00', 'NH00 Sigorta Yuvası', 'fuse', 'Generic', 3, 52.5, 70, 62, ARRAY[16,20,25,32,40,50,63,80,100,125,160], 3),
  ('fuse-nh1',  'NH1 Sigorta Yuvası',  'fuse', 'Generic', 3, 52.5, 70, 70, ARRAY[63,80,100,125,160,200,250], 3);

INSERT INTO switchgear_catalog (id, name, category, brand, din_modules, width, height, depth, current_rating, pole_count) VALUES
  ('mcb-1p', 'Otomatik Sigorta 1P', 'mcb', 'Generic', 1, 17.5, 80, 68, ARRAY[6,10,16,20,25,32,40,50,63], 1),
  ('mcb-2p', 'Otomatik Sigorta 2P', 'mcb', 'Generic', 2, 35.0, 80, 68, ARRAY[6,10,16,20,25,32,40,50,63], 2),
  ('mcb-3p', 'Otomatik Sigorta 3P', 'mcb', 'Generic', 3, 52.5, 80, 68, ARRAY[6,10,16,20,25,32,40,50,63], 3),
  ('mcb-4p', 'Otomatik Sigorta 4P', 'mcb', 'Generic', 4, 70.0, 80, 68, ARRAY[6,10,16,20,25,32,40,50,63], 4);

INSERT INTO switchgear_catalog (id, name, category, brand, din_modules, width, height, depth, coil_voltage, contact_count, pole_count) VALUES
  ('relay-4co', 'Ara Röle 4CO', 'relay', 'Generic', 1, 17.5, 80, 62, ARRAY[24,48,110,230], 4, 1),
  ('relay-2co', 'Ara Röle 2CO', 'relay', 'Generic', 1, 15.5, 80, 62, ARRAY[24,48,110,230], 2, 1);

INSERT INTO switchgear_catalog (id, name, category, brand, din_modules, width, height, depth, current_rating, coil_voltage, pole_count) VALUES
  ('contactor-9a',  'Kontaktör 9A',  'contactor', 'Generic', 3, 45, 82, 77, ARRAY[9],  ARRAY[24,48,110,230], 3),
  ('contactor-18a', 'Kontaktör 18A', 'contactor', 'Generic', 3, 45, 82, 77, ARRAY[18], ARRAY[24,48,110,230], 3),
  ('contactor-32a', 'Kontaktör 32A', 'contactor', 'Generic', 3, 55, 95, 85, ARRAY[32], ARRAY[24,48,110,230], 3);

INSERT INTO switchgear_catalog (id, name, category, brand, din_modules, width, height, depth, current_rating, pole_count) VALUES
  ('switch-isolator-3p', 'Yük Ayırıcı 3P', 'switch', 'Generic', 3, 52.5, 80, 68, ARRAY[25,32,40,63,80,100], 3);

INSERT INTO switchgear_catalog (id, name, category, brand, din_modules, width, height, depth, cross_section, pole_count) VALUES
  ('terminal-2.5', 'UT 2,5 Klemens', 'terminal', 'Phoenix Contact', 0, 5.2, 47.7, 47.5, 2.5, 1),
  ('terminal-4',   'UT 4 Klemens',   'terminal', 'Phoenix Contact', 0, 6.2, 47.7, 47.5, 4,   1),
  ('terminal-6',   'UT 6 Klemens',   'terminal', 'Phoenix Contact', 0, 8.2, 52.3, 51.9, 6,   1);

INSERT INTO switchgear_catalog (id, name, category, brand, din_modules, width, height, depth, pole_count) VALUES
  ('surge-type2', 'Tip 2 Parafudr', 'surge_protector', 'Generic', 4, 70, 90, 65, 3);

INSERT INTO switchgear_catalog (id, name, category, brand, din_modules, width, height, depth, coil_voltage, pole_count) VALUES
  ('timer-digital', 'Dijital Zaman Rölesi', 'timer', 'Generic', 1, 17.5, 90, 62, ARRAY[24,230], 1);

INSERT INTO switchgear_catalog (id, name, category, brand, din_modules, width, height, depth, output_voltage, output_current, pole_count) VALUES
  ('psu-24v-2.5a', '24V 2.5A Güç Kaynağı', 'power_supply', 'Generic', 2, 35, 90, 55, 24, 2.5, 1);

-- ==================== COVER ELEMENTS CATALOG ====================
INSERT INTO cover_element_catalog (id, name, category, cutout_diameter, bezel_diameter, depth_behind_panel, color, function) VALUES
  ('btn-22-green',  'Yeşil Buton 22mm',    'pushbutton', 22, 30, 40, 'green',  'start'),
  ('btn-22-red',    'Kırmızı Buton 22mm',  'pushbutton', 22, 30, 40, 'red',    'stop'),
  ('btn-22-yellow', 'Sarı Buton 22mm',     'pushbutton', 22, 30, 40, 'yellow', 'general'),
  ('btn-22-blue',   'Mavi Buton 22mm',     'pushbutton', 22, 30, 40, 'blue',   'reset'),
  ('btn-22-white',  'Beyaz Buton 22mm',    'pushbutton', 22, 30, 40, 'white',  'general');

INSERT INTO cover_element_catalog (id, name, category, cutout_diameter, bezel_diameter, depth_behind_panel, color, positions) VALUES
  ('sel-22-2pos', '2 Konumlu Anahtar 22mm', 'selector_switch', 22, 30, 45, 'black', 2),
  ('sel-22-3pos', '3 Konumlu Anahtar 22mm', 'selector_switch', 22, 30, 45, 'black', 3);

INSERT INTO cover_element_catalog (id, name, category, cutout_diameter, bezel_diameter, depth_behind_panel, color, voltage) VALUES
  ('lamp-22-green',  'Yeşil Sinyal Lambası 22mm',    'indicator_lamp', 22, 30, 30, 'green',  ARRAY[24,230]),
  ('lamp-22-red',    'Kırmızı Sinyal Lambası 22mm',  'indicator_lamp', 22, 30, 30, 'red',    ARRAY[24,230]),
  ('lamp-22-yellow', 'Sarı Sinyal Lambası 22mm',     'indicator_lamp', 22, 30, 30, 'yellow', ARRAY[24,230]),
  ('lamp-22-blue',   'Mavi Sinyal Lambası 22mm',     'indicator_lamp', 22, 30, 30, 'blue',   ARRAY[24,230]),
  ('lamp-22-white',  'Beyaz Sinyal Lambası 22mm',    'indicator_lamp', 22, 30, 30, 'white',  ARRAY[24,230]);

INSERT INTO cover_element_catalog (id, name, category, cutout_diameter, bezel_diameter, depth_behind_panel, color, function) VALUES
  ('estop-40', 'Acil Stop Butonu 40mm', 'emergency_stop', 22, 40, 50, 'red', 'emergency_stop');

INSERT INTO cover_element_catalog (id, name, category, cutout_width, cutout_height, bezel_width, bezel_height, depth_behind_panel, color) VALUES
  ('ammeter-72',  'Ampermetre 72x72mm', 'ammeter',   68, 68, 72, 72, 50, 'black'),
  ('voltmeter-72','Voltmetre 72x72mm',  'voltmeter', 68, 68, 72, 72, 50, 'black');

-- ==================== SALT MALZEME ====================
INSERT INTO salt_malzeme (part_name, part_code, quantity, description) VALUES
  ('EJB Kapak',                'EJB-COVER',                    1, 'Kutu kapağı'),
  ('CLIPFIX 35/5 Uç Kelepçe', 'pnl_302203_CLIPFIX-35-5',      2, 'DIN ray uç kelepçesi (ray başına 2 adet)'),
  ('Drenaj Valfi M20x1.5',    'Drain_Valve_M20x1.5mm',        1, 'Kondensasyon drenaj valfi M20x1.5mm');

-- ==================== STORAGE BUCKETS ====================
-- Note: Run these via Supabase dashboard or CLI
-- CREATE STORAGE BUCKET 'drawings' (public: false)
-- CREATE STORAGE BUCKET 'labels' (public: false)
