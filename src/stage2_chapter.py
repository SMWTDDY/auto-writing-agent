"""
阶段二：章节迭代创作
- 循环生成每一章节
- 准备上下文
- 生成正文
- 质量审计
- 持久化存储
"""
import json
import re
from pathlib import Path
from utils import FileManager, AIClient, Logger, ContextManager
from config import (
    X_CHAPTERS, Y_CHAPTERS, TEXT_CHECK_ITERATIONS, get_book_subdirs
)


class ChapterGenerator:
    """章节生成器"""
    
    def __init__(self, book_folder: str, full_outline: str):
        self.book_folder = Path(book_folder)
        self.full_outline = full_outline
        self.ai_client = AIClient()
        self.file_manager = FileManager()
        
        # 使用get_book_subdirs获取各个子目录
        subdirs = get_book_subdirs(self.book_folder)
        self.chapters_dir = subdirs['chapters']
        self.context_dir = subdirs['context']
        
        self.context_manager = ContextManager(str(self.context_dir))
    
    def _initialize_check_specs(self):
        """初始化检查规范文件"""
        if not self.check_specs_file.exists():
            check_specs_content = """质量检查标准
                    1. 与大纲的符合度
                    - 章节内容是否与全文大纲一致
                    - 是否偏离原定的剧情设定

                    2. 逻辑连贯性和矛盾检查
                    - 情节逻辑是否通顺
                    - 时间线是否有矛盾
                    - 因果关系是否合理

                    3. 人物一致性
                    - 人物性格是否保持一致
                    - 人物的对话风格是否符合
                    - 人物的行为动机是否合理

                    4. 语法和表达清晰度
                    - 是否有明显的语病或错别字
                    - 句子结构是否清晰
                    - 段落划分是否合理

                    5. 章节标题与内容匹配度
                    - 标题是否准确反映章节内容
                    - 标题是否具有吸引力"""
                                
            self.file_manager.write_file(str(self.check_specs_file), check_specs_content)
    
    def prepare_context(self, chapter_num: int) -> dict:
        """
        准备上下文
        
        Args:
            chapter_num: 章节编号
        
        Returns:
            包含上下文信息的字典
        """
        context = {
            "full_outline": self.full_outline,
            "previous_chapters": [],
            "context_outline": "",
            "x": X_CHAPTERS,
            "y": Y_CHAPTERS
        }
        
        if chapter_num == 1:
            # 第一章：只有全文大纲
            Logger.log(f"第一章特殊处理，仅使用全文大纲")
        else:
            # 非第一章：加载前面的章节和上下文
            # 加载前x章的全文内容
            for i in range(max(1, chapter_num - (X_CHAPTERS)), chapter_num):
                chapter_file = self.chapters_dir / f"Chapter_{i}.txt"
                if chapter_file.exists():
                    content = self.file_manager.read_file(str(chapter_file))
                    context["previous_chapters"].append({
                        "num": i,
                        "content": content
                    })
            # 加载上一章的上下文大纲
            prev_context_file = self.context_dir / f"Context_{chapter_num - 1}.txt"
            if prev_context_file.exists():
                context["context_outline"] = self.file_manager.read_file(str(prev_context_file))  
        return context
    
    def update_context_outline(self, chapter_num: int, chapter_content: str, context: dict) -> str:
        """
        根据新生成的章节内容更新上下文大纲
        
        Args:
            chapter_num: 章节编号
            chapter_content: 上一章章节内容，用于更新上一章的上下文大纲
            context: 当前上下文
        
        Returns:
            更新后的上下文大纲
        """
        prompt = f"""根据以下信息生成第 {chapter_num} 章的上下文大纲。
                【全文大纲】
                {context['full_outline']}

                【上一章内容】
                {chapter_content}

                【上一章的上下文大纲】（如果有）
                {context.get('context_outline', '无')}

                请生成包含以下三个部分的上下文大纲（如果有上一章上下文大纲，则在上一章的上下文大纲进行修改）：

                1. 【长期记忆】
                提取这一章中的重要人物设定、重要设定等信息，对上下文大纲进行补充和修正，形成长期记忆部分，如果没有则不需要改动

                2. 【中期摘要 + 局部剧情】
                总结最近上一章的核心剧情发展，对上一章上下文大纲的此部分进行修改，保留时间线较近、剧情更重要的部分

                3. 【未来剧情发展大纲】
                根据全文大纲和当前进展，修正未来剧情方向

                请确保上下文大纲与全文大纲和前文内容的一致性。"""
        
        Logger.log(f"正在更新第 {chapter_num} 章的上下文大纲...")
        new_context = self.ai_client.generate_text(prompt, max_tokens=20000)
        
        return new_context
    
    def generate_chapter_content(self, chapter_num: int, context: dict) -> tuple:
        """
        生成章节正文和标题
        
        Args:
            chapter_num: 章节编号
            context: 上下文字典
        
        Returns:
            (标题, 正文内容) 元组
        """
        system_prompt = """你是一位网络文学创作大师，擅长驾驭叙事节奏、营造沉浸式阅读体验。
                        你的专长：
                        - 叙事节奏：精准控制铺垫、冲突、高潮的节奏
                        - 人物刻画：通过行动、对话、心理活动展现人物
                        - 世界沉浸：细节描写让读者仿佛身临其境
                        - 情感共鸣：引发读者的情感共鸣和思考
                        - 爽点设计：合理安排满足感和期待感的节奏

                        你注重：每个场景都有明确的目的；每个对话都推动角色关系或情节；描写既要生动又要精炼;
                        """
        # 构建提示词
        previous_context = ""
        if context["previous_chapters"]:
            previous_context = "\n【前面的章节内容】\n"
            for ch in context["previous_chapters"]:
                previous_context += f"(Chapter {ch['num']} 片段)\n{ch['content']}\n\n"
        
        prompt = f"""请根据以下信息生成小说第 {chapter_num} 章的内容。

                【全文大纲】
                {context['full_outline']}

                【上下文大纲】
                {context.get('context_outline', '根据全文大纲生成此章')}

                {previous_context}

                【写作要求】

                【字数与长度】
                - 字数：至少3000字以上尽量不要超过5000字
                - 篇幅充足，充分展现故事和人物

                【内容质量】
                - 与大纲保持高度一致，不得偏离核心设定
                - 保持与前文的连贯性和细节一致性
                - 避免逻辑矛盾和时间线混乱
                - 人物行为、性格、对话必须符合既定设定

                【叙事风格】
                - 节奏要有张有弛，避免单调
                - 在关键情节处设置张力和悬念
                - 适当融入环境描写和人物心理
                - 对话要推动情节或表现人物

                【情节深度】
                - 情节发展饱满曲折，多展现人物魅力和世界观
                - 融入伏笔或细节呼应
                - 展现人物的内心活动和成长
                - 若有冲突，要展现角色不同的理念或立场

                【表达质量】
                - 文笔流畅自然，避免生硬
                - 表达清晰，避免歧义
                - 恰当使用修辞，增强表现力

                【输出格式】
                请以以下格式返回：
                【标题】一个简洁有吸引力的章节标题 （例如  第x章 xxxxx）
                【正文】
                实际的正文内容
                """
        
        Logger.log(f"正在生成第 {chapter_num} 章...")
        response = self.ai_client.generate_text(prompt, max_tokens=20000, system_prompt=system_prompt)
        
        # 解析 AI 的响应
        title = ""
        content = response
        
        if "【标题】" in response and "【正文】" in response:
            try:
                title_start = response.find("【标题】") + 4
                title_end = response.find("\n", title_start)
                if title_end == -1:
                    title_end = response.find("【正文】", title_start)
                title = response[title_start:title_end].strip()
                
                content_start = response.find("【正文】") + 4
                content = response[content_start:].strip()
            except:
                pass
        
        # 如果没有成功解析，使用默认标题
        if not title:
            title = f"第 {chapter_num} 章"
        
        return title, content
    
    def check_chapter_quality(self, chapter_num: int, chapter_content: str) -> dict:
        """
        质量审计：检查章节质量
        """
        check_specs = """检查以下方面：
                        1. 字数：必须3000字以上（不合格如果少于3000字），尽量5000字以内，超过扣分
                        2. 与大纲的符合度
                        3. 逻辑连贯性和矛盾检查
                        4. 人物一致性
                        5. 语法和表达清晰度
                        6. 章节标题与内容匹配度"""
        
        prompt = f"""请对以下第 {chapter_num} 章的内容进行质量审计。
                【检查标准】
                {check_specs}

                【章节内容】
                {chapter_content}

                【全文大纲】
                {self.full_outline}

                请以JSON格式返回评估结果，包含：
                - is_qualified: 是否通过审计（true/false，如果字数少于3000字必须为false）
                - score: 总体评分（0-100）
                - issues: 主要问题列表（数组，如字数不足要明确指出）
                - suggestions: 改进建议列表（数组）
                例如：
                {{"is_qualified": false,
                "score": 85,
                "issues": [
                    "字数不足3000字（当前字数：2800字）",
                    "部分段落逻辑衔接不自然"
                ],
                "suggestions": [
                    "扩充内容至3000字以上，补充具体案例支撑观点",
                    "优化段落过渡语句，提升内容连贯性"
                ]}}
                或
                                {{
                "is_qualified": true,
                "score": 88,
                "issues": [
                    "无明显核心问题"
                ],
                "suggestions": [
                    "可适当精简冗余表述，提升内容紧凑度",
                    "补充1-2个最新案例，增强时效性"
                ]}}
                
                如果评分低于70分或字数不足，请标记为不合格。"""
                
        raw_response = self.ai_client.generate_text(prompt, check_specs)
        # 尝试解析 JSON
        try:
            # 步骤1：提取AI返回中的JSON内容（兼容多种格式）
            json_str = raw_response
            # 优先匹配```json ... ```格式
            if "```json" in raw_response:
                json_match = re.search(r"```json\s*(.*?)\s*```", raw_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
            # 其次匹配``` ... ```格式
            elif "```" in raw_response:
                json_match = re.search(r"```\s*(.*?)\s*```", raw_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
            # 最后兜底匹配{}包裹的JSON内容（防止AI只返回JSON但无代码块）
            else:
                json_match = re.search(r"\{[\s\S]*\}", raw_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)

            # 步骤2：解析JSON并强制校验规则
            audit_result = json.loads(json_str.strip())

            # 强制校验字段类型，确保格式正确
            # 1. 处理is_qualified：严格遵循「字数不足/评分<70 → false」
            score = audit_result.get("score", 0)
            # 检查issues中是否包含"字数不足3000字"
            has_word_count_issue = any("字数不足3000字" in issue for issue in audit_result.get("issues", []))
            # 强制重置is_qualified
            audit_result["is_qualified"] = False if (has_word_count_issue or score < 70) else True

            # 2. 处理score：确保是0-100的数字
            if not isinstance(audit_result["score"], (int, float)) or audit_result["score"] < 0 or audit_result["score"] > 100:
                audit_result["score"] = 0  # 非法值重置为0

            # 3. 处理issues：确保是列表
            if not isinstance(audit_result.get("issues"), list):
                audit_result["issues"] = ["返回的问题列表格式异常"]

            # 4. 处理suggestions：确保是列表
            if not isinstance(audit_result.get("suggestions"), list):
                audit_result["suggestions"] = ["请根据检查标准优化章节内容"]

            return audit_result

        except Exception as e:
            Logger.log(f"解析审计结果失败: {e}", "ERROR")
            # 失败时返回默认字典，确保后续逻辑不崩溃
            return {
                "is_qualified": False, 
                "score": 0, 
                "issues": ["JSON 解析失败，强制重写"], 
                "suggestions": []
            }
    
    def revise_chapter(self, chapter_num: int, chapter_content: str, issues: list) -> str:
        """
        根据审计结果重写章节
        
        Args:
            chapter_num: 章节编号
            chapter_content: 原章节内容
            issues: 问题列表
        
        Returns:
            重写后的章节内容
        """
        prompt = f"""请根据以下问题对第 {chapter_num} 章的内容进行针对性修改。

                【核心问题】
                {chr(10).join(f'- {issue}' for issue in issues)}

                【原章节内容】
                {chapter_content}

                【全文大纲】
                {self.full_outline}

                请重新撰写这一章，解决上述问题，保持字数在3000字以上。
                直接输出修改后的章节正文。"""
        
        Logger.log(f"第 {chapter_num} 章未通过审计，正在重写...")
        revised_content = self.ai_client.generate_text(prompt, max_tokens=20000)
        
        return revised_content
    
    def save_chapter(self, chapter_num: int, title: str, chapter_content: str) -> bool:
        """
        保存章节内容到文件
        
        Args:
            chapter_num: 章节编号
            title: 章节标题
            chapter_content: 章节内容
        
        Returns:
            是否保存成功
        """
        # 格式化输出：标题 + 正文
        formatted_content = f"{title}\n\n{chapter_content}"
        
        filepath = self.chapters_dir / f"Chapter_{chapter_num}.txt"
        success = self.file_manager.write_file(str(filepath), formatted_content)
        
        if success:
            Logger.log(f"✓ Chapter {chapter_num} 已保存")
        else:
            Logger.log(f"✗ Chapter {chapter_num} 保存失败", "ERROR")
        
        return success
    
    def generate_chapter(self, chapter_num: int) -> dict:
        """
        生成单个章节
        """
        Logger.log_chapter(chapter_num, "开始生成章节")
        
        # 1. 准备上下文 (返回 dict)
        context = self.prepare_context(chapter_num)
        
        # 修复1：获取上一章内容用于更新大纲。如果没有上一章，则传空字符串
        prev_chapter_content = ""
        if context.get("previous_chapters"):
            prev_chapter_content = context["previous_chapters"][-1]["content"]
            
        # 2. 利用上一章内容更新上下文大纲
        # 修复2：不要用字符串覆写 context 字典，而是更新其中的 'context_outline' 字段
        updated_outline_text = self.update_context_outline(chapter_num, prev_chapter_content, context)
        context["context_outline"] = updated_outline_text
        
        # 保存上下文大纲（存字符串）
        self.context_manager.save_context(chapter_num, updated_outline_text)
        
        # 3. 生成正文和标题 (此时 context 依然是包含完整信息的 dict)
        title, chapter_content = self.generate_chapter_content(chapter_num, context)
        
        # 4. 质量审计与迭代
        for check_round in range(1, TEXT_CHECK_ITERATIONS + 1):
            Logger.log(f"第 {check_round} 轮审计...")
            
            check_result = self.check_chapter_quality(chapter_num, chapter_content)
            
            if check_result.get("is_qualified", False):
                Logger.log(f"✓ 审计通过 (评分: {check_result.get('score', 'N/A')})")
                break
            else:
                Logger.log(f"✗ 审计未通过 (评分: {check_result.get('score', 'N/A')})")
                
                if check_round < TEXT_CHECK_ITERATIONS:
                    issues = check_result.get("issues", [])
                    if issues:
                        chapter_content = self.revise_chapter(chapter_num, chapter_content, issues)
                    else:
                        Logger.log("无法获取具体问题，跳过重写", "WARNING")
                        break
        
        # 5. 保存章节
        self.save_chapter(chapter_num, title, chapter_content)
        
        Logger.log_chapter(chapter_num, "✓ 生成完成")
        
        return {
            "success": True,
            "chapter_num": chapter_num,
            "content_length": len(chapter_content),
            "quality_check": check_result
        }
    
    #判断是否可以进入结局阶段
    def should_enter_ending(self, current_chapter: int) -> bool:
        prompt = f"""根据以下大纲，当前已经写到第 {current_chapter} 章。
                【全文大纲】
                {self.full_outline}

                请判断：现在是否已经充分铺垫和发展，可以开始进入故事的最终结局阶段？

                请简洁地回答：
                - 回答 '是' 或 '可以'，表示可以进入结局
                - 回答 '否' 或 '还需要'，表示还需要继续发展

                只需要返回一个词或短语，不需要解释。"""
        
        response = self.ai_client.generate_text(prompt, max_tokens=50).strip()
        
        # 检查响应中是否包含肯定的词汇
        positive_keywords = ['是', '可以', '好的', '同意', 'yes', 'ok', '完全可以', '可']
        is_ready = any(keyword in response.lower() for keyword in positive_keywords)
        
        Logger.log(f"AI判断是否可进入结局: {response} → {'可以' if is_ready else '还需要继续'}")
        
        return is_ready
    
    def run(self, start_chapter: int = 1, total_chapters: int = None) -> dict:
        """
        执行阶段二：章节迭代创作（自动完成模式）
        
        Args:
            start_chapter: 起始章节编号
            total_chapters: 参数已废弃（保留兼容性）
        
        Returns:
            执行结果字典
        
        工作流程：
        - 持续生成章节
        - 每10章问一次AI是否可以进入结局
        - 当AI同意进入结局时停止生成
        """
        Logger.log_stage("阶段二", "章节迭代创作（自动完成模式）")
        Logger.log("AI将持续写作，每10章检查一次是否可以进入结局...")
        
        results = []
        chapter_num = start_chapter
        chapters_since_check = 0
        
        # 无限循环，仅由AI的进入结局判断控制
        while True:
            result = self.generate_chapter(chapter_num)
            results.append(result)
            
            if not result.get("success"):
                Logger.log(f"✗ 第 {chapter_num} 章生成失败", "WARNING")
                break
            
            chapters_since_check += 1
            
            # 每10章检查一次是否可以进入结局
            if chapters_since_check >= 10:
                Logger.log(f"\n{'='*60}")
                Logger.log(f"已生成 {chapter_num} 章，检查是否可以进入结局...")
                Logger.log(f"{'='*60}")
                
                if self.should_enter_ending(chapter_num):
                    Logger.log(f"\n{'='*60}")
                    Logger.log(f"✓ 可以进入结局，开始生成最后的收尾章节...")
                    Logger.log(f"{'='*60}\n")
                    
                    # 继续生成直到AI认为完成为止
                    # 这里可以根据需要继续生成几章作为结局
                    while True:
                        result = self.generate_chapter(chapter_num + 1)
                        results.append(result)
                        
                        if not result.get("success"):
                            break
                        
                        chapter_num += 1
                        
                        # 询问当前章节是否是最终结局
                        final_check_prompt = f"""第 {chapter_num} 章已经完成。根据以下大纲：
                                            【全文大纲】
                                            {self.full_outline}
                                            这一章是否已经是故事的最终结局或大结局？请简洁回答'是'或'否'。"""
                        
                        final_response = self.ai_client.generate_text(final_check_prompt, max_tokens=20).strip()
                        
                        if any(kw in final_response.lower() for kw in ['是', '对', 'yes', '完', '结束']):
                            Logger.log(f"\n{'='*60}")
                            Logger.log(f"✓ 故事已达到最终结局！")
                            Logger.log(f"✓ 全书完成，共 {chapter_num} 章")
                            Logger.log(f"{'='*60}\n")
                            return {
                                "success": True,
                                "chapters_generated": len(results),
                                "final_chapter": chapter_num,
                                "results": results
                            }
                    break
                else:
                    Logger.log(f"继续生成更多章节...\n")
                    chapters_since_check = 0
            
            chapter_num += 1
        
        Logger.log_stage("阶段二", "✓ 完成")
        
        return {
            "success": True,
            "chapters_generated": len(results),
            "final_chapter": chapter_num,
            "results": results
        }


def run_stage2(book_folder: str, full_outline: str, chapters_count: int = 10, start_from: int = 1):
    """运行阶段二"""
    generator = ChapterGenerator(book_folder, full_outline)
    return generator.run(start_from, chapters_count)
