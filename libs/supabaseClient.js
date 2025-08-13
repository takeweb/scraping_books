import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
  console.warn(
    "⚠️ Supabase URL or Anon Key is not configured. Please set them in a .env file (e.g., .env.local)."
  );
  // 環境変数が設定されていない場合、アプリの実行を停止するか、エラーメッセージを表示
  const appDiv = document.querySelector("#app");
  if (appDiv) {
    appDiv.innerHTML = `
      <h1>設定エラー</h1>
      <p style="color: red;">Supabase URLまたはAnon Keyが設定されていません。.envファイルを確認してください。</p>
    `;
  }
  throw new Error("Supabase credentials are not set.");
}

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
