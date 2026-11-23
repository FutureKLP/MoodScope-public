//! Own a packaged backend through a pipe lease, with no PID-file adoption.
use std::io::Read;
use std::path::Path;
use std::process::{Child, ChildStdin, Command, Stdio};
use std::time::{Duration, Instant};

pub struct Backend {
    child: Child,
    lease: Option<ChildStdin>,
    _owner: tempfile::TempDir,
}

fn matches_health(body: &str, owner: &str) -> bool {
    let Ok(value) = serde_json::from_str::<serde_json::Value>(body) else { return false; };
    value["status"] == "ok" && value["version"] == "0.3.0"
        && value["api_revision"] == 16 && value["runtime_owner"] == owner
}

impl Backend {
    pub fn exited(&mut self) -> bool {
        !matches!(self.child.try_wait(), Ok(None))
    }

    pub fn start(resources: &Path, data: &Path, models: &Path) -> Result<Self, String> {
        let executable = resources.join("backend-runtime").join(if cfg!(windows) { "moodscope-backend.exe" } else { "moodscope-backend" });
        if !executable.is_file() { return Err("Packaged MoodScope backend is missing. Reinstall the application.".into()); }
        // Fail closed even when the existing listener reports the right version.
        if std::net::TcpStream::connect_timeout(&"127.0.0.1:8765".parse().unwrap(), Duration::from_millis(500)).is_ok() {
            return Err("Port 8765 is occupied. Close the other service before starting MoodScope.".into());
        }
        std::fs::create_dir_all(data).map_err(|e| e.to_string())?;
        let owner = tempfile::Builder::new().prefix("backend-owner-").tempdir_in(data).map_err(|e| e.to_string())?;
        let identity = owner.path().file_name().unwrap().to_string_lossy().into_owned();
        let log = std::fs::OpenOptions::new().create(true).append(true)
            .open(data.join("backend.log")).map_err(|e| e.to_string())?;
        let mut command = Command::new(executable);
        command.current_dir(data).env("MOODSCOPE_DATA", data).env("MOODSCOPE_MODELS", models)
            .env("HF_HOME", models).env("MOODSCOPE_RUNTIME_OWNER", &identity)
            .env_remove("PYTHONPATH").env_remove("PYTHONHOME")
            .env_remove("HF_HUB_CACHE").env_remove("HUGGINGFACE_HUB_CACHE").env_remove("TRANSFORMERS_CACHE")
            .env("TORCH_HOME", models.join("torch"))
            .env("NUMBA_CACHE_DIR", data.join("cache").join("numba"))
            .stdin(Stdio::piped()).stdout(Stdio::null()).stderr(Stdio::from(log));
        #[cfg(windows)] {
            use std::os::windows::process::CommandExt;
            command.creation_flags(0x08000000);
        }
        let mut child = command.spawn().map_err(|e| e.to_string())?;
        let lease = child.stdin.take();
        let mut backend = Self { child, lease, _owner: owner };
        let client = reqwest::blocking::Client::builder().no_proxy().redirect(reqwest::redirect::Policy::none())
            .timeout(Duration::from_secs(2)).build().map_err(|e| e.to_string())?;
        let deadline = Instant::now() + Duration::from_secs(120);
        while Instant::now() < deadline {
            if backend.child.try_wait().map_err(|e| e.to_string())?.is_some() {
                return Err("MoodScope backend exited. See the user data backend.log.".into());
            }
            if let Ok(response) = client.get("http://127.0.0.1:8765/api/health").send() {
                let successful = response.status().is_success();
                let mut body = String::new();
                if successful && response.take(65536).read_to_string(&mut body).is_ok() && matches_health(&body, &identity) { return Ok(backend); }
            }
            std::thread::sleep(Duration::from_millis(200));
        }
        Err("MoodScope backend readiness timed out. See the user data backend.log.".into())
    }
}

impl Drop for Backend {
    fn drop(&mut self) {
        self.lease.take(); // EOF also occurs if the native app is killed.
        let deadline = Instant::now() + Duration::from_secs(20);
        while Instant::now() < deadline {
            if !matches!(self.child.try_wait(), Ok(None)) { return; }
            std::thread::sleep(Duration::from_millis(100));
        }
        // Never look up or kill a process by port or a persisted PID.
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn rejects_unknown_owner_and_incompatible_contract() {
        let good = r#"{"status":"ok","version":"0.3.0","api_revision":16,"runtime_owner":"own"}"#;
        assert!(matches_health(good, "own"));
        assert!(!matches_health(good, "foreign"));
        assert!(!matches_health(&good.replace(":16", ":15"), "own"));
        assert!(!matches_health("not json", "own"));
    }
}
