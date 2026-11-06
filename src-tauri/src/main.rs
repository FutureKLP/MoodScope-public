#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

#[tauri::command]
fn exit_app(app: tauri::AppHandle) {
    app.exit(0);
}

#[tauri::command]
fn toggle_fullscreen(window: tauri::WebviewWindow) -> Result<(), String> {
    let fullscreen = window.is_fullscreen().map_err(|e| e.to_string())?;
    window.set_fullscreen(!fullscreen).map_err(|e| e.to_string())
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![exit_app, toggle_fullscreen])
        .run(tauri::generate_context!())
        .expect("MoodScope desktop runtime failed");
}
