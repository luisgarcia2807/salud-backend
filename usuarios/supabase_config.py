from supabase import create_client, Client

SUPABASE_URL = "https://aerrtkevqiajbrckbchv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFlcnJ0a2V2cWlhamJyY2tiY2h2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg3NTAwOTAsImV4cCI6MjA2NDMyNjA5MH0.z09xD2OiJ4p3TQWDW68E866H0ja3RDSVLatP3oFlu80"  # tu clave anon completa

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
