use std::io::{Read, Write, Seek, SeekFrom};
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

fn persist_wave_export(mut source: impl Read, path: &std::path::Path) -> Result<(), String> {
    let parent = path.parent().ok_or("export-destination")?;
    let mut header = [0_u8; 12];
    source.read_exact(&mut header).map_err(|_| "export-download")?;
    if &header[0..4] != b"RIFF" || &header[8..12] != b"WAVE" { return Err("export-format".into()); }
    let expected = u32::from_le_bytes(header[4..8].try_into().unwrap()) as u64 + 8;
    if expected < 12 || expected > MAX_BYTES { return Err("export-size".into()); }
    let mut temporary = tempfile::NamedTempFile::new_in(parent).map_err(|_| "export-write")?;
    temporary.write_all(&header).map_err(|_| "export-write")?;
    let copied = std::io::copy(&mut source.take(MAX_BYTES + 1), &mut temporary).map_err(|_| "export-download")?;
    if copied > MAX_BYTES - 12 { return Err("export-size".into()); }
    if copied + 12 != expected { return Err("export-download".into()); }
    validate_wave(temporary.as_file_mut(), expected)?;
    temporary.as_file_mut().sync_all().map_err(|_| "export-write")?;
    temporary.persist(path).map_err(|_| "export-write")?;
    Ok(())
}

// Inspect bounded chunk headers without decoding or retaining the audio in RAM.
fn validate_wave(file: &mut std::fs::File, size: u64) -> Result<(), String> {
    let invalid = || "export-format".to_string();
    let mut offset = 12_u64;
    let mut alignment = 0_u16;
    let mut has_data = false;
    while offset + 8 <= size {
        file.seek(SeekFrom::Start(offset)).map_err(|_| invalid())?;
        let mut header = [0_u8; 8];
        file.read_exact(&mut header).map_err(|_| invalid())?;
        let length = u32::from_le_bytes(header[4..8].try_into().unwrap()) as u64;
        let next = offset + 8 + length + length % 2;
        if next > size { return Err(invalid()); }
        if &header[..4] == b"fmt " {
            if alignment != 0 || length < 16 { return Err(invalid()); }
            let mut fmt = [0_u8; 16];
            file.read_exact(&mut fmt).map_err(|_| invalid())?;
            let format = u16::from_le_bytes(fmt[0..2].try_into().unwrap());
            let channels = u16::from_le_bytes(fmt[2..4].try_into().unwrap());
            let rate = u32::from_le_bytes(fmt[4..8].try_into().unwrap());
            let byte_rate = u32::from_le_bytes(fmt[8..12].try_into().unwrap());
            alignment = u16::from_le_bytes(fmt[12..14].try_into().unwrap());
            let bits = u16::from_le_bytes(fmt[14..16].try_into().unwrap());
            if ![1, 3].contains(&format) || ![1, 2].contains(&channels) || rate == 0
                || ![8, 16, 24, 32, 64].contains(&bits) || (format == 3 && ![32, 64].contains(&bits))
                || alignment != channels * bits / 8 || u64::from(byte_rate) != u64::from(rate) * u64::from(alignment) {
                return Err(invalid());
            }
        }
        if &header[..4] == b"data" {
            if alignment == 0 || has_data || length == 0 || length % u64::from(alignment) != 0 { return Err(invalid()); }
            has_data = true;
        }
        offset = next;
    }
    if offset != size || !has_data { return Err(invalid()); }
    Ok(())
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
        let client = reqwest::blocking::Client::builder().no_proxy().redirect(reqwest::redirect::Policy::none()).timeout(Duration::from_secs(180)).build().map_err(|_| "export-download")?;
        let response = client.get(url).send().map_err(|_| "export-download")?.error_for_status().map_err(|_| "export-download")?;
        if response.content_length().is_some_and(|size| size > MAX_BYTES) { return Err("export-size".into()); }
        // Keep the selected destination intact if transfer fails or the app exits.
        persist_wave_export(response, &path)?;
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
    #[test]
    fn malformed_chunks_and_trailing_payloads_preserve_destination() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("authored.wav");
        let wave = b"RIFF\x28\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00\x80\xbb\x00\x00\x00\xee\x02\x00\x04\x00\x10\x00data\x04\x00\x00\x00\x00\x00\x00\x00";
        let mut missing = wave.to_vec(); missing[36..40].copy_from_slice(b"JUNK");
        let mut invalid = wave.to_vec(); invalid[32] = 3;
        let mut truncated = wave.to_vec(); truncated[40] = 100;
        let mut trailing = wave.to_vec(); trailing.extend_from_slice(b"extra");
        for bytes in [missing, invalid, truncated, trailing, b"RIFF\x08\x00\x00\x00WAVEdata".to_vec()] {
            std::fs::write(&path, b"preserve destination").unwrap();
            assert!(persist_wave_export(std::io::Cursor::new(bytes), &path).is_err());
            assert_eq!(std::fs::read(&path).unwrap(), b"preserve destination");
            assert_eq!(std::fs::read_dir(dir.path()).unwrap().count(), 1);
        }
    }
    #[test]
    fn failed_and_truncated_transfers_preserve_existing_destination() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("authored.wav");
        std::fs::write(&path, b"existing authored audio").unwrap();
        for input in [b"RIFF".to_vec(), b"invalid-header".to_vec(), b"RIFF\x20\x00\x00\x00WAVEshort".to_vec()] {
            assert!(persist_wave_export(std::io::Cursor::new(input), &path).is_err());
            assert_eq!(std::fs::read(&path).unwrap(), b"existing authored audio");
            assert_eq!(std::fs::read_dir(dir.path()).unwrap().count(), 1);
        }
        let complete = b"RIFF\x28\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00\x80\xbb\x00\x00\x00\xee\x02\x00\x04\x00\x10\x00data\x04\x00\x00\x00\x00\x00\x00\x00";
        persist_wave_export(std::io::Cursor::new(complete), &path).unwrap();
        assert_eq!(std::fs::read(&path).unwrap(), complete);
    }
}
