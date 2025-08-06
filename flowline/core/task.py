import threading
import queue
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from flowline.utils import Log

logger = Log(__name__)

Base = declarative_base()


class TaskStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"


class TaskModel(Base):
    """SQLAlchemy模型类，对应数据库中的task表"""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    cmd = Column(Text, nullable=False)
    run_num = Column(Integer, default=0, nullable=False)
    need_run_num = Column(Integer, default=1, nullable=False)
    config_dict = Column(JSON, nullable=True)  # 存储配置字典
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def status(self) -> str:
        """计算任务状态"""
        return TaskStatus.COMPLETED if self.run_num >= self.need_run_num else TaskStatus.PENDING
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "task_id": self.id,
            "dict": str(self.config_dict or {}),
            "run_num": self.run_num,
            "need_run_num": self.need_run_num,
            "name": self.name,
            "cmd": self.cmd,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Task:
    """任务包装类，保持与原有接口的兼容性"""
    def __init__(self, task_model: TaskModel):
        self._model = task_model
        
    @property
    def task_id(self) -> int:
        return self._model.id
    
    @property
    def dict(self) -> Dict[str, Any]:
        return self._model.config_dict or {}
    
    @property
    def config_dict(self) -> Dict[str, Any]:
        return self._model.config_dict or {}
    
    @property
    def run_num(self) -> int:
        return self._model.run_num
    
    @property
    def need_run_num(self) -> int:
        return self._model.need_run_num
    
    @property
    def name(self) -> str:
        return self._model.name
    
    @property
    def cmd(self) -> str:
        return self._model.cmd
    
    @property
    def state(self) -> str:
        return self._model.status

    def __str__(self) -> str:
        return f"Task:{self.task_id}"
    
    def get_dict(self) -> Dict[str, Any]:
        return self._model.to_dict()

class TaskManager:
    """
    任务管理器，使用SQLAlchemy ORM管理任务数据
    """
    def __init__(self, db_path: str = "tasks.db"):
        self._lock = threading.Lock()
        self.db_path = db_path
        
        # 创建数据库引擎和会话
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # 内存中的任务队列
        self.task_ids = queue.PriorityQueue()
        
        # 初始化任务队列
        self._initialize_task_queue()
        
        logger.info(f"TaskManager initialized with database: {db_path}")

    def _get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()

    def _initialize_task_queue(self):
        """初始化任务队列，将未完成的任务加入队列"""
        with self._get_session() as session:
            pending_tasks = session.query(TaskModel).filter(
                TaskModel.run_num < TaskModel.need_run_num
            ).all()
            
            for task in pending_tasks:
                remaining_runs = task.need_run_num - task.run_num
                for _ in range(remaining_runs):
                    self.task_ids.put(task.id)
                    
        logger.info(f"Initialized task queue with {self.task_ids.qsize()} pending task runs")

    def synchronized(func):
        """同步装饰器"""
        def wrapper(self, *args, **kwargs):
            with self._lock:
                return func(self, *args, **kwargs)
        return wrapper
    
    # -------------------------------
    
    def get_task_dict(self) -> List[Dict[str, Any]]:
        """获取所有任务的字典列表"""
        with self._get_session() as session:
            tasks = session.query(TaskModel).all()
            return [task.to_dict() for task in tasks]
    
    @synchronized
    def get_next_task(self) -> Optional[Task]:
        """获取下一个待执行的任务"""
        while not self.task_ids.empty():
            task_id = self.task_ids.get()
            
            with self._get_session() as session:
                task_model = session.query(TaskModel).filter(TaskModel.id == task_id).first()
                if task_model is None:
                    logger.warning(f"Task {task_id} not found in database")
                    continue
                
                # 检查任务是否已完成
                if task_model.run_num >= task_model.need_run_num:
                    logger.info(f"Task {task_id} is already completed, skipping")
                    continue
                    
                logger.info(f"get task {task_id} config: {task_model.config_dict}")
                return Task(task_model)
        
        return None
    
    @synchronized
    def put_task_ids(self, task_id: int):
        """将任务重新放回队列"""
        self.task_ids.put(task_id)
        logger.info(f"put task {task_id} back to queue")
        
    @synchronized
    def update_task_ids(self, task_ids: List[int]):
        """更新任务执行次数"""
        with self._get_session() as session:
            for task_id in task_ids:
                task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
                if task is None:
                    logger.warning(f"Task {task_id} not found in database")
                    continue
                    
                task.run_num += 1
                task.updated_at = datetime.utcnow()
                
                logger.info(f"update task {task_id} run times: {task.run_num}")
            
            session.commit()

    @synchronized
    def create_task(self, name: str, cmd: str, need_run_num: int = 1, 
                   config_dict: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """创建新任务"""
        try:
            with self._get_session() as session:
                new_task = TaskModel(
                    name=name,
                    cmd=cmd,
                    need_run_num=need_run_num,
                    config_dict=config_dict or {}
                )
                session.add(new_task)
                session.commit()
                
                # 将新任务加入队列
                for _ in range(need_run_num):
                    self.task_ids.put(new_task.id)
                    
                logger.info(f"Created new task: {new_task.id} - {name}")
                return new_task.id
                
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return None

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """根据ID获取任务"""
        with self._get_session() as session:
            task_model = session.query(TaskModel).filter(TaskModel.id == task_id).first()
            if task_model:
                return Task(task_model)
            return None

    def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        try:
            with self._get_session() as session:
                task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
                if task:
                    session.delete(task)
                    session.commit()
                    logger.info(f"Deleted task: {task_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            return False

    def update_task(self, task_id: int, **kwargs) -> bool:
        """更新任务信息"""
        try:
            with self._get_session() as session:
                task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
                if task:
                    for key, value in kwargs.items():
                        if hasattr(task, key):
                            setattr(task, key, value)
                    task.updated_at = datetime.utcnow()
                    session.commit()
                    logger.info(f"Updated task: {task_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            return False

# task_manager = TaskManager()

if __name__ == "__main__":
    pass
    # print(2)
    # task = TaskManager()
    # print(task.get_next_task())
    # print(task.get_next_task())
    # task.update_task_ids(0)
    # print(todo.get_next_todo())
    
    """
    python -m flowline.todo
    """
