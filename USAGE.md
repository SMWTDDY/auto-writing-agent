# 自动写作代理 - 使用说明

## 项目概述

自动写作代理是一个基于AI的自动网络小说生成系统，它能够根据用户提供的主题，自动完成**大纲生成、章节创作和发布**的全流程。

系统遵循规范的三阶段工作流：
1. **阶段一**：初始化与大纲构建
2. **阶段二**：章节迭代创作  
3. **阶段三**：发布与监控

## 项目结构

```
src/
├── main.py              # 主程序入口
├── config.py            # 配置管理
├── utils.py             # 工具函数集
├── stage1_outline.py    # 阶段一：大纲生成
├── stage2_chapter.py    # 阶段二：章节创作
└── stage3_publish.py    # 阶段三：发布管理
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑 `.env` 文件，设置您的OpenAI API密钥：

```env
api_key=your_api_key_here
```

### 3. 运行程序

#### 完整流程（推荐）
```bash
python src/main.py --theme "你的书籍主题" --chapters 10
```

#### 指定书籍名称
```bash
python src/main.py --theme "悬疑推理" --name "密室谜案" --chapters 15
```

#### 仅执行阶段一（大纲生成）
```bash
python src/main.py --theme "网络文学主题" --stage 1
```

#### 恢复中断的写作
```bash
python src/main.py --resume /path/to/book_folder --start-chapter 5 --chapters 5
```

#### 检查书籍状态
```bash
python src/main.py --check /path/to/book_folder
```

## 命令行参数

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--theme` | `-t` | **必需**：书籍主题 | `--theme "悬疑推理"` |
| `--name` | `-n` | 书籍名称，不指定则由AI生成 | `--name "密室谜案"` |
| `--chapters` | `-c` | 计划生成的章节数，默认10 | `--chapters 20` |
| `--stage` | `-s` | 执行的阶段（1/2/3）默认执行全部 | `--stage 1` |
| `--resume` | - | 恢复写作，指定书籍文件夹 | `--resume ./book/mybook` |
| `--start-chapter` | - | 恢复写作的起始章节 | `--start-chapter 5` |
| `--check` | - | 检查书籍创作状态 | `--check ./book/mybook` |

## 使用示例

### 完整示例：从零开始创作一部悬疑小说

```bash
# 1. 生成整个流程（大纲 + 10章节 + 发布）
python src/main.py --theme "侦探与失踪案件的真相" --name "迷局" --chapters 10

# 2. 检查创作进度
python src/main.py --check ./book/迷局

# 3. 如果中途中断，继续写作
python src/main.py --resume ./book/迷局 --start-chapter 8 --chapters 3

# 4. 再次检查状态
python src/main.py --check ./book/迷局
```

## 输出文件结构

执行完成后，生成的文件位于 `/book` 文件夹：

```
/book/
└── 书籍名称/
    ├── Outline/
    │   ├── Full_Outline.txt       # 全文大纲（初始，不可修改）
    │   └── master_outline.txt     # 最终大纲（优化版）
    ├── Chapters/
    │   ├── Chapter_1.txt
    │   ├── Chapter_2.txt
    │   └── ...
    ├── Context/
    │   ├── Context_1.txt
    │   ├── Context_2.txt
    │   └── ...
    ├── Check_Specs/
    │   └── check_standards.txt    # 质量检查标准
    └── publish_status.json        # 发布状态记录
```

## 系统配置参数

在 `src/config.py` 中可配置以下参数：

```python
# 阶段一参数
OUTLINE_ITERATIONS = 3              # 大纲迭代次数

# 阶段二参数  
X_CHAPTERS = 1                      # 生成正文时加入的前x章节全文（可保持连贯性）
Y_CHAPTERS = 5                      # 生成正文时加入的前y章章上下文大纲
TEXT_CHECK_ITERATIONS = 2           # 每章节的质量检查次数

# 阶段三参数
UPLOAD_THRESHOLD = 3                # 累积多少章节后触发上传
```

