"""
自动写作代理 - 主程序入口
根据规范自动生成完整的网络小说

使用方式：
    python main.py --theme "主题" [--name "书籍名称"] [--chapters 10] [--stage 1]
"""

from pathlib import Path
import argparse
from stage1_outline import run_stage1
from stage2_chapter import run_stage2
from stage3_publish import run_stage3, check_publish_status
from utils import FileManager, Logger
from config import BOOK_OUTPUT_DIR


def read_theme_from_file(filepath: str) -> str:
    """
    从文件中读取主题内容
    支持相对路径（在/theme/目录中）和绝对路径
    
    Args:
        filepath: 文件路径（如 "theme/my_theme.txt" 或绝对路径）
    
    Returns:
        主题内容字符串
    
    Raises:
        FileNotFoundError: 文件不存在时
        Exception: 读取文件失败时
    """
    try:
        path = Path(filepath)
        
        # 如果是相对路径，检查是否需要加上theme前缀
        if not path.is_absolute():
            # 如果不以 'theme/' 开头，自动加上
            if not str(path).startswith('theme'):
                path = Path('theme') / filepath
        
        # 检查文件是否存在
        if not path.exists():
            # 如果不存在，尝试加上 .txt 扩展名
            if path.suffix == '':
                path = path.with_suffix('.txt')
            
            if not path.exists():
                raise FileNotFoundError(f"主题文件不存在: {filepath}")
        
        # 读取文件内容
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            raise ValueError(f"主题文件为空: {path}")
        
        Logger.log(f"成功读取主题文件: {path}")
        return content
        
    except Exception as e:
        Logger.log(f"读取主题文件失败: {str(e)}", "ERROR")
        raise


def list_available_themes() -> None:
    """
    列出/theme/目录下所有可用的主题文件
    """
    theme_dir = Path('theme')
    
    if not theme_dir.exists():
        Logger.log("主题目录不存在: ./theme/", "WARNING")
        Logger.log("请创建 theme/ 目录并添加主题文件", "WARNING")
        return
    
    # 查找所有 .txt 文件
    theme_files = sorted(theme_dir.glob('*.txt'))
    
    if not theme_files:
        Logger.log("主题目录为空，未找到任何主题文件", "WARNING")
        return
    
    Logger.log(f"\n{'='*60}")
    Logger.log("可用的主题文件:")
    Logger.log(f"{'='*60}")
    
    for idx, theme_file in enumerate(theme_files, 1):
        filename = theme_file.name
        # 读取文件第一行作为描述
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                description = first_line[:60] + '...' if len(first_line) > 60 else first_line
        except:
            description = "(无法读取)"
        
        Logger.log(f"\n{idx}. {filename}")
        Logger.log(f"   描述: {description}")
        Logger.log(f"   路径: theme/{filename}")
    
    Logger.log(f"\n{'='*60}")
    Logger.log("使用方式:")
    Logger.log(f"  python main.py --theme-file theme/filename.txt -c 10")
    Logger.log(f"{'='*60}\n")


