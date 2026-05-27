import FalangoEssentialSystems as FES

# El juego tiene 2 jugadores
# Las rondas controlan el estado de las manos en el juego
# # Las rondas deben tener acceso a los jugadores
# El juego controla la ejecución de las rondas
# # El juego debe ser capaz de crear rondas
# # También debe poder almacenar la lista de rondas

class Round:
    """
    Clase ronda para gestionar las rondas en el juego

    - player1 y player2: FES.Player
    - winner: FES.Player
    - duel: bool -> indicador de ronda duelo
    """
    def __init__(self, player1: FES.Player, player2: FES.Player, duel: bool):
        self.player1: FES.Player = player1
        self.player2: FES.Player = player2
        self.winner: int = 0

        self.duel: bool = duel # indicador de ronda pistola (o duelo) o ronda normal

    def evalRound(self): # evaluar el resultado de una ronda
        self.winner = 0
        if self.player1.right.hasOneOpenFinger() and self.player2.right.hasOneOpenFinger():
            fingerList1 = list(self.player1.right.fingersDict.values())
            fingerList2 = list(self.player2.right.fingersDict.values())
            fingerIndex1 = fingerList1.index(True)
            fingerIndex2 = fingerList2.index(True)
            if fingerList1[fingerIndex1] and fingerList2[(fingerIndex1 + 1) % 5]:
                self.winner = 1
                if self.duel: self.player2.left.closeHand()
                self.player1.left.openFingerSpecial(FES.fingerNames[fingerIndex2])
            elif fingerList2[fingerIndex2] and fingerList1[(fingerIndex2 + 1) % 5]:
                self.winner = 2
                if self.duel: self.player1.left.closeHand()
                self.player2.left.openFingerSpecial(FES.fingerNames[fingerIndex1])

class Game:
    """
    Clase partida que controla la información de la partida

    - player1 y player2: FES.Player
    - winner: int -> número que representa al jugador ganador. 0: ninguno, 1 y 2, jugadores respectivos
    - currentRound: Round
    - roundList: list[Round] -> Recuento de las rondas jugadas
    """
    def __init__(self):
        self.player1: FES.PlayerHuman = FES.PlayerHuman(1, False)
        self.player2: FES.PlayerCPURandom = FES.PlayerCPURandom(2, True)
        self.winner: int = 0

        self.currentRound: Round = None
        self.roundList: list[Round] = []

    def evalPistolRound(self) -> bool:
        return self.player1.left.isSpecialPos("pistol") or self.player2.left.isSpecialPos("pistol")

    def resetRightHands(self):
        self.player1.right.closeHand()
        self.player2.right.closeHand()

    def processRound(self): # recibe los dedos que los jugadores abren en sus manos derechas y procesa la información
        self.player1.right.openFinger(self.player1.chosenFinger)
        self.player1.chosenFinger = self.player1.chosenFinger
        self.player2.right.openFinger(self.player2.chosenFinger)
        self.player2.chosenFinger = self.player2.chosenFinger
        newRound = Round(self.player1, self.player2, self.evalPistolRound)
        newRound.evalRound()
        self.player1 = newRound.player1
        self.player2 = newRound.player2
        self.currentRound = newRound
        self.roundList.append(newRound)

    def evalWinner(self) -> bool:
        if self.player1.left.isHandOpen(): self.winner = self.player1
        elif self.player2.left.isHandOpen(): self.winner = self.player2
        else: self.winner = None
        return self.player1.left.isHandOpen() or self.player2.left.isHandOpen()