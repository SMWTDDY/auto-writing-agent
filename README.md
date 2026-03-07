# 自动写作代理 (Auto Writing Agent)

一个基于大语言模型的**全自动网络小说生成系统**，可根据规范和伪代码自动完成从大纲到发布的整个创作流程。

## ✨ 核心特性

- 🤖 **智能大纲生成**：AI自动生成符合规范的详细大纲，并进行多轮迭代优化
- 📝 **自动章节创作**：基于大纲和上下文自动生成每个章节的正文
- ✅ **质量审计系统**：对每章节进行智能审计，不合格自动重写
- 📚 **上下文管理**：维护长期记忆、中期摘要和未来发展规划
- 🚀 **自动发布**：支持异步周期发布，自动管理发布状态
- 🔄 **断点恢复**：支持中途中断后的恢复和继续写作

## 🏗️ 系统架构

遵循规范定义的**三阶段工作流**：

```
┌─────────────────────────────────────────────────────────┐
│         阶段一：初始化与大纲构建                          │
│  ┌────────────────────────────────────────────────────┐│
│  │ 1. 创建书籍文件夹结构                              ││
│  │ 2. AI生成初步大纲                                  ││
│  │ 3. 迭代优化大纲（x次）                            ││
│  │ 4. 保存最终大纲 → master_outline.txt              ││
│  └────────────────────────────────────────────────────┘│
└────────────────┬──────────────────────────────────────────┘
                 │
┌────────────────▼──────────────────────────────────────────┐
│         阶段二：章节迭代创作（核心阶段）                   │
│  ┌────────────────────────────────────────────────────┐│
│  │ For 每个章节:                                      ││
│  │  1. 准备上下文 (前x和前y章内容)                   ││
│  │  2. AI生成章节正文 (800-1500字)                   ││
│  │  3. 质量审计 (评分必须≥70)                        ││
│  │     - 未通过则AI重写 (迭代y次)                   ││
│  │  4. 更新上下文大纲 → Context_n.txt               ││
│  │  5. 保存章节 → Chapter_n.txt                      ││
│  └────────────────────────────────────────────────────┘│
└────────────────┬──────────────────────────────────────────┘
                 │
┌────────────────▼──────────────────────────────────────────┐
│         阶段三：发布管理                                   │
│  ┌────────────────────────────────────────────────────┐│
│  │ 1. 监控已完成的章节                                ││
│  │ 2. 当达到阈值时自动上传                            ││
│  │ 3. 标记上传状态                                    ││
│  └────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## 📁 项目结构

```
auto writing agent/
├── src/                          # 核心程序
│   ├── main.py                  # 主程序入口
│   ├── config.py                # 配置管理
│   ├── utils.py                 # 工具函数
│   ├── stage1_outline.py        # 大纲生成
│   ├── stage2_chapter.py        # 章节创作
│   └── stage3_publish.py        # 发布管理
│
├── book/                         # 输出文件夹（自动创建）
│   └── 书籍名称/
│       ├── Outline/
│       │   ├── Full_Outline.txt
│       │   └── master_outline.txt
│       ├── Chapters/
│       │   ├── Chapter_1.txt
│       │   └── ...
│       ├── Context/
│       │   ├── Context_1.txt
│       │   └── ...
│       └── Check_Specs/
│
├── .env                         # API密钥配置
├── requirements.txt             # 依赖包列表
├── USAGE.md                     # 详细使用说明
├── 伪代码与规范                 # 规范文档
└── README.md                    # 本文件
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆或进入项目目录
cd auto\ writing\ agent

# 安装依赖
pip install -r requirements.txt
```

### 2. API配置

编辑 `.env` 文件：
```env
api_key=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. 开始创作

```bash
# 最简单的用法
python src/main.py --theme "你的书籍主题"

# 指定书名、章节数
python src/main.py --theme "悬疑推理" --name "密室谜案" --chapters 15

# 仅生成大纲（阶段一）
python src/main.py --theme "科幻冒险" --stage 1

# 恢复中断的写作
python src/main.py --resume ./book/mybook --start-chapter 5 --chapters 5

# 检查创作进度
python src/main.py --check ./book/mybook
```

## 📋 命令行使用

详见 [USAGE.md](USAGE.md)

