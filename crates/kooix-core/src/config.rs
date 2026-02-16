/// 处理配置
pub struct Config {
    pub silence_threshold: f64,
    pub min_duration: f64,
    pub window_size: f64,
    pub smoothing: usize,
    pub padding: f64,
    pub codec: String,
    pub preset: String,
    pub output_file: String,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            silence_threshold: 0.01,
            min_duration: 3.0,
            window_size: 0.3,
            smoothing: 3,
            padding: 0.5,
            codec: "libx264".into(),
            preset: "fast".into(),
            output_file: "output.mp4".into(),
        }
    }
}
