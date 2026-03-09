-- Fix: Grant insert on profiles to the trigger function
-- The SECURITY DEFINER function runs as the owner, but needs explicit grants

GRANT USAGE ON SCHEMA public TO supabase_auth_admin;
GRANT ALL ON TABLE profiles TO supabase_auth_admin;

-- Recreate the trigger function with proper search_path
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, company)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    COALESCE(NEW.raw_user_meta_data->>'company', '')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;
