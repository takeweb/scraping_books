from supabase import create_client, Client
import os
import sys
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    print("⚠️ Supabase URLまたはAPIキーが設定されていません。環境変数 SUPABASE_URL, SUPABASE_KEY を確認してください。")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)