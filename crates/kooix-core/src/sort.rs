use std::cmp::Ordering;

/// 自然排序键：将字符串拆分为文本和数字片段
fn natural_sort_key(s: &str) -> Vec<NaturalToken> {
    let mut tokens = Vec::new();
    let mut chars = s.chars().peekable();
    while chars.peek().is_some() {
        if chars.peek().unwrap().is_ascii_digit() {
            let num: String = chars.by_ref().take_while(|c| c.is_ascii_digit()).collect();
            tokens.push(NaturalToken::Num(num.parse().unwrap_or(0)));
        } else {
            let text: String = chars
                .by_ref()
                .take_while(|c| !c.is_ascii_digit())
                .collect();
            tokens.push(NaturalToken::Text(text.to_lowercase()));
        }
    }
    tokens
}

#[derive(Debug, Clone)]
enum NaturalToken {
    Text(String),
    Num(u64),
}

impl PartialEq for NaturalToken {
    fn eq(&self, other: &Self) -> bool {
        self.cmp(other) == Ordering::Equal
    }
}
impl Eq for NaturalToken {}

impl PartialOrd for NaturalToken {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for NaturalToken {
    fn cmp(&self, other: &Self) -> Ordering {
        match (self, other) {
            (NaturalToken::Num(a), NaturalToken::Num(b)) => a.cmp(b),
            (NaturalToken::Text(a), NaturalToken::Text(b)) => a.cmp(b),
            (NaturalToken::Num(_), NaturalToken::Text(_)) => Ordering::Less,
            (NaturalToken::Text(_), NaturalToken::Num(_)) => Ordering::Greater,
        }
    }
}

/// 按自然顺序排序文件路径列表
pub fn sort_natural(files: &mut [String]) {
    files.sort_by(|a, b| {
        let ka = natural_sort_key(std::path::Path::new(a).file_name().unwrap_or_default().to_str().unwrap_or(""));
        let kb = natural_sort_key(std::path::Path::new(b).file_name().unwrap_or_default().to_str().unwrap_or(""));
        ka.cmp(&kb)
    });
}
