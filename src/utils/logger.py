"""
ResearchOps Logging System

Provides structured logging with:
- Console output with colors (for local dev)
- JSON format (for GitHub Actions / production)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Workflow context (WF1, WF2, WF3)
- Optional file persistence
"""
import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path


class ResearchOpsFormatter(logging.Formatter):
    """Custom formatter with emoji icons and colors for terminal output"""

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'RESET': '\033[0m'
    }

    ICONS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️ ',
        'WARNING': '⚠️ ',
        'ERROR': '🚨'
    }

    def format(self, record):
        # Add workflow context if available
        workflow = getattr(record, 'workflow', '')
        workflow_prefix = f"[{workflow}] " if workflow else ""

        # Determine if we're in a terminal (for colors)
        use_colors = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

        if use_colors:
            color = self.COLORS.get(record.levelname, '')
            reset = self.COLORS['RESET']
            icon = self.ICONS.get(record.levelname, '')
            return f"{color}{icon} {workflow_prefix}{record.getMessage()}{reset}"
        else:
            icon = self.ICONS.get(record.levelname, '')
            return f"{icon} {workflow_prefix}{record.getMessage()}"


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging in CI/production"""

    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'message': record.getMessage(),
            'workflow': getattr(record, 'workflow', None),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        # Remove None values
        log_entry = {k: v for k, v in log_entry.items() if v is not None}

        return json.dumps(log_entry)


class WorkflowLogger:
    """Logger with workflow context"""

    def __init__(self, workflow: str, logger: logging.Logger):
        self.workflow = workflow
        self.logger = logger

    def _log(self, level: int, msg: str, *args, **kwargs):
        extra = kwargs.pop('extra', {})
        extra['workflow'] = self.workflow
        kwargs['extra'] = extra
        self.logger.log(level, msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs):
        self._log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self._log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self._log(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self._log(logging.ERROR, msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
        kwargs['exc_info'] = True
        self._log(logging.ERROR, msg, *args, **kwargs)


def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup the logging system.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        json_format: Use JSON format (for CI/production)
        log_file: Optional path to log file

    Returns:
        Configured logger
    """
    # Determine settings from environment
    env_level = os.getenv('LOG_LEVEL', level).upper()
    env_json = os.getenv('LOG_JSON', str(json_format)).lower() == 'true'
    env_file = os.getenv('LOG_FILE', log_file)

    # In GitHub Actions, default to JSON format
    if os.getenv('GITHUB_ACTIONS') == 'true':
        env_json = True

    # Create logger
    logger = logging.getLogger('researchops')
    logger.setLevel(getattr(logging, env_level, logging.INFO))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if env_json:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ResearchOpsFormatter())
    logger.addHandler(console_handler)

    # File handler (optional)
    if env_file:
        log_path = Path(env_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(JSONFormatter())  # Always JSON for files
        logger.addHandler(file_handler)

    return logger


def get_logger(workflow: Optional[str] = None) -> WorkflowLogger | logging.Logger:
    """
    Get a logger instance, optionally with workflow context.

    Args:
        workflow: Workflow identifier (WF1, WF2, WF3)

    Returns:
        Logger with optional workflow context
    """
    logger = logging.getLogger('researchops')

    # Ensure logger is configured
    if not logger.handlers:
        setup_logging()

    if workflow:
        return WorkflowLogger(workflow, logger)

    return logger


# Convenience function for quick logging
def log(level: str, message: str, workflow: Optional[str] = None):
    """Quick logging function"""
    logger = get_logger(workflow)
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message)
