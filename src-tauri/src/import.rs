use std::fs::File;
use std::io::{Cursor, Read};
use std::path::Path;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tauri_plugin_dialog::DialogExt;

const AUDIO_LIMIT: u64 = 250 * 1024 * 1024;
const TEXT_LIMIT: u64 = 1024 * 1024;

fn after_selection<T>(chosen: Option<T>, import: impl FnOnce(T) -> Result<String, String>) -> Result<Option<String>, String> {
    chosen.map(import).transpose()
}

fn open_source(path: &Path, lyrics: bool) -> Result<(File, u64), String> {
    let extension = path.extension().unwrap_or_default().to_string_lossy().to_lowercase();
    let allowed: &[&str] = if lyrics { &["lrc", "txt"] } else { &["mp3", "wav", "flac"] };
    if !allowed.contains(&extension.as_str()) { return Err("import-extension".into()); }
    let file = File::open(path).map_err(|_| "import-read")?;
    let metadata = file.metadata().map_err(|_| "import-read")?;
    if !metadata.is_file() { return Err("import-read".into()); }
    let length = metadata.len();
    if length > if lyrics { TEXT_LIMIT } else { AUDIO_LIMIT } { return Err("import-size".into()); }
    Ok((file, length))
}

fn read_lyrics(path: &Path) -> Result<String, String> {
    let (file, _) = open_source(path, true)?;
    let mut bytes = Vec::new();
    file.take(TEXT_LIMIT + 1).read_to_end(&mut bytes).map_err(|_| "import-read")?;
    if bytes.len() as u64 > TEXT_LIMIT { return Err("import-size".into()); }
    // Match File.text(): UTF-8 with replacement and an optional leading BOM.
    let text = String::from_utf8_lossy(&bytes).trim_start_matches('\u{feff}').to_string();
    if text.chars().count() > 200_000 { return Err("import-size".into()); }
    Ok(text)
}

fn multipart_header(boundary: &str, name: &str) -> Vec<u8> {
    let safe: String = name.chars().map(|c| if c.is_control() || "\"\\".contains(c) { '_' } else { c }).collect();
    format!("--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{safe}\"\r\nContent-Type: application/octet-stream\r\n\r\n").into_bytes()
}

fn import_audio(path: &Path, language: &str) -> Result<String, String> {
    let (file, length) = open_source(path, false)?;
    let boundary = format!("moodscope-{:x}-{:x}", std::process::id(), SystemTime::now().duration_since(UNIX_EPOCH).map_err(|_| "import-read")?.as_nanos());
    let header = multipart_header(&boundary, &path.file_name().unwrap_or_default().to_string_lossy());
    let footer = format!("\r\n--{boundary}--\r\n").into_bytes();
    let size = header.len() as u64 + length + footer.len() as u64;
    let source = Cursor::new(header).chain(file.take(length)).chain(Cursor::new(footer));
    let client = reqwest::blocking::Client::builder().no_proxy().redirect(reqwest::redirect::Policy::none())
        .timeout(Duration::from_secs(180)).build().map_err(|_| "import-service")?;
    // The renderer cannot supply a filesystem path, host, URL or redirect target.
    let response = client.post("http://127.0.0.1:8765/api/tracks")
        .header("Content-Type", format!("multipart/form-data; boundary={boundary}"))
        .header("Accept-Language", if language == "en" { "en" } else { "de" })
        .body(reqwest::blocking::Body::sized(source, size)).send().map_err(|_| "import-service")?;
    let success = response.status().is_success();
    let mut body = String::new();
    response.take(65537).read_to_string(&mut body).map_err(|_| "import-service")?;
    if body.len() > 65536 { return Err("import-service".into()); }
    if !success { return Err(format!("import-http:{body}")); }
    Ok(body)
}

#[tauri::command]
pub async fn import_source(app: tauri::AppHandle, window: tauri::WebviewWindow, kind: String, language: String) -> Result<Option<String>, String> {
    if !["audio", "lyrics"].contains(&kind.as_str()) { return Err("import-kind".into()); }
    tauri::async_runtime::spawn_blocking(move || {
        let lyrics = kind == "lyrics";
        let title = match (lyrics, language.as_str()) {
            (true, "en") => "Import LRC", (true, _) => "LRC importieren",
            (false, "en") => "Import audio", (false, _) => "Audio importieren",
        };
        let picker = app.dialog().file().set_parent(&window).set_title(title);
        let picker = if lyrics { picker.add_filter("LRC / TXT", &["lrc", "txt"]) }
            else { picker.add_filter("MP3 / WAV / FLAC", &["mp3", "wav", "flac"]) };
        after_selection(picker.blocking_pick_file(), |chosen| {
            let path = chosen.into_path().map_err(|_| "import-read")?;
            if lyrics { read_lyrics(&path) } else { import_audio(&path, &language) }
        })
    }).await.map_err(|_| "import-service".to_string())?
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn cancellation_never_reads_or_uploads_a_file() {
        assert_eq!(after_selection(None::<&Path>, |_| panic!("cancelled import")), Ok(None));
        assert_eq!(after_selection(Some("selected"), |_| Err("failure".into())), Err("failure".into()));
    }
    #[test]
    fn selected_lyrics_preserve_timestamps_and_source_bytes() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("source.LRC");
        let bytes = b"\xef\xbb\xbf[00:10.25]Authored line\r\n[00:25.00]Next";
        std::fs::write(&path, bytes).unwrap();
        assert_eq!(read_lyrics(&path).unwrap(), "[00:10.25]Authored line\r\n[00:25.00]Next");
        assert_eq!(std::fs::read(&path).unwrap(), bytes);
        assert!(open_source(&path, false).is_err());
        let oversized = dir.path().join("large.txt");
        File::create(&oversized).unwrap().set_len(TEXT_LIMIT + 1).unwrap();
        assert_eq!(read_lyrics(&oversized), Err("import-size".into()));
    }
    #[test]
    fn multipart_filename_cannot_add_headers() {
        let header = String::from_utf8(multipart_header("boundary", "test\"\r\nInjected: yes\\.wav")).unwrap();
        assert!(header.contains("filename=\"test___Injected: yes_.wav\""));
        assert_eq!(header.matches("\r\n").count(), 4);
    }
}
