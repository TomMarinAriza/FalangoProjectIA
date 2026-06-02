from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import FalangoEssentialSystems as FES
import FalangoGameLogic as FGL
import ai

class GameWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Falango - PyQt")
            
        self.game = FGL.Game(ai.PlayerCPUAdaptive(True))
        self.root = Path(__file__).resolve().parent

        self.status_label = QLabel("Elige un dedo para jugar.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))

        self.player_left_label = QLabel()
        self.player_right_label = QLabel()
        self.cpu_left_label = QLabel()
        self.cpu_right_label = QLabel()

        for label in (
            self.player_left_label,
            self.player_right_label,
            self.cpu_left_label,
            self.cpu_right_label,
        ):
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setMinimumSize(220, 220)
            label.setStyleSheet(
                "background: #0f172a; border: 1px solid #334155; border-radius: 10px;"
            )

        self.buttons: dict[str, QPushButton] = {}
        buttons_layout = QGridLayout()
        for i, finger in enumerate(FES.fingerNames):
            btn = QPushButton(finger)
            btn.clicked.connect(lambda _, f=finger: self.play_round(f))
            self.buttons[finger] = btn
            buttons_layout.addWidget(btn, i // 3, i % 3)

        self.reset_button = QPushButton("Reiniciar")
        self.reset_button.clicked.connect(self.reset_game)

        hands_layout = QGridLayout()
        hands_layout.addWidget(QLabel("Jugador izquierda"), 0, 0)
        hands_layout.addWidget(QLabel("Jugador derecha"), 0, 1)
        hands_layout.addWidget(QLabel("CPU izquierda"), 0, 2)
        hands_layout.addWidget(QLabel("CPU derecha"), 0, 3)
        hands_layout.addWidget(self.player_left_label, 1, 0)
        hands_layout.addWidget(self.player_right_label, 1, 1)
        hands_layout.addWidget(self.cpu_left_label, 1, 2)
        hands_layout.addWidget(self.cpu_right_label, 1, 3)

        self.setStyleSheet(
            "QWidget { background: #0b1220; color: #e2e8f0; }"
            "QPushButton { background: #1f2937; color: #e2e8f0; padding: 8px 12px; border-radius: 8px; }"
            "QPushButton:hover { background: #334155; }"
            "QPushButton:disabled { background: #0f172a; color: #64748b; }"
        )

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        main_layout.addWidget(self.status_label)
        main_layout.addLayout(hands_layout)
        main_layout.addItem(QSpacerItem(0, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.reset_button)
        self.setLayout(main_layout)

        self.update_hands()

    def sprite_pixmap(self, sprite_path: str) -> QPixmap:
        full_path = self.root / sprite_path
        pixmap = QPixmap(str(full_path))
        return pixmap

    def set_label_pixmap(self, label: QLabel, sprite_path: str) -> None:
        pixmap = self.sprite_pixmap(sprite_path)
        if pixmap.isNull():
            label.setText("(sin imagen)")
            return
        target = label.size()
        if target.width() <= 0 or target.height() <= 0:
            target = QSize(220, 220)
        label.setPixmap(
            pixmap.scaled(
                target,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def update_hands(self) -> None:
        self.game.player1.left.evalHandPos()
        self.game.player1.right.evalHandPos()
        self.game.player2.left.evalHandPos()
        self.game.player2.right.evalHandPos()

        self.set_label_pixmap(self.player_left_label, self.game.player1.left.sprite)
        self.set_label_pixmap(self.player_right_label, self.game.player1.right.sprite)
        self.set_label_pixmap(self.cpu_left_label, self.game.player2.left.sprite)
        self.set_label_pixmap(self.cpu_right_label, self.game.player2.right.sprite)

    def play_round(self, finger: str) -> None:
        if self.game.evalWinner():
            return

        self.game.player1.chooseFinger(finger)
        self.game.player2.chooseFinger()

        
        self.game.player1.right.closeHand()
        self.game.player2.right.closeHand()
        
        self.game.player1.right.openFinger(self.game.player1.chosenFinger)
        self.game.player2.right.openFinger(self.game.player2.chosenFinger)

        # Evaluar ronda
        self.game.evalRightHands()
        self.game.evalLeftHands()

        if hasattr(self.game.player2, "record_player_choice"):
            self.game.player2.record_player_choice(finger)

        self.update_hands()

        handNum = self.game.player2.left.handNum()
        print(handNum)
        print(7 - handNum + 16 * handNum // 8)

        if self.game.evalWinner():
            winner = 1 if self.game.player1.isGameWinner else (2 if self.game.player2.isGameWinner else 0)
            if hasattr(self.game.player2, "record_game_result"):
                self.game.player2.record_game_result(winner)
            if winner == 1:
                msg = "Ganaste!"
            elif winner == 2:
                msg = "La CPU gana."
            else:
                msg = "Empate."

            self.status_label.setText(msg)
            for btn in self.buttons.values():
                btn.setEnabled(False)
            QMessageBox.information(self, "Fin de partida", msg)
        else:
            self.status_label.setText("Elige un dedo para jugar.")

    def reset_game(self) -> None:
        self.game = FGL.Game(ai.PlayerCPUAdaptive(True))
        self.status_label.setText("Elige un dedo para jugar.")
        for btn in self.buttons.values():
            btn.setEnabled(True)
        self.update_hands()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update_hands()

def main() -> None:
    app = QApplication([])
    window = GameWindow()
    window.resize(800, 500)
    window.show()
    app.exec()

if __name__ == "__main__":
    main()