fn main() {
    if std::env::var("PROFILE").as_deref() == Ok("release") && tauri_build::is_dev() {
        panic!("Release builds must embed the frontend. Use npm run tauri build -- --no-bundle or enable tauri/custom-protocol.");
    }
    tauri_build::build()
}
