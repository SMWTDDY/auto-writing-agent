"""
阶段三：发布
- 监控已完成章节
- 异步上传到平台
- 标记上传状态
"""

from pathlib import Path
from utils import FileManager, Logger
from config import UPLOAD_THRESHOLD, get_book_subdirs


class PublishManager:
    """发布管理器"""
    
    def __init__(self, book_folder: str):
        self.book_folder = Path(book_folder)
        
        # 使用get_book_subdirs获取各个子目录
        subdirs = get_book_subdirs(self.book_folder)
        self.chapters_dir = subdirs['chapters']
        
        self.file_manager = FileManager()
        self.status_file = self.book_folder / "publish_status.json"
    
    def get_completed_chapters(self) -> list:
        """
        获取已完成的章节列表
        
        Returns:
            已完成章节编号列表
        """
        chapters = []
        
        if self.chapters_dir.exists():
            for chapter_file in sorted(self.chapters_dir.glob("Chapter_*.txt")):
                chapter_num = int(chapter_file.stem.split('_')[1])
                chapters.append(chapter_num)
        
        return sorted(chapters)
    
    def get_uploaded_chapters(self) -> set:
        """
        获取已上传的章节集合
        
        Returns:
            已上传章节编号的集合
        """
        # 这里可以读取上传状态文件
        # 简化实现：暂时返回空集
        return set()
    
    def get_pending_upload(self) -> list:
        """
        获取待上传的章节
        
        Returns:
            待上传章节编号列表
        """
        completed = set(self.get_completed_chapters())
        uploaded = self.get_uploaded_chapters()
        pending = sorted(list(completed - uploaded))
        
        return pending
    
    def upload_chapter(self, chapter_num: int) -> dict:
        """
        上传单个章节
        
        Args:
            chapter_num: 章节编号
        
        Returns:
            上传结果字典
        """
        chapter_file = self.chapters_dir / f"Chapter_{chapter_num}.txt"
        
        if not chapter_file.exists():
            return {
                "success": False,
                "chapter_num": chapter_num,
                "error": "章节文件不存在"
            }
        
        try:
            content = self.file_manager.read_file(str(chapter_file))
            
            # TODO: 实现实际的上传逻辑
            # 这里应该调用平台API进行上传
            # 示例：upload_to_platform(content, chapter_num)
            
            Logger.log(f"✓ Chapter {chapter_num} 已上传 (字数: {len(content)})")
            
            return {
                "success": True,
                "chapter_num": chapter_num,
                "content_length": len(content),
                "timestamp": str(Path(chapter_file).stat().st_mtime)
            }
        
        except Exception as e:
            Logger.log(f"✗ Chapter {chapter_num} 上传失败: {e}", "ERROR")
            return {
                "success": False,
                "chapter_num": chapter_num,
                "error": str(e)
            }
    
    def mark_uploaded(self, chapter_num: int) -> bool:
        """
        标记章节为已上传
        
        Args:
            chapter_num: 章节编号
        
        Returns:
            是否标记成功
        """
        # TODO: 实现状态持久化
        return True
    
    def monitor_and_publish(self) -> dict:
        """
        监控已完成的章节并自动上传
        
        Returns:
            发布结果字典
        """
        Logger.log_stage("监控与发布", "检查待上传章节")
        
        pending = self.get_pending_upload()
        
        Logger.log(f"待上传章节数: {len(pending)}")
        Logger.log(f"待上传章节: {pending}")
        
        results = []
        
        if len(pending) >= UPLOAD_THRESHOLD:
            Logger.log(f"已达到上传阈值 ({UPLOAD_THRESHOLD}), 开始上传")
            
            # 从最早的章节开始上传
            for chapter_num in pending[:UPLOAD_THRESHOLD]:
                result = self.upload_chapter(chapter_num)
                results.append(result)
                
                if result["success"]:
                    self.mark_uploaded(chapter_num)
        else:
            Logger.log(f"待上传章节数未达阈值，暂不上传")
        
        return {
            "success": True,
            "pending_count": len(pending),
            "uploaded_count": len([r for r in results if r.get("success")]),
            "results": results
        }
    
    def run(self) -> dict:
        """
        执行阶段三：发布
        
        Returns:
            执行结果字典
        """
        Logger.log_stage("阶段三", "发布处理")
        
        result = self.monitor_and_publish()
        
        Logger.log_stage("阶段三", "✓ 完成")
        
        return result
    
    def get_statistics(self) -> dict:
        """
        获取发布统计信息
        
        Returns:
            统计信息字典
        """
        completed = self.get_completed_chapters()
        uploaded = self.get_uploaded_chapters()
        pending = self.get_pending_upload()
        
        return {
            "total_completed": len(completed),
            "total_uploaded": len(uploaded),
            "pending_upload": len(pending),
            "completed_chapters": completed,
            "pending_chapters": pending
        }


def run_stage3(book_folder: str):
    """运行阶段三"""
    manager = PublishManager(book_folder)
    return manager.run()


def check_publish_status(book_folder: str) -> dict:
    """检查发布状态"""
    manager = PublishManager(book_folder)
    return manager.get_statistics()
