"""ui — themed component vocabulary. Every function reads the active theme."""

from cli_kit.ui.banner import banner
from cli_kit.ui.console import console
from cli_kit.ui.feedback import breadcrumb, error, info, success, warn
from cli_kit.ui.layout import Cell, Col, badge, kv, panel, table
from cli_kit.ui.progress import Task, progress
from cli_kit.ui.report import Step, StepReport, StepStatus
from cli_kit.ui.status import status

__all__ = [
    "console",
    "banner",
    "success",
    "error",
    "warn",
    "info",
    "breadcrumb",
    "kv",
    "panel",
    "table",
    "Cell",
    "Col",
    "badge",
    "progress",
    "Task",
    "status",
    "StepReport",
    "Step",
    "StepStatus",
]
