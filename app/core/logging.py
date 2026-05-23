import structlog
import logging
import sys
from typing import Any, Dict


def setup_logging(environment: str = "development"):
    """Настройка структурированного логирования"""

    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if environment == "production":
        # JSON формат для production
        processors = shared_processors + [structlog.processors.JSONRenderer()]
        logging.basicConfig(
            format="%(message)s",
            level=logging.INFO,
            handlers=[logging.StreamHandler(sys.stdout)],
        )
    else:
        # Человекочитаемый формат для разработки
        processors = shared_processors + [structlog.dev.ConsoleRenderer()]
        logging.basicConfig(
            format="%(message)s",
            level=logging.DEBUG,
            handlers=[logging.StreamHandler(sys.stdout)],
        )

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


# Глобальный логгер
logger = setup_logging()


def log_llm_request(
    competency_id: str, scenario: str, answer: str, evaluation: Dict[str, Any]
):
    """Логирование LLM запросов"""
    logger.info(
        "llm_evaluation",
        competency_id=competency_id,
        scenario_length=len(scenario),
        answer_length=len(answer),
        score=evaluation.get("total_score"),
        passed=evaluation.get("passed"),
        model="gpt-4o-mini",
        provider="vsegpt",
    )
