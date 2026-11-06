use std::io::{Read, Write};
use std::time::Duration;
use tauri_plugin_dialog::DialogExt;

const MAX_BYTES: u64 = 1024 * 1024 * 1024;
const SOURCES: [&str; 6] = ["vocals", "drums", "bass", "other", "guitar", "piano"];

fn export_url(track_id: &str, model: &str, sources: &[String], gains: &[f64]) -> Result<String, String> {
    if track_id.len() != 64 || !track_id.bytes().all(|b| b.is_ascii_hexdigit())
        || !["htdemucs", "htdemucs_ft", "htdemucs_6s", "htdemucs_auto"].contains(&model)
        || sources.is_empty() || sources.len() > 6 || sources.len() != gains.len()
        || !sources.iter().all(|s| SOURCES.contains(&s.as_str()))
        || !gains.iter().all(|g| g.is_finite() && (0.0..=1.0).contains(g)) {
        return Err("export-invalid".into());
    }
    let gains = gains.iter().map(|g| g.to_string()).collect::<Vec<_>>().join(",");
    // The renderer cannot supply a host, URL, filesystem path or redirect target.
    Ok(format!("http://127.0.0.1:8765/api/tracks/{track_id}/mix?model={model}&sources={}&gains={gains}", sources.join(",")))
}

fn suggested_name(filename: &str) -> String {
    let clean: String = filename.chars().filter(|c| !c.is_control() && !"<>:\"/\\|?*".contains(*c)).take(160).collect();
    let base = clean.trim().trim_end_matches('.');
    if base.is_empty() { return "MoodScope-Mix.wav".into(); }
    if base.to_lowercase().ends_with(".wav") { base.into() } else { format!("{base}.wav") }
}

#[tauri::command]
pub async fn save_wave_export(app: tauri::AppHandle, track_id: String, model: String, sources: Vec<String>, gains: Vec<f64>, filename: String, language: String) -> Result<bool, String> {
    let url = export_url(&track_id, &model, &sources, &gains)?;
    tauri::async_runtime::spawn_blocking(move || {
        let title = if language == "en" { "Export WAV" } else { "WAV exportieren" };
        let chosen = app.dialog().file().set_title(title).add_filter("WAV", &["wav"]).set_file_name(suggested_name(&filename)).blocking_save_file();
        let Some(chosen) = chosen else { return Ok(false); };
        let path = chosen.into_path().map_err(|_| "export-destination")?;
        if !path.extension().is_some_and(|s| s.to_string_lossy().eq_ignore_ascii_case("wav")) { return Err("export-extension".into()); }
        let parent = path.parent().ok_or("export-destination")?;
        let client = reqwest::blocking::Client::builder().no_proxy().redirect(reqwest::redirect::Policy::none()).timeout(Duration::from_secs(180)).build().map_err(|_| "export-download")?;
        let mut response = client.get(url).send().map_err(|_| "export-download")?.error_for_status().map_err(|_| "export-download")?;
        if response.content_length().is_some_and(|size| size > MAX_BYTES) { return Err("export-size".into()); }
        let mut header = [0_u8; 12];
        response.read_exact(&mut header).map_err(|_| "export-download")?;
        if &header[0..4] != b"RIFF" || &header[8..12] != b"WAVE" { return Err("export-format".into()); }
        // Keep the selected destination intact if transfer fails or the app exits.
        let mut temporary = tempfile::NamedTempFile::new_in(parent).map_err(|_| "export-write")?;
        temporary.write_all(&header).map_err(|_| "export-write")?;
        let copied = std::io::copy(&mut response.take(MAX_BYTES + 1), &mut temporary).map_err(|_| "export-download")?;
        if copied > MAX_BYTES - 12 { return Err("export-size".into()); }
        temporary.as_file_mut().sync_all().map_err(|_| "export-write")?;
        temporary.persist(path).map_err(|_| "export-write")?;
        Ok(true)
    }).await.map_err(|_| "export-failed".to_string())?
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn only_managed_loopback_exports_are_allowed() {
        let id = "a".repeat(64);
        assert!(export_url(&id,"htdemucs",&["vocals".into()],&[0.5]).unwrap().starts_with("http://127.0.0.1:8765/"));
        for bad in ["../outside", "https://example.invalid", "a?b"] { assert!(export_url(bad,"htdemucs",&["vocals".into()],&[1.0]).is_err()); }
        assert!(export_url(&id,"other",&["vocals".into()],&[1.0]).is_err());
        assert!(export_url(&id,"htdemucs",&["../outside".into()],&[1.0]).is_err());
        assert!(export_url(&id,"htdemucs",&["vocals".into()],&[f64::NAN]).is_err());
        assert!(export_url(&id,"htdemucs",&["vocals".into()],&[]).is_err());
    }
    #[test]
    fn dialog_suggestions_cannot_contain_paths() {
        assert_eq!(suggested_name("../Song: vocals.wav"), "..Song vocals.wav");
        assert_eq!(suggested_name(""), "MoodScope-Mix.wav");
    }
}
