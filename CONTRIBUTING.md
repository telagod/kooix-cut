# 贡献指南

感谢您对 KOOI Cut 的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告 Bug

如果您发现了 bug，请：
1. 检查 [Issues](https://github.com/YOUR_USERNAME/kooix-cut/issues) 是否已有相关报告
2. 如果没有，创建新 Issue，包含：
   - 清晰的标题
   - 详细的复现步骤
   - 预期行为 vs 实际行为
   - 系统环境（OS、Python 版本等）
   - 错误日志（如果有）

### 提出新功能

1. 先在 Issues 中讨论您的想法
2. 说明功能的用途和价值
3. 如果可能，提供实现思路

### 提交代码

1. **Fork 仓库**
   ```bash
   git clone https://github.com/YOUR_USERNAME/kooix-cut.git
   cd kooix-cut
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **开发**
   - 遵循现有代码风格
   - 添加必要的注释
   - 保持代码简洁（KISS 原则）

4. **测试**
   ```bash
   # 运行程序测试
   uv run modern_gui.py
   ```

5. **提交**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

6. **推送并创建 PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 代码规范

### Python 风格
- 遵循 PEP 8
- 使用类型注解
- 函数和类添加文档字符串

### 提交信息
使用语义化提交：
- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码格式
- `refactor:` 重构
- `perf:` 性能优化
- `test:` 测试相关

### 示例
```
feat: 添加 Whisper 字幕生成功能

- 集成 Whisper 模型
- 支持多语言识别
- 添加字幕导出功能
```

## 开发环境

### 依赖安装
```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e ".[dev]"
```

### 项目结构
```
kooix-cut/
├── gui.py              # 经典 GUI
├── modern_gui.py       # 现代化 GUI
├── kooix_cut.py        # 核心处理逻辑
├── ai_detect.py        # AI 检测模块
├── pyproject.toml      # 项目配置
├── README.md           # 项目文档
├── ROADMAP.md          # 开发路线图
└── CHANGELOG.md        # 更新日志
```

## 优先级

我们特别欢迎以下方面的贡献：

1. 🔥 **性能优化** - 更快的处理速度
2. 🤖 **AI 功能** - 智能检测和分析
3. 🎨 **用户体验** - 更友好的界面
4. 🌍 **跨平台** - Windows/macOS/Linux 支持
5. 📝 **文档** - 教程、示例、翻译

## 行为准则

- 尊重他人
- 保持友善和专业
- 接受建设性批评
- 关注项目目标

## 问题？

如有任何问题，欢迎：
- 创建 Issue
- 发起 Discussion
- 联系维护者

---

感谢您的贡献！❤️
