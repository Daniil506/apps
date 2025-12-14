import sys
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QDialog,
    QDialogButtonBox,
    QMessageBox,
    QMenu,
    QCheckBox,
    QComboBox,
    QDateEdit,
)
from PySide6.QtCore import Qt, QDate
from models import Board, Column, Card, make_id
from storage import load_board, save_board

class CardDialog(QDialog):
    def __init__(self, parent=None, title="Новая задача", card: Card | None = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        
        self.title_edit = QLineEdit()
        self.desc_edit = QTextEdit()
        self.completed_checkbox = QCheckBox("Задача выполнена")
        
        # Новые поля
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Низкая", "Средняя", "Высокая"])
        
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate())
        self.clear_date_checkbox = QCheckBox("Без срока")
        
        self.team_edit = QLineEdit()
        
        if card is not None:
            self.title_edit.setText(card.title)
            self.desc_edit.setPlainText(card.description)
            self.completed_checkbox.setChecked(card.completed)
            self.priority_combo.setCurrentText(card.priority)
            self.team_edit.setText(card.team)
            
            if card.due_date:
                # Парсим дату из строки
                try:
                    date_obj = datetime.fromisoformat(card.due_date)
                    self.due_date_edit.setDate(date_obj.date())
                except:
                    pass
            else:
                self.clear_date_checkbox.setChecked(True)
                self.due_date_edit.setEnabled(False)
        
        # UI Layout
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Название"))
        layout.addWidget(self.title_edit)
        
        layout.addWidget(QLabel("Описание"))
        layout.addWidget(self.desc_edit)
        
        layout.addWidget(QLabel("Срочность"))
        layout.addWidget(self.priority_combo)
        
        layout.addWidget(QLabel("Срок выполнения"))
        layout.addWidget(self.due_date_edit)
        layout.addWidget(self.clear_date_checkbox)
        
        layout.addWidget(QLabel("Команда/Исполнитель"))
        layout.addWidget(self.team_edit)
        
        layout.addWidget(self.completed_checkbox)
        
        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.btn_box = QDialogButtonBox(buttons)
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)
        layout.addWidget(self.btn_box)
        
        # Связываем чекбокс с включением/отключением выбора даты
        self.clear_date_checkbox.stateChanged.connect(self.toggle_due_date)
    
    def toggle_due_date(self):
        self.due_date_edit.setEnabled(not self.clear_date_checkbox.isChecked())
    
    def get_data(self) -> tuple[str, str, bool, str, str, str]:
        due_date = ""
        if not self.clear_date_checkbox.isChecked():
            due_date = self.due_date_edit.date().toString(Qt.ISODate)
        
        return (
            self.title_edit.text().strip(),
            self.desc_edit.toPlainText().strip(),
            self.completed_checkbox.isChecked(),
            self.priority_combo.currentText(),
            due_date,
            self.team_edit.text().strip(),
        )

class ColumnDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новая колонка")
        self.setModal(True)
        self.title_edit = QLineEdit()
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Название колонки"))
        layout.addWidget(self.title_edit)
        
        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.btn_box = QDialogButtonBox(buttons)
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)
        layout.addWidget(self.btn_box)
    
    def get_title(self) -> str:
        return self.title_edit.text().strip()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaskBoard – десктоп‑планировщик")
        self.resize(1000, 600)
        
        self.board: Board = load_board()
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        root_layout = QHBoxLayout(main_widget)
        
        # Левая панель - колонки
        left_layout = QVBoxLayout()
        self.columns_list = QListWidget()
        self.btn_add_column = QPushButton("Добавить колонку")
        self.btn_delete_column = QPushButton("Удалить колонку")
        left_layout.addWidget(QLabel("Колонки"))
        left_layout.addWidget(self.columns_list)
        left_layout.addWidget(self.btn_add_column)
        left_layout.addWidget(self.btn_delete_column)
        
        # Правая панель - задачи
        right_layout = QVBoxLayout()
        self.board_title_label = QLabel(self.board.title)
        self.board_title_label.setAlignment(Qt.AlignCenter)
        self.board_title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        self.cards_list = QListWidget()
        self.cards_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.cards_list.customContextMenuRequested.connect(self.show_card_menu)
        
        self.btn_add_card = QPushButton("Добавить задачу")
        self.btn_delete_card = QPushButton("Удалить задачу")
        
        right_layout.addWidget(self.board_title_label)
        right_layout.addWidget(self.cards_list)
        right_layout.addWidget(self.btn_add_card)
        right_layout.addWidget(self.btn_delete_card)
        
        root_layout.addLayout(left_layout, 1)
        root_layout.addLayout(right_layout, 2)
        
        # Сигналы
        self.columns_list.currentRowChanged.connect(self.on_column_changed)
        self.btn_add_column.clicked.connect(self.add_column)
        self.btn_delete_column.clicked.connect(self.delete_column)
        self.btn_add_card.clicked.connect(self.add_card)
        self.btn_delete_card.clicked.connect(self.delete_card)
        self.cards_list.itemDoubleClicked.connect(self.edit_card)
        
        self.refresh_columns()
    
    def current_column(self) -> Column | None:
        idx = self.columns_list.currentRow()
        if idx < 0 or idx >= len(self.board.columns):
            return None
        return self.board.columns[idx]
    
    def refresh_columns(self):
        self.columns_list.clear()
        for col in self.board.columns:
            item = QListWidgetItem(col.title)
            self.columns_list.addItem(item)
        
        if self.board.columns:
            self.columns_list.setCurrentRow(0)
        else:
            self.cards_list.clear()
    
    def refresh_cards(self, column: Column | None):
        self.cards_list.clear()
        if not column:
            return
        
        for card in column.cards:
            # Формируем текст задачи
            status = "✓ " if card.completed else "○ "
            priority_icon = {"Низкая": "◯", "Средняя": "◐", "Высокая": "●"}[card.priority]
            
            # Формируем дату
            date_str = ""
            if card.due_date:
                try:
                    date_obj = datetime.fromisoformat(card.due_date)
                    date_str = f" 📅 {date_obj.strftime('%d.%m')}"
                except:
                    pass
            
            # Формируем команду
            team_str = ""
            if card.team:
                team_str = f" 👥 {card.team}"
            
            display_text = f"{status}{priority_icon} {card.title}{date_str}{team_str}"
            item = QListWidgetItem(display_text)
            
            # Tooltip с полной информацией
            tooltip = f"Название: {card.title}\n"
            tooltip += f"Срочность: {card.priority}\n"
            if card.due_date:
                tooltip += f"Срок: {card.due_date}\n"
            if card.team:
                tooltip += f"Команда: {card.team}\n"
            tooltip += f"Описание: {card.description}"
            item.setToolTip(tooltip)
            
            # Если выполнена, делаем текст серым
            if card.completed:
                item.setForeground(Qt.gray)
            
            self.cards_list.addItem(item)
    
    def on_column_changed(self, index: int):
        if index < 0 or index >= len(self.board.columns):
            self.cards_list.clear()
            return
        self.refresh_cards(self.board.columns[index])
    
    def add_column(self):
        dlg = ColumnDialog(self)
        if dlg.exec() == QDialog.Accepted:
            title = dlg.get_title()
            if not title:
                return
            self.board.columns.append(Column(id=make_id(), title=title))
            save_board(self.board)
            self.refresh_columns()
    
    def delete_column(self):
        col = self.current_column()
        if not col:
            return
        
        if (
            QMessageBox.question(
                self,
                "Удалить колонку",
                f"Удалить колонку «{col.title}» со всеми задачами?",
            )
            == QMessageBox.Yes
        ):
            self.board.columns.remove(col)
            save_board(self.board)
            self.refresh_columns()
    
    def add_card(self):
        col = self.current_column()
        if not col:
            return
        
        dlg = CardDialog(self, title="Новая задача")
        if dlg.exec() == QDialog.Accepted:
            title, desc, completed, priority, due_date, team = dlg.get_data()
            if not title:
                return
            
            col.cards.append(
                Card(
                    id=make_id(),
                    title=title,
                    description=desc,
                    completed=completed,
                    priority=priority,
                    due_date=due_date,
                    team=team,
                )
            )
            save_board(self.board)
            self.refresh_cards(col)
    
    def edit_card(self, item: QListWidgetItem):
        col = self.current_column()
        if not col:
            return
        
        idx = self.cards_list.row(item)
        if idx < 0 or idx >= len(col.cards):
            return
        
        card = col.cards[idx]
        dlg = CardDialog(self, title="Редактировать задачу", card=card)
        
        if dlg.exec() == QDialog.Accepted:
            title, desc, completed, priority, due_date, team = dlg.get_data()
            if not title:
                return
            
            card.title = title
            card.description = desc
            card.completed = completed
            card.priority = priority
            card.due_date = due_date
            card.team = team
            
            save_board(self.board)
            self.refresh_cards(col)
    
    def delete_card(self):
        col = self.current_column()
        if not col:
            return
        
        idx = self.cards_list.currentRow()
        if idx < 0 or idx >= len(col.cards):
            return
        
        card = col.cards[idx]
        
        if (
            QMessageBox.question(
                self,
                "Удалить задачу",
                f"Удалить задачу «{card.title}»?",
            )
            == QMessageBox.Yes
        ):
            col.cards.pop(idx)
            save_board(self.board)
            self.refresh_cards(col)
    
    def show_card_menu(self, pos):
        col = self.current_column()
        if not col:
            return
        
        idx = self.cards_list.currentRow()
        if idx < 0 or idx >= len(col.cards):
            return
        
        menu = QMenu(self)
        move_menu = menu.addMenu("Переместить в колонку")
        
        for target_col in self.board.columns:
            if target_col is col:
                continue
            act = move_menu.addAction(target_col.title)
            act.triggered.connect(
                lambda checked=False, tc=target_col: self.move_card_to_column(tc)
            )
        
        menu.exec(self.cards_list.mapToGlobal(pos))
    
    def move_card_to_column(self, target_column: Column):
        src_col = self.current_column()
        if not src_col:
            return
        
        idx = self.cards_list.currentRow()
        if idx < 0 or idx >= len(src_col.cards):
            return
        
        card = src_col.cards.pop(idx)
        target_column.cards.append(card)
        
        save_board(self.board)
        self.refresh_cards(src_col)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()