# Entwicklungsumgebung

MoodScope benötigt Python 3.11 oder neuer und Node.js 22.12 oder neuer. Das Windows-Setup richtet Python 3.13 projektlokal ein. Native Builds benötigen Rust und die plattformspezifischen Tauri-Systembibliotheken.

Unter Windows werden MSVC C++ Build Tools, Windows SDK und WebView2 benötigt. Unter Linux werden unter anderem WebKitGTK 4.1, GTK 3 und native Build-Werkzeuge benötigt. Die Setupskripte installieren keine Betriebssystempakete automatisch.

CUDA ist optional. PyTorch muss die Architektur der vorhandenen NVIDIA-GPU unterstützen. MoodScope prüft eine tatsächliche CUDA-Operation und verwendet bei automatischer Gerätewahl andernfalls die CPU. Die Whisper-Inferenz nutzt standardmäßig die CPU; CTranslate2-CUDA benötigt separat kompatible CUDA/cuDNN-Bibliotheken.

Das aktuelle Windows-Setup verwendet `.venv-modern`; die ältere `.venv` kann als lokale Rückfallumgebung bestehen bleiben. Der Starter bevorzugt die validierte Projektumgebung. Portable Werkzeuge liegen optional in `.tools`. FFmpeg wird über das lokale Python-Paket imageio-ffmpeg bereitgestellt. Diese Verzeichnisse werden nicht veröffentlicht.

Aktuelle Prüfungen und benötigte lokale Testclient-Sockets: [Testbaseline](TEST-BASELINE.md).
