import glue_work_bot
from types import ModuleType


def test_nothing() -> None:
    assert type(glue_work_bot) == ModuleType