## 工作流程详解

### 阶段一：大纲构建

1. **初始化**：根据主题创建书籍文件夹和子目录
2. **大纲生成**：AI根据主题生成初步大纲，包括：
   - 书籍背景与世界观
   - 中心思想与剧情发展
   - 关键人物设定
   - 关键设定和冲突
3. **迭代优化**：进行多轮大纲修改，优化逻辑连贯性和故事设置
4. **保存**：最终大纲保存到 `master_outline.txt`

### 阶段二：章节创作

对于每个章节（1到总章节数）：

1. **上下文准备**
   - 第一章：仅使用全文大纲
   - 其他章：加载前x章的全文内容和前y章的上下文大纲
   
2. **正文生成**：AI根据大纲和上下文生成章节正文（800-1500字）

3. **质量审计**（核心步骤）
   - 按检查规范评估章节质量
   - 评分≥70分判定为通过
   - 未通过则进行重写

4. **上下文更新**：根据新生成的章节更新上下文大纲
   - 长期记忆：人物和设定信息
   - 中期摘要：最近几章的内容总结
   - 未来大纲：接下来的剧情方向

5. **持久化**：保存章节内容和上下文

### 阶段三：发布管理

1. **监控**：检查已完成且未上传的章节数
2. **触发**：当达到上传阈值时，开始上传
3. **记录**：标记章节为已上传

## 检查规范（quality checks）

系统对每个生成的章节执行以下检查：

1. **与大纲的符合度**：内容是否符合全文大纲和上下文大纲
2. **逻辑连贯性**：是否存在逻辑错误或前后矛盾
3. **人物一致性**：角色是否符合设定，行为是否一致
4. **语法质量**：是否存在语法错误，表达是否清晰
5. **章节匹配度**：内容是否与章节目的相符

## 高级用法

### 自定义配置生成

编辑 `src/config.py` 调整参数：

```python
# 提高大纲质量（更多迭代次数）
OUTLINE_ITERATIONS = 5

# 更长的上下文（保持更好的连贯性）
Y_CHAPTERS = 10

# 更严格的质量检查
TEXT_CHECK_ITERATIONS = 3
```

### 恢复长时间中断的写作

```bash
# 检查当前进度
python src/main.py --check ./book/mybook

# 从第8章继续，写10章
python src/main.py --resume ./book/mybook --start-chapter 8 --chapters 10
```

### 仅做阶段检查

```bash
# 检查一个已有书籍的状态
python src/main.py --check /path/to/book
```

## 常见问题

### Q: API密钥怎样配置？
A: 在项目根目录创建 `.env` 文件，编写 `api_key=your_key_here` 即可。

### Q: 一次命令可以生成多少章？
A: 默认10章，可通过 `--chapters` 参数修改。建议一次10-20章以保持稳定性。

### Q: 生成中出错怎么办？
A: 
1. 检查API密钥是否正确
2. 检查网络连接
3. 检查API余额是否充足
4. 使用 `--resume` 恢复中断的任务

### Q: 可以修改已生成的大纲吗？
A: 
- `Full_Outline.txt`：初始设定，不建议修改（会影响后续章节生成）
- `master_outline.txt`：优化版大纲，如需修改请同步修改对应的 Context 文件

### Q: 怎样导出最终成稿？
A: 所有章节文件位于 `book/书籍名称/Chapters/` 文件夹，可直接导入任何文本编辑器或发布平台。

## 性能优化建议

1. **减少迭代次数**：如果时间紧张，降低 `OUTLINE_ITERATIONS` 和 `TEXT_CHECK_ITERATIONS`
2. **减少上下文**：降低 `Y_CHAPTERS` 值可加快生成速度（但可能影响连贯性）
3. **批量处理**：分多次运行，每次10-15章，避免长时间占用API连接

## 许可证

MIT License

## 支持

如遇到问题，请检查：
1. API配置和连接
2. 磁盘空间充足
3. Python 版本 >= 3.7
4. 所有依赖包已安装
