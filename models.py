from dataclasses import dataclass, field
from typing import List
import uuid
from datetime import datetime

def make_id() -> str:
    return str(uuid.uuid4())

@dataclass
class Card:
    id: str
    title: str
    description: str = ""
    completed: bool = False
    priority: str = "Средняя"  # "Низкая", "Средняя", "Высокая"
    due_date: str = ""  # ISO формат: "2025-12-31" или "2025-12-31T14:30"
    team: str = ""  # Команда/исполнитель

@dataclass
class Column:
    id: str
    title: str
    cards: List[Card] = field(default_factory=list)

@dataclass
class Board:
    id: str
    title: str
    columns: List[Column] = field(default_factory=list)

def demo_board() -> Board:
    todo = Column(
        id=make_id(),
        title="Неделя",
        cards=[
            Card(id=make_id(), title="Найти заказ на видеомонтаж", completed=False, priority="Высокая", due_date="2025-12-20", team="Видео"),
            Card(id=make_id(), title="Выложить пост в ВК с фото", completed=False, priority="Средняя", due_date="2025-12-18", team="Маркетинг"),
            Card(id=make_id(), title="Улучшить личный сайт", completed=False, priority="Низкая", team="Дизайн"),
        ],
    )

    done = Column(
        id=make_id(),
        title="Готово",
        cards=[
            Card(id=make_id(), title="Выложить фото в фотобанк", completed=True, priority="Средняя", team="Фото"),
        ],
    )

    return Board(
        id=make_id(),
        title="Задачи",
        columns=[todo, done],
    )