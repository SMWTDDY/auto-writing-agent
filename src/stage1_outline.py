"""
阶段一：初始化与大纲构建
- 根据主题创建书籍文件夹
- 生成初步大纲
- 迭代优化大纲
"""

from pathlib import Path
from datetime import datetime
from utils import FileManager, AIClient, Logger, ContextManager
from config import (
    BOOK_OUTPUT_DIR, create_book_structure, OUTLINE_ITERATIONS
)


class OutlineGenerator:
    """大纲生成器"""
    
    def __init__(self):
        self.ai_client = AIClient()
        self.file_manager = FileManager()
    
    def initialize_book_structure(self, theme: str, book_name: str = None) -> str:
        """
        初始化：根据主题创建书籍文件夹和子目录
        
        Args:
            theme: 书籍主题
            book_name: 书籍名称（如果为None，由AI生成）
        
        Returns:
            书籍文件夹路径
        """
        # 如果没有指定书籍名称，由AI生成
        if not book_name:
            prompt = f"根据以下主题生成一个简洁有趣的书籍名称：\n{theme}\n\n只返回书籍名称，不超过20个字符。"
            book_name = self.ai_client.generate_text(prompt).strip()
            
            if not book_name:
                raise Exception("无法生成书籍名称")
        
        # 使用config中的create_book_structure创建完整的书籍结构
        try:
            book_folder = create_book_structure(book_name)
            return str(book_folder)
        except Exception as e:
            Logger.log(f"✗ 创建书籍文件夹失败: {e}", "ERROR")
            raise
    
    def generate_initial_outline(self, theme: str, config: str = "") -> str:
        """
        生成初步大纲
        
        Args:
            theme: 书籍主题
            config: 额外的配置信息
        
        Returns:
            生成的大纲内容
        """
        system_prompt = """你是一位顶级畅销书编辑兼作家导师，拥有20年行业经验，精通网络文学与传统文学。你擅长策划爆款小说，能精准把握市场趋势、读者心理和叙事节奏。

你的核心能力：
- 故事结构：精通三幕剧、英雄之旅、黄金圈等经典结构
- 人物塑造：擅长创造立体、有缺陷、有成长弧线的角色
- 节奏控制：深谙爽点密集、悬念设置、情绪管理的技巧
- 市场洞察：了解各平台读者偏好和流行趋势

你的任务：创作一个完美的小说大纲，包含所有成功要素。"""
        
        prompt = f"""请为以下主题创作一个完美、完整、可直接投入创作的大纲。这个大纲需要达到专业出版/爆款网文的标准。

【主题】
{theme}

【额外设定】
{config if config else "无"}

大纲必须包含以下核心模块：

1. 【核心概念】
   - 一句话梗概（电梯游说）
   - 简短有力的故事核心

2. 【世界观体系】
   - 物理规则/超自然体系
   - 社会结构与权力关系
   - 力量体系（修炼/魔法/科技等）
   - 独特世界观设定（至少3个创新点）
   - 重要地点设定

3. 【主角团设定】
   - 主角：姓名、年龄、性格（核心特质+缺陷）、背景故事、内心冲突、成长弧线、特殊能力、核心动机
   - 主要配角：角色定位、与主角关系、叙事功能、个人故事线
   - 反派：反派级别、动机、核心理念、力量资源、与主角的特殊联系

4. 【故事主线】
   - 激励事件（打破平静的时刻）
   - 关键决定（主角的选择）
   - 中点转折（重大转折/伪胜利）
   - 至暗时刻（最大失败）
   - 高潮对决（最终对决）
   - 结局（尘埃落定、新平衡）

5. 【冲突体系】
   - 内部冲突（主角内心的矛盾）
   - 人际冲突（角色之间的对立）
   - 社会冲突（更大层面的对立）
   - 终极冲突（核心理念的碰撞）

6. 【创新亮点】
   - 概念创新点
   - 世界观创新点
   - 人物设定创新点
   - 情节设计创新点
   - 主题表达创新点

7. 【读者期待管理】
   - 开篇承诺（前3章给读者的预期）
   - 中期兑现（中段兑现的承诺）
   - 结局满足（必须满足的核心期待）
   - 意外惊喜（超出预期的亮点）

【特别要求】
1. 原创创意，避免抄袭现有作品
2. 创新点要具体、可执行，不是空泛描述
3. 人物必须有缺陷和成长空间，避免完美无缺
4. 冲突要有层次感，从个人到社会到理念
5. 节奏要有张有弛，爽点分布要合理
6. 伏笔精心设计，前后呼应
7. 结局既满足预期又出乎意料
8. 平衡商业性与艺术性
"""
        
        outline = self.ai_client.generate_text(prompt, max_tokens=20000, system_prompt=system_prompt)
        
        if not outline:
            raise Exception("无法生成初步大纲")
        
        return outline
    
    def iterate_outline(self, outline: str, iteration: int) -> str:
        """
        迭代优化大纲
        
        Args:
            outline: 当前大纲
            iteration: 迭代次数
        
        Returns:
            优化后的大纲
        """
        prompt = f"""请对以下大纲进行第 {iteration} 轮修改和优化。

【当前大纲】
{outline}

【检查标准】
1. 逻辑连贯性：各章节之间的因果关系是否清晰
2. 冲突设置：是否有足够的核心冲突来驱动故事发展
3. 人物发展：各主要人物是否有明确的成长或变化轨迹
4. 情节合理性：情节发展是否符合世界观和人物设定
5. 章节分布：是否合理安排了起承转合的章节分布

请直接返回改进后的完整大纲，保持原有的四部分结构。不需要输出改进说明或注释。"""
        
        improved_outline = self.ai_client.generate_text(prompt, max_tokens=20000)
        
        if not improved_outline:
            return outline  # 返回原大纲而不中断
        
        return improved_outline
    
    def save_outline(self, book_folder: str, outline: str) -> bool:
        """
        保存大纲为 master_outline.txt
        
        Args:
            book_folder: 书籍文件夹路径
            outline: 大纲内容
        
        Returns:
            是否保存成功
        """
        filename = "master_outline.txt"
        filepath = Path(book_folder) / "Outline" / filename
        
        success = self.file_manager.write_file(str(filepath), outline)
        
        if success:
            Logger.log(f"✓ 大纲已保存")
        else:
            Logger.log(f"✗ 大纲保存失败", "ERROR")
        
        return success
    
    def run(self, theme: str, config: str = "", book_name: str = None) -> dict:
        """
        执行阶段一：初始化与大纲构建
        
        Args:
            theme: 书籍主题
            config: 额外配置
            book_name: 书籍名称
        
        Returns:
            包含生成结果的字典
        """
        Logger.log_stage("阶段一", "初始化与大纲构建")
        
        try:
            # 初始化书籍结构
            book_folder = self.initialize_book_structure(theme, book_name)
            
            # 生成初步大纲
            outline = self.generate_initial_outline(theme, config)
            
            # 迭代优化大纲
            for i in range(1, OUTLINE_ITERATIONS + 1):
                outline = self.iterate_outline(outline, i)
            
            # 保存最终大纲
            self.save_outline(book_folder, outline)
            
            Logger.log_stage("阶段一", "✓ 完成")
            
            return {
                "success": True,
                "book_folder": book_folder,
                "outline": outline,
                "book_name": Path(book_folder).name
            }
        
        except Exception as e:
            Logger.log(f"✗ 阶段一执行失败: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }


def run_stage1(theme: str, config: str = "", book_name: str = None):
    """运行阶段一"""
    generator = OutlineGenerator()
    return generator.run(theme, config, book_name)
