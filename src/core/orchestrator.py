"""
Orchestrator - the central dispatcher of the Methodist Agent.
Analyzes user requests, selects specialists, creates execution plans,
and manages approval gates.
Inspired by OpenCode's orchestration concept.
"""

import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from core.config import Config
from core.model_router import ModelRouter, Message
from core.context_manager import ContextManager


class TaskType(Enum):
    """Types of tasks the agent can handle."""
    DOCX_CREATE = "docx_create"
    DOCX_EDIT = "docx_edit"
    XLSX_CREATE = "xlsx_create"
    XLSX_EDIT = "xlsx_edit"
    PPTX_CREATE = "pptx_create"
    PPTX_EDIT = "pptx_edit"
    PDF_READ = "pdf_read"
    PDF_CONVERT = "pdf_convert"
    WEB_SEARCH = "web_search"
    DOCUMENT_ADAPT = "document_adapt"
    REPORT_GENERATE = "report_generate"
    SCHEDULE_MANAGE = "schedule_manage"
    CURRICULUM_DESIGN = "curriculum_design"
    GENERAL = "general"


@dataclass
class Task:
    """A single task in the execution plan."""
    id: str
    type: TaskType
    description: str
    agent: str  # Which specialist agent should handle this
    parameters: Dict[str, Any]
    dependencies: List[str]  # Task IDs that must complete before this one
    approved: bool = False
    completed: bool = False
    result: Any = None


@dataclass
class ExecutionPlan:
    """A plan of tasks to execute."""
    id: str
    description: str
    tasks: List[Task]
    requires_approval: bool = True
    approved: bool = False


class Orchestrator:
    """Central orchestrator that manages all agent operations."""
    
    # Keywords that trigger specific task types
    TRIGGERS = {
        TaskType.DOCX_CREATE: [
            "создать документ", "создать word", "новый документ", "новый docx",
            "рабочая программа", "учебная программа", "план", "отчет", "документ",
            "create document", "new docx", "working program", "curriculum"
        ],
        TaskType.DOCX_EDIT: [
            "редактировать документ", "изменить документ", "поправить", "отредактировать",
            "edit document", "modify docx", "update document"
        ],
        TaskType.XLSX_CREATE: [
            "создать таблицу", "создать excel", "ведомость", "расписание", "статистика",
            "create spreadsheet", "new xlsx", "schedule", "grade sheet"
        ],
        TaskType.XLSX_EDIT: [
            "редактировать таблицу", "изменить excel", "обновить ведомость",
            "edit spreadsheet", "modify xlsx"
        ],
        TaskType.PPTX_CREATE: [
            "создать презентацию", "создать powerpoint", "презентация", "слайды",
            "create presentation", "new pptx", "slides"
        ],
        TaskType.PPTX_EDIT: [
            "редактировать презентацию", "изменить слайды",
            "edit presentation", "modify pptx"
        ],
        TaskType.PDF_READ: [
            "прочитать pdf", "извлечь текст", "pdf", "скан",
            "read pdf", "extract text", "pdf document"
        ],
        TaskType.PDF_CONVERT: [
            "конвертировать pdf", "pdf в word", "pdf в docx",
            "convert pdf", "pdf to word", "pdf to docx"
        ],
        TaskType.WEB_SEARCH: [
            "найти", "поиск", "искать", "методичка", "интернет",
            "search", "find", "look for", "google"
        ],
        TaskType.DOCUMENT_ADAPT: [
            "адаптировать", "переделать", "обновить под", "привести в соответствие",
            "adapt", "update to", "convert to new format", "migrate"
        ],
        TaskType.REPORT_GENERATE: [
            "сгенерировать отчет", "создать отчет", "аналитика",
            "generate report", "create report", "analytics"
        ],
        TaskType.SCHEDULE_MANAGE: [
            "расписание", "график", "планирование",
            "schedule", "timetable", "planning"
        ],
        TaskType.CURRICULUM_DESIGN: [
            "учебный план", "программа обучения", "компетенции", "фгос",
            "curriculum", "syllabus", "competencies"
        ],
    }
    
    # Mapping task types to specialist agents
    AGENT_MAP = {
        TaskType.DOCX_CREATE: "document_specialist",
        TaskType.DOCX_EDIT: "document_specialist",
        TaskType.XLSX_CREATE: "document_specialist",
        TaskType.XLSX_EDIT: "document_specialist",
        TaskType.PPTX_CREATE: "document_specialist",
        TaskType.PPTX_EDIT: "document_specialist",
        TaskType.PDF_READ: "pdf_reader",
        TaskType.PDF_CONVERT: "pdf_reader",
        TaskType.WEB_SEARCH: "web_search",
        TaskType.DOCUMENT_ADAPT: "adaptation_agent",
        TaskType.REPORT_GENERATE: "document_specialist",
        TaskType.SCHEDULE_MANAGE: "document_specialist",
        TaskType.CURRICULUM_DESIGN: "document_specialist",
        TaskType.GENERAL: "general",
    }
    
    def __init__(self, config: Config, model_router: ModelRouter, context_manager: ContextManager):
        self.config = config
        self.model_router = model_router
        self.context_manager = context_manager
        self.current_plan: Optional[ExecutionPlan] = None
    
    def analyze_request(self, user_input: str) -> List[TaskType]:
        """Analyze user request and determine task types."""
        user_input_lower = user_input.lower()
        detected_types = []
        
        for task_type, keywords in self.TRIGGERS.items():
            for keyword in keywords:
                if keyword.lower() in user_input_lower:
                    if task_type not in detected_types:
                        detected_types.append(task_type)
                    break
        
        if not detected_types:
            detected_types = [TaskType.GENERAL]
        
        return detected_types
    
    def create_plan(self, user_input: str) -> ExecutionPlan:
        """Create an execution plan based on user request."""
        task_types = self.analyze_request(user_input)
        
        # Use LLM to refine the plan
        system_prompt = """You are a task planner for an AI assistant that helps methodists in educational institutions.
Your job is to break down user requests into specific, actionable steps.

Available specialists:
- document_specialist: Creates and edits DOCX, XLSX, PPTX files
- pdf_reader: Extracts text and tables from PDF files
- web_search: Searches the internet for methodological materials
- adaptation_agent: Adapts existing documents to new requirements

Respond with a JSON array of tasks. Each task should have:
- description: what to do
- agent: which specialist to use
- parameters: specific parameters for the task
"""
        
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=f"Create a plan for: {user_input}")
        ]
        
        try:
            response = self.model_router.chat(messages, temperature=0.3)
            # Try to parse JSON from response
            try:
                plan_data = json.loads(response.content)
            except json.JSONDecodeError:
                # Extract JSON from markdown code blocks
                json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response.content, re.DOTALL)
                if json_match:
                    plan_data = json.loads(json_match.group(1))
                else:
                    plan_data = []
        except Exception as e:
            print(f"LLM planning failed ({e}), using rule-based plan")
            plan_data = []
        
        # Build tasks
        tasks = []
        task_id = 0
        
        # If LLM didn't return valid plan, create rule-based plan
        if not plan_data:
            for task_type in task_types:
                agent = self.AGENT_MAP.get(task_type, "general")
                task_id += 1
                tasks.append(Task(
                    id=f"task_{task_id}",
                    type=task_type,
                    description=self._get_task_description(task_type, user_input),
                    agent=agent,
                    parameters={"user_input": user_input},
                    dependencies=[]
                ))
        else:
            # Use LLM-generated plan
            for i, item in enumerate(plan_data):
                task_type = self._guess_task_type(item.get("description", ""))
                tasks.append(Task(
                    id=f"task_{i+1}",
                    type=task_type,
                    description=item.get("description", ""),
                    agent=item.get("agent", self.AGENT_MAP.get(task_type, "general")),
                    parameters=item.get("parameters", {}),
                    dependencies=item.get("dependencies", [])
                ))
        
        plan = ExecutionPlan(
            id=f"plan_{self.context_manager._current_session.id if self.context_manager._current_session else 'default'}",
            description=user_input,
            tasks=tasks,
            requires_approval=self.config.approval.enabled
        )
        
        self.current_plan = plan
        return plan
    
    def _get_task_description(self, task_type: TaskType, user_input: str) -> str:
        """Get human-readable description for a task type."""
        descriptions = {
            TaskType.DOCX_CREATE: f"Создать Word документ: {user_input}",
            TaskType.DOCX_EDIT: f"Редактировать Word документ: {user_input}",
            TaskType.XLSX_CREATE: f"Создать Excel таблицу: {user_input}",
            TaskType.XLSX_EDIT: f"Редактировать Excel таблицу: {user_input}",
            TaskType.PPTX_CREATE: f"Создать презентацию: {user_input}",
            TaskType.PPTX_EDIT: f"Редактировать презентацию: {user_input}",
            TaskType.PDF_READ: f"Прочитать PDF документ: {user_input}",
            TaskType.PDF_CONVERT: f"Конвертировать PDF: {user_input}",
            TaskType.WEB_SEARCH: f"Поиск в интернете: {user_input}",
            TaskType.DOCUMENT_ADAPT: f"Адаптировать документ: {user_input}",
            TaskType.REPORT_GENERATE: f"Сгенерировать отчет: {user_input}",
            TaskType.SCHEDULE_MANAGE: f"Управление расписанием: {user_input}",
            TaskType.CURRICULUM_DESIGN: f"Проектирование учебного плана: {user_input}",
            TaskType.GENERAL: f"Общая задача: {user_input}",
        }
        return descriptions.get(task_type, user_input)
    
    def _guess_task_type(self, description: str) -> TaskType:
        """Guess task type from description."""
        desc_lower = description.lower()
        for task_type, keywords in self.TRIGGERS.items():
            for keyword in keywords:
                if keyword.lower() in desc_lower:
                    return task_type
        return TaskType.GENERAL
    
    def present_plan(self, plan: ExecutionPlan) -> str:
        """Format plan for user approval."""
        lines = [
            "🤖 План действий:",
            "=" * 50,
            f"Задача: {plan.description}",
            "",
            "Шаги:",
        ]
        
        for i, task in enumerate(plan.tasks, 1):
            status = "✅" if task.completed else "⏳"
            agent_emoji = {
                "document_specialist": "📝",
                "pdf_reader": "📄",
                "web_search": "🔍",
                "adaptation_agent": "🔄",
                "general": "🤖",
            }.get(task.agent, "🤖")
            
            lines.append(f"  {status} {i}. {agent_emoji} [{task.agent}] {task.description}")
        
        lines.extend([
            "",
            "=" * 50,
        ])
        
        if plan.requires_approval and not plan.approved:
            lines.append("⚠️  Этот план требует вашего подтверждения перед выполнением.")
        
        return "\n".join(lines)
    
    def approve_plan(self, plan: Optional[ExecutionPlan] = None) -> ExecutionPlan:
        """Mark plan as approved."""
        plan = plan or self.current_plan
        if plan:
            plan.approved = True
            for task in plan.tasks:
                task.approved = True
        return plan
    
    def reject_plan(self, plan: Optional[ExecutionPlan] = None) -> None:
        """Reject current plan."""
        plan = plan or self.current_plan
        if plan:
            plan.approved = False
    
    def get_next_task(self, plan: Optional[ExecutionPlan] = None) -> Optional[Task]:
        """Get next task that is ready to execute."""
        plan = plan or self.current_plan
        if not plan or not plan.approved:
            return None
        
        for task in plan.tasks:
            if task.completed or not task.approved:
                continue
            
            # Check dependencies
            deps_satisfied = all(
                any(t.id == dep and t.completed for t in plan.tasks)
                for dep in task.dependencies
            )
            
            if deps_satisfied:
                return task
        
        return None
    
    def mark_task_complete(self, task: Task, result: Any = None) -> None:
        """Mark a task as completed."""
        task.completed = True
        task.result = result
        
        # Log to context
        self.context_manager.log_action(
            f"task_complete_{task.type.value}",
            json.dumps({"task_id": task.id, "description": task.description}, ensure_ascii=False)
        )
    
    def is_plan_complete(self, plan: Optional[ExecutionPlan] = None) -> bool:
        """Check if all tasks in plan are completed."""
        plan = plan or self.current_plan
        if not plan:
            return True
        return all(task.completed for task in plan.tasks)
    
    def get_plan_summary(self, plan: Optional[ExecutionPlan] = None) -> str:
        """Get summary of completed plan."""
        plan = plan or self.current_plan
        if not plan:
            return "Нет активного плана."
        
        completed = sum(1 for t in plan.tasks if t.completed)
        total = len(plan.tasks)
        
        lines = [
            f"📊 Прогресс: {completed}/{total} задач выполнено",
            "",
        ]
        
        for task in plan.tasks:
            status = "✅ Выполнено" if task.completed else "❌ Не выполнено"
            lines.append(f"  {status}: {task.description}")
            if task.result:
                lines.append(f"     Результат: {str(task.result)[:100]}...")
        
        return "\n".join(lines)