常用命令示例：
```bash
# 完整流程：生成大纲+10章节+发布
python src/main.py -t "网络文学主题" -c 10

# 恢复中断
python src/main.py --resume ./book/mybook --start-chapter 8 --chapters 5

# 查看状态
python src/main.py --check ./book/mybook
```

## 🔧 配置参数

在 `src/config.py` 中可自定义：

| 参数 | 说明 | 默认值 |
|-----|------|--------|
| `OUTLINE_ITERATIONS` | 大纲迭代次数 | 3 |
| `X_CHAPTERS` | 生成正文时加入的前x章全文 | 1 |
| `Y_CHAPTERS` | 生成正文时加入的前y章上下文 | 5 |
| `TEXT_CHECK_ITERATIONS` | 每章质量检查次数 | 2 |
| `UPLOAD_THRESHOLD` | 触发上传的章节累积数 | 3 |

## 📊 质量检查规范

系统对每章节执行5大检查：

1. **角色一致性** - 人物是否符合大纲设定
2. **大纲符合度** - 内容是否符合中心思想
3. **逻辑连贯性** - 是否存在矛盾或漏洞
4. **技术质量** - 语法、表达清晰度
5. **章节匹配度** - 内容与标题是否相符

评分≥70分判定为通过，未通过自动重写。

## 🎯 工作原理

### 阶段一：大纲构建 (Stage 1)

1. **初始化**：创建项目文件夹
2. **生成初稿**：AI根据主题生成初步大纲
3. **迭代优化**：进行x轮优化（默认3轮）
   - 检查逻辑连贯性
   - 调整章节分布
   - 强化冲突设置
4. **保存最终**：保存优化后的大纲

### 阶段二：章节创作 (Stage 2) - 核心阶段

对于每个章节：

```python
# 伪代码流程
for chapter_n in range(1, total_chapters):
    # 1. 准备上下文
    context = prepare_context(chapter_n)
    
    # 2. 生成正文
    chapter_text = generate_by_ai(context)
    
    # 3. 质量检查（可能多轮）
    for check_round in range(check_iterations):
        result = check_quality(chapter_text)
        if result.pass:
            break
        else:
            chapter_text = revise_by_ai(result.issues)
    
    # 4. 更新上下文
    new_context = update_context(chapter_text)
    save_context(new_context)
    
    # 5. 保存章节
    save_chapter(chapter_text)
```

关键特性：
- 动态上下文：每章节生成和更新专属的上下文
- 质量保证：强制审计，不合格自动重写
- 连贯性维护：加载前面章节内容作为提示

### 阶段三：发布管理 (Stage 3)

- 监控：定期检查已完成的章节
- 触发：达到阈值自动上传（可自定义API）
- 记录：维护发布状态

## 🛠️ 技术栈

- **Python 3.7+**
- **OpenAI API** (GPT-4/GPT-3.5)
- **requests** - HTTP库
- **pathlib** - 文件管理

## 📈 使用成本估算

以10章、平均2000token/章计算：

- 阶段一（大纲）：~4,000-5,000 tokens
- 阶段二（写作）：~20,000-30,000 tokens  （含迭代+检查）
- **总计**：~30,000 tokens ≈ $0.3-0.6 (GPT-3.5) 或 $3-6 (GPT-4)

*成本因模型和迭代次数而异*

## 🔍 故障排查

### API 连接错误
- 检查 `.env` 中的密钥是否正确
- 检查网络连接
- 检查API配额和余额

### 文件权限错误
- 确保 ./book/ 目录可写
- Windows用户检查文件夹权限

### 中途中断
- 使用 `--resume` 从中断点继续
- 系统会自动跳过已完成的章节

## 📚 扩展和定制

### 自定义上下文格式
修改 `stage2_chapter.py` 中的 `update_context_outline()` 方法

### 集成其他API
编辑 `utils.py` 中的 `AIClient` 类，支持其他大模型

### 自定义发布平台
在 `stage3_publish.py` 中的 `upload_chapter()` 实现实际的API调用

## 📖 了解更多

- [详细使用指南](USAGE.md)
- [伪代码与规范](伪代码与规范)

## ⚖️ 许可证

MIT License

## 🤝 贡献

欢迎提issue和PR改进这个项目！

## 💬 反馈

如有问题或建议，请提交issue。

---

**祝您创作快乐！🎉**

*自动写作代理 v1.0*
