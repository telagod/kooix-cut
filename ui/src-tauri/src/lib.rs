use kooix_core::{config::Config, video};
use serde::Serialize;
use tauri::Emitter;

#[derive(Clone, Serialize)]
struct ProgressPayload {
    current: usize,
    total: usize,
    name: String,
}

#[tauri::command]
async fn process_videos(
    app: tauri::AppHandle,
    input_dir: String,
    output: String,
    threshold: f64,
    min_duration: f64,
    codec: String,
    preset: String,
) -> Result<String, String> {
    let config = Config {
        silence_threshold: threshold,
        min_duration,
        codec,
        preset,
        output_file: output,
        ..Default::default()
    };
    let app_clone = app.clone();
    tokio::task::spawn_blocking(move || {
        video::process_videos(&input_dir, &config, |current, total, name| {
            let _ = app_clone.emit(
                "progress",
                ProgressPayload {
                    current,
                    total,
                    name: name.to_string(),
                },
            );
        })
    })
    .await
    .map_err(|e| e.to_string())?
    .map_err(|e| e.to_string())?;
    Ok("处理完成".into())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![process_videos])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