class AutoWritingAgent:
    """自动写作代理主类"""
    
    def __init__(self):
        self.file_manager = FileManager()
    
    def run_full_pipeline(self, theme: str, book_name: str = None, chapters_count: int = 10, target_stage: int = None):
        """
        执行指定阶段的流程
        
        Args:
            theme: 书籍主题
            book_name: 书籍名称
            chapters_count: 章节数
            target_stage: 目标阶段（1/2/3，None表示全部）
        """
        try:
            # 阶段一：大纲构建
            if target_stage is None or target_stage == 1:
                Logger.log("\n" + "="*60)
                Logger.log("阶段一：初始化与大纲构建")
                Logger.log("="*60)
                
                stage1_result = run_stage1(theme, "", book_name)
                
                if not stage1_result.get("success"):
                    error_msg = stage1_result.get("error", "未知错误")
                    Logger.log(f"阶段一失败: {error_msg}", "ERROR")
                    Logger.log("已在上方输出详细错误信息，请检查", "ERROR")
                    return False
                
                book_folder = stage1_result["book_folder"]
                outline = stage1_result["outline"]
                book_name = stage1_result["book_name"]
                
                Logger.log(f"\n✓ 阶段一完成")
            
            if target_stage == 1:
                return True
            
            # 阶段二：章节创作
            if target_stage is None or target_stage == 2:
                Logger.log("\n" + "="*60)
                Logger.log("阶段二：章节迭代创作")
                Logger.log("="*60)
                
                stage2_result = run_stage2(book_folder, outline, chapters_count, start_from=1)
                
                if not stage2_result.get("success"):
                    Logger.log("阶段二失败，将尝试继续发布已完成的章节", "WARNING")
                else:
                    Logger.log(f"\n✓ 阶段二完成")
                    Logger.log(f"已生成章节数: {stage2_result['chapters_generated']}")
            
            if target_stage == 2:
                return True
            
            # 阶段三：发布
            if target_stage is None or target_stage == 3:
                Logger.log("\n" + "="*60)
                Logger.log("阶段三：发布处理")
                Logger.log("="*60)
                
                stage3_result = run_stage3(book_folder)
                
                if stage3_result.get("success"):
                    Logger.log(f"\n✓ 阶段三完成")
                    Logger.log(f"已上传章节: {stage3_result['uploaded_count']}")
                    Logger.log(f"待上传章节: {stage3_result['pending_count']}")
            
            Logger.log("\n" + "="*60)
            Logger.log("✓ 流程完成！")
            Logger.log("="*60)
            
            return True
        
        except Exception as e:
            Logger.log(f"\n✗ 执行过程中出错: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    def continue_writing(self, book_folder: str, chapter_start: int, chapter_count: int):
        """
        继续写作（用于阶段二中断后的恢复）
        
        Args:
            book_folder: 书籍文件夹路径
            chapter_start: 起始章节编号
            chapter_count: 要生成的章节数
        """
        Logger.log("="*60)
        Logger.log(f"恢复写作模式")
        Logger.log(f"书籍: {book_folder}")
        Logger.log(f"起始章节: {chapter_start}")
        Logger.log(f"计划章节数: {chapter_count}")
        Logger.log("="*60)
        
        try:
            # 读取已保存的大纲
            outline_file = Path(book_folder) / "Outline" / "master_outline.txt"
            if not outline_file.exists():
                outline_file = Path(book_folder) / "Outline" / "Full_Outline.txt"
            
            if not outline_file.exists():
                Logger.log("找不到大纲文件，无法继续写作", "ERROR")
                return False
            
            outline = self.file_manager.read_file(str(outline_file))
            
            # 继续阶段二
            stage2_result = run_stage2(book_folder, outline, chapter_count, chapter_start)
            
            # 执行阶段三
            stage3_result = run_stage3(book_folder)
            
            Logger.log("\n" + "="*60)
            Logger.log(f"✓ 恢复完成")
            Logger.log(f"已生成章节: {stage2_result['chapters_generated']}")
            Logger.log(f"已上传章节: {stage3_result.get('uploaded_count', 0)}")
            Logger.log("="*60)
            
            return True
        
        except Exception as e:
            Logger.log(f"\n✗ 执行过程中出错: {e}", "ERROR")
            return False
    
    def check_status(self, book_folder: str):
        """
        检查书籍的创作状态
        
        Args:
            book_folder: 书籍文件夹路径
        """
        Logger.log("="*60)
        Logger.log(f"书籍状态检查: {book_folder}")
        Logger.log("="*60)
        
        try:
            stats = check_publish_status(book_folder)
            
            Logger.log(f"已完成章节: {stats['total_completed']}")
            Logger.log(f"  详情: {stats['completed_chapters']}")
            Logger.log(f"已上传章节: {stats['total_uploaded']}")
            Logger.log(f"待上传章节: {stats['pending_upload']}")
            Logger.log(f"  详情: {stats['pending_chapters']}")
            
            return stats
        
        except Exception as e:
            Logger.log(f"✗ 检查失败: {e}", "ERROR")
            return None


def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(
        description="自动写作代理 - 自动生成网络小说"
    )
    
    parser.add_argument(
        "--theme", "-t",
        type=str,
        required=False,
        help="书籍主题"
    )
    
    parser.add_argument(
        "--theme-file", "-tf",
        type=str,
        default=None,
        help="从文件读取主题（指定文件路径或theme/目录中的文件名）"
    )
    
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="列出theme/目录中的所有可用主题文件"
    )
    
    parser.add_argument(
        "--name", "-n",
        type=str,
        nargs='?',
        const='',
        default=None,
        help="书籍名称（如不指定则由AI生成）"
    )
    
    parser.add_argument(
        "--chapters", "-c",
        type=int,
        default=10,
        help="计划生成的章节数（默认10）"
    )
    
    parser.add_argument(
        "--stage", "-s",
        type=int,
        choices=[1, 2, 3],
        default=1,
        help="执行的阶段（1=大纲，2=创作，3=发布，默认执行全部）"
    )
    
    parser.add_argument(
        "--resume",
        type=str,
        default=None,
        help="恢复写作，指定书籍文件夹路径"
    )
    
    parser.add_argument(
        "--start-chapter",
        type=int,
        default=1,
        help="恢复写作的起始章节"
    )
    
    parser.add_argument(
        "--check",
        type=str,
        default=None,
        help="检查创作状态，指定书籍文件夹路径"
    )
    
    args = parser.parse_args()
    
    agent = AutoWritingAgent()
    
    # 列出可用主题
    if args.list_themes:
        list_available_themes()
        return
    
    # 从文件读取主题
    theme = args.theme
    if args.theme_file:
        theme = read_theme_from_file(args.theme_file)
        if not theme:
            return
    
    # 检查模式
    if args.check:
        agent.check_status(args.check)
        return
    
    # 恢复模式
    if args.resume:
        agent.continue_writing(args.resume, args.start_chapter, args.chapters)
        return
    
    # 正常模式
    if not theme:
        parser.print_help()
        print("\n执行示例:")
        print('  python main.py --theme "网络文学主题" --chapters 10')
        print('  python main.py -t "悬疑推理小说" -n "密室谜案" -c 20')
        print('  python main.py --theme-file theme/my_theme.txt -c 10')
        print('  python main.py --list-themes')
        return
    
    agent.run_full_pipeline(theme, args.name, args.chapters, target_stage=args.stage)


if __name__ == "__main__":
    main()
