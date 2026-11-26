#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
mod export;
mod import;
mod backend;
use tauri::Manager;
use tauri_plugin_dialog::DialogExt;
use std::sync::Mutex;

#[tauri::command]
fn exit_app(app: tauri::AppHandle) {
    app.exit(0);
}

#[tauri::command]
fn restart_app(app: tauri::AppHandle) {
    // The project launcher selects the newest built executable on exit code 75.
    if app.state::<Mutex<Option<backend::Backend>>>().lock().unwrap().is_some() {
        app.request_restart();
    } else { app.exit(75); }
}

#[tauri::command]
fn toggle_fullscreen(window: tauri::WebviewWindow) -> Result<(), String> {
    let fullscreen = window.is_fullscreen().map_err(|e| e.to_string())?;
    window.set_fullscreen(!fullscreen).map_err(|e| e.to_string())
}

fn main() {
    tauri::Builder::default()
        .manage(Mutex::new(None::<backend::Backend>))
        .setup(|app| {
            // Development launchers remain supported. Packaged builds opt in
            // through their resource manifest, never a renderer-supplied path.
            let resources = app.path().resource_dir()?;
            if cfg!(feature = "packaged-backend") {
                let root = app.path().app_local_data_dir()?;
                let service = match backend::Backend::start(&resources, &root.join("data"), &root.join("models")) {
                    Ok(service) => service,
                    Err(error) => {
                        let handle = app.handle().clone();
                        app.dialog().message(error).title("MoodScope backend startup")
                            .kind(tauri_plugin_dialog::MessageDialogKind::Error)
                            .show(move |_| handle.exit(1));
                        return Ok(());
                    }
                };
                *app.state::<Mutex<Option<backend::Backend>>>().lock().unwrap() = Some(service);
                let config = app.config().app.windows.iter().find(|window| window.label == "main")
                    .ok_or("Packaged main window configuration missing")?;
                tauri::WebviewWindowBuilder::from_config(app, config)?.build()?;
                let handle = app.handle().clone();
                std::thread::spawn(move || loop {
                    std::thread::sleep(std::time::Duration::from_millis(250));
                    let ended = {
                        let state = handle.state::<Mutex<Option<backend::Backend>>>();
                        let mut guard = state.lock().unwrap();
                        match guard.as_mut() {
                            Some(service) => service.exited(),
                            None => return,
                        }
                    };
                    if ended {
                        // Stop rendering before another listener could be mistaken
                        // for this session after an unexpected supervisor loss.
                        if let Some(window) = handle.get_webview_window("main") {
                            let _ = window.close();
                        }
                        handle.exit(1);
                        return;
                    }
                });
            }
            Ok(())
        })
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![exit_app, restart_app, toggle_fullscreen, export::save_wave_export, import::import_source])
        .build(tauri::generate_context!())
        .expect("MoodScope desktop runtime failed")
        .run(|app, event| {
            if let tauri::RunEvent::Exit = event {
                app.state::<Mutex<Option<backend::Backend>>>().lock().unwrap().take();
            }
        });
}
