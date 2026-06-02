import FalangoEssentialSystems as FES
import ai
import dataclasses

# El juego tiene 2 jugadores
# Las rondas controlan el estado de las manos en el juego
# # Las rondas deben tener acceso a los jugadores
# El juego controla la ejecución de las rondas
# # El juego debe ser capaz de crear rondas
# # También debe poder almacenar la lista de rondas

class Round:
    """
    Clase ronda para guardar información de rondas del juego

    - player1 y player2: FES.Player
    - winner: FES.Player
    - duel: bool -> indicador de ronda duelo
    """
    def __init__(self, player1: FES.Player, player2: FES.Player, duel: bool):
        self.player1: FES.Player = player1
        self.player2: FES.Player = player2
        self.winner: FES.Player = None

        self.duel: bool = duel # Variable de estado de la ronda. True para ronda pistola, false para ronda normal

    def evalRound(self): # evaluar el resultado de una ronda
        self.winner = 0

        if self.player1.right.hasOneOpenFinger() and self.player2.right.hasOneOpenFinger():
            fingerList1 = list(self.player1.right.fingersDict.values())
            fingerList2 = list(self.player2.right.fingersDict.values())

            fingerIndex1 = fingerList1.index(True)
            fingerIndex2 = fingerList2.index(True)

            if fingerList1[fingerIndex1] and fingerList2[(fingerIndex1 + 1) % 5]:
                self.winner = self.player1
                if self.duel: self.player2.left.closeHand()
                self.player1.left.openFingerSpecial(FES.fingerNames[fingerIndex2])
            elif fingerList2[fingerIndex2] and fingerList1[(fingerIndex2 + 1) % 5]:
                self.winner = self.player2
                if self.duel: self.player1.left.closeHand()
                self.player2.left.openFingerSpecial(FES.fingerNames[fingerIndex1])

class Game:
    """
    Clase partida que controla la información de la partida con métodos para la evaluación de las rondas

    - player1 y player2: FES.Player
    - winner: int -> número que representa al jugador ganador. 0: ninguno, 1 y 2, jugadores respectivos
    - currentRound: Round
    - roundList: list[Round] -> Recuento de las rondas jugadas
    """
    def __init__(self, Player2: FES.Player):
        self.player1: FES.PlayerHuman = FES.PlayerHuman(False)
        self.player2: FES.PlayerCPURandom = Player2
        self.winner: int = 0

        self.roundList: list[Round] = []
    
    def evalRightHands(self): # evaluar el resultado de una ronda
        if self.player1.right.hasOneOpenFinger() and self.player2.right.hasOneOpenFinger():
            fingerList1: list[bool] = list(self.player1.right.fingersDict.values())
            fingerList2: list[bool] = list(self.player2.right.fingersDict.values())

            fingerIndex1: int = fingerList1.index(True)
            fingerIndex2: int = fingerList2.index(True)

            if fingerList1[fingerIndex1] and fingerList2[(fingerIndex1 + 1) % 5]:
                self.player1.isRoundWinner = True
                self.player1.left.openFingerSpecial(FES.fingerNames[fingerIndex2])
                self.player1.updateData()

                self.player1.pistolUsed = False
                self.player1.scissorsUsed = False
            elif fingerList2[fingerIndex2] and fingerList1[(fingerIndex2 + 1) % 5]:
                self.player2.isRoundWinner = True
                self.player2.left.openFingerSpecial(FES.fingerNames[fingerIndex1])
                self.player2.updateData()

                self.player2.pistolUsed = False
                self.player2.scissorsUsed = False
            else:
                if self.player1.left.specialPosition == "pistol": self.player1.pistolUsed = True
                if self.player2.left.specialPosition == "pistol": self.player2.pistolUsed = True

    def evalLeftHands(self):
        if self.player1.left.specialPosition != "":
            match self.player1.left.specialPosition:
                case "phone": self.player1.left.openFinger(self.player1.chosenFinger)
                case "scissors":
                    self.player2.left.closeFinger(self.player1.chosenFinger)
                    self.player1.scissorsUsed = True
                case "pistol":
                    self.player2.left.closeHand()
                case "lil' devil": self.player1.left.closeFinger(self.player1.chosenFinger)
                case "fuck you": self.player2.isGameWinner = True
        elif self.player2.left.specialPosition != "":
            match self.player2.left.specialPosition:
                case "phone": self.player2.left.openFinger(self.player1.chosenFinger)
                case "scissors":
                    self.player1.left.closeFinger(self.player1.chosenFinger)
                    self.player2.scissorsUsed = True
                case "pistol":
                    self.player1.left.closeHand()
                case "lil' devil": self.player2.left.closeFinger(self.player1.chosenFinger)
                case "fuck you": self.player1.isGameWinner = True

    def evalWinner(self) -> bool:
        if self.player1.left.isHandOpen(): self.player1.isGameWinner = True
        elif self.player2.left.isHandOpen(): self.player2.isGameWinner = True
        return self.player1.left.isHandOpen() or self.player2.left.isHandOpen()

# PLAN
# 1. La interfaz dice qué dedo se escoge a la clase Game
# 2. Game evalúa las manos derechas de ambos jugadores
# 3. Tras eso, si es necesario, se evalúan las manos izquierdas, tomando un input de la interfaz de ser necesario
# 4. Se preparan los jugadores para una nueva ronda
# 5. Repetir hasta que alguno gane el juego.