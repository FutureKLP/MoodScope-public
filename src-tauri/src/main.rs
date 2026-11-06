#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
mod export;

#[tauri::command]
fn exit_app(app: tauri::AppHandle) {
    app.exit(0);
}

#[tauri::command]
fn restart_app(app: tauri::AppHandle) {
    // The project launcher selects the newest built executable on exit code 75.
    app.exit(75);
}

#[tauri::command]
fn toggle_fullscreen(window: tauri::WebviewWindow) -> Result<(), String> {
    let fullscreen = window.is_fullscreen().map_err(|e| e.to_string())?;
    window.set_fullscreen(!fullscreen).map_err(|e| e.to_string())
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![exit_app, restart_app, toggle_fullscreen, export::save_wave_export])
        .run(tauri::generate_context!())
        .expect("MoodScope desktop runtime failed");
}
