import random as rng

fingerNames: list[str] = ["thumb", "index","middle","ring","pinkie"]
phoneFingerOptions: list[str] = ["index","middle","ring"]
devilFingerOptions: list[str] = ["index","pinkie"]

specialPositions: dict[str, dict[str, bool]] = {
    "phone": {
        "thumb": True,
        "index": False,
        "middle": False,
        "ring": False,
        "pinkie": True
    },
    "scissors": {
        "thumb": False,
        "index": True,
        "middle": True,
        "ring": False,
        "pinkie": False
    },
    "pistol": {
        "thumb": True,
        "index": True,
        "middle": False,
        "ring": False,
        "pinkie": False
    },
    "lil' devil": {
        "thumb": False,
        "index": True,
        "middle": False,
        "ring": False,
        "pinkie": True
    },
    "fuck you": {
        "thumb": True,
        "index": False,
        "middle": True,
        "ring": False,
        "pinkie": False
    }
}

class Hand:
    """
    Clase para el manejo de las manos

    - isLeftHand: bool
    - fingersDict: dict -> lista los dedos y su estado
    - specialPosition: str -> indica la posición especial de la mano si es que tiene una.
    """
    def __init__(self, isLeftHand: bool, isInverted: bool):
        self.isLeftHand: bool = isLeftHand
        self.isInverted: bool = isInverted

        self.fingersDict: dict[str, bool] = { # Diccionario que indica los dedos abiertos y cerrados de una mano como True o False respectivamente
            "thumb": False,
            "index": False,
            "middle": False,
            "ring": False,
            "pinkie": False
        }

        self.specialPosition: str = ""
        self.sprite: str = ""

    def __str__(self) -> str: return f"{self.fingersDict}\n{self.specialPosition}"
    
    # datos numéricos
    def handCount(self) -> int: # retorna la cuenta de dedos que hay abiertos
        count: int = 0
        for finger in self.fingersDict: count += int(self.fingersDict[finger])
        return count

    def handNum(self) -> int: # Crea un número entre 0 y 31 que representa la posición actual de la mano tomando los dedos abiertos o cerrados como un número binario. 0 es todos cerrados, 31 es todos abiertos, el pulgar es el menos significativo y el meñique el más significativo
        """
        Función que representa la posición actual de la mano en términos de un número entre 0 y 31. Se puede pensar en cada dedo como un dígito de un número binario, donde el pulgar es el menos significativo y el meñique el más significativo.

        Se usa para la selección de los sprites.

        Retorna el número que representa la posición de la mano.
        """
        num: int = 0
        power: int = 0
        for finger in self.fingersDict:
            num += int(self.fingersDict[finger]) * 2 ** power
            power += 1
        return num

    # booleanos
    def hasOneOpenFinger(self) -> bool: return self.handCount() == 1

    def hasTwoOpenFingers(self) -> bool: return self.handCount() == 2
    
    def isHandOpen(self) -> bool: return self.handCount() == 5
    
    def isHandClosed(self) -> bool: return self.handCount() == 0

    def isSpecialPos(self, specialPos: str) -> bool: return self.specialPosition == specialPos

    # modificadores de atributos
    def evalHandSprite(self) -> str:
        spritePath: str = "mano/" # carpeta de manos

        # Decidir entre jugador izquierdo y derecho
        if not self.isInverted: spritePath += "derecho"
        else: spritePath += "reves"

        # Número de la posición
        spritePath += "/mano_"
        if self.isInverted: spritePath += "reves_"

        num: int = self.handNum()
        if not self.isInverted and not self.isLeftHand: num += 32 # Si se trata de la mano derecha del jugador a la izquierda
        elif self.isInverted: # Si se trata del jugador a la derecha
            num = 7 - num + 16 * num // 8
            if self.isLeftHand: num += 32 # Si se trata de su mano izquierda

            # Si no se cumple este if, se presume que es mano derecha del jugador izquierdo
        
        # Si no se cumple el elif, se presume que es su mano izquierda del jugador derecho

        spritePath += f"{num:02d}"
        spritePath += ".png"

        return spritePath
    
    def evalHandPos(self) -> None: # evaluar si la mano tiene una posición especial
        if self.hasTwoOpenFingers() and not(self.fingersDict["ring"]): # Debido a las posiciones existentes en el juego, el dedo anular no tiene posiciones que lo usen, por lo que tenerlo abierto descarta cualquier posición especial
            for pos in specialPositions.keys():
                if specialPositions[pos] == self.fingersDict: self.specialPosition = pos
        else: self.specialPosition = ""
        self.sprite = self.evalHandSprite()

    def openFinger(self, finger: str) -> None: # abrir un dedo a secas
        self.fingersDict[finger] = True
        self.evalHandPos()
    
    def openFingerSpecial(self, finger: str) -> None: # abrir un dedo con las reglas de apertura de Falango
        i: int = fingerNames.index(finger)
        for _ in range(5):
            if self.fingersDict[fingerNames[i]]: i = i - 1 - 5 * ((i - 1)//5)
            else:
                self.openFinger(fingerNames[i])
                break
        self.evalHandPos()
        return

    def closeFinger(self, finger: str) -> None:
        self.fingersDict[finger] = False
        self.evalHandPos()

    def closeHand(self) -> None:
        for finger in self.fingersDict: self.fingersDict[finger] = False
        self.specialPosition = ""
        self.evalHandPos()

    def openHand(self) -> None:
        for finger in self.fingersDict: self.fingersDict[finger] = True
        self.specialPosition = ""
        self.evalHandPos()

    def namesOfFingersOpen(self) -> list[str]: # devuelve una lista de los nombres de los dedos que están abiertos. Para ser usada por la pistola y el diablito
        openFingersList: list[str] = []
        for finger in self.fingersDict:
            if self.fingersDict[finger]: openFingersList.append(finger)
        return openFingersList

class Player:
    """
    Clase base para los jugadores, donde se definen todas las cosas que aplican para ambos jugadores sin importar cómo son.

    Tienen 2 manos, un dedo escogido tanto para rondas como posiciones especiales, indicadores de uso para la tijera y la pistola para que solo se usen 1 vez por obtención, una cola de los últimos 2 dedos sacados para no sacar 3 veces seguidas el mismo y datos que van recopilando tanto para ser usados en las dificultades como para el historial de partidas. isInverted se refiere a si usa los sprites invertidos o no
    """
    def __init__(self, isInverted: bool):
        self.right: Hand = Hand(False, isInverted)
        self.left: Hand = Hand(True, isInverted)

        self.chosenFinger: str = ""

        self.isRoundWinner: bool = False
        self.isGameWinner: bool = False

        # Variables de estado de las posiciones especiales
        self.pistolUsed: bool = False
        self.scissorsUsed: bool = False

        self.lastTwoFingers: list[str] = ["", ""] # Esto funciona esencialmente como una cola de longitud constante = 2. Los elementos entran por la izquierda y salen por la derecha

        self.Data: dict = {
            "fingerHistory": [],
            "fingerUses": {
                "thumb": 0,
                "index": 0,
                "middle": 0,
                "ring": 0,
                "pinkie": 0
            }
        }

    # Métodos comunes
    def updateLastTwoFingers(self, finger: str) -> None: self.lastTwoFingers = [finger, self.lastTwoFingers[0]]
    
    def twoFingersInARow(self) -> bool: return self.lastTwoFingers[0] == self.lastTwoFingers[1] and self.lastTwoFingers != ""
    
    def listOfOpenFingers(self) -> list[str]:
        fingerList: list[str] = []

        for finger in self.left.fingersDict:
            if self.left.fingersDict[finger]: fingerList.append(finger)

        return fingerList

    def closedFingerList(self) -> list[str]:
        fingerList: list[str] = []

        for finger in self.left.fingersDict:
            if not self.left.fingersDict[finger]: fingerList.append(finger)

        return fingerList
    
    def updateData(self):
        self.Data["fingerHistory"].append(self.chosenFinger)
        self.Data["fingerUses"][self.chosenFinger] += 1
    
    def closeHands(self):
        self.right.closeHand()
        self.left.closeHand()
    
    # métodos específicos que serán sobreescritos por las diferentes subclases de jugadores
    def chooseFinger():
        pass

class PlayerHuman(Player):
    def chooseFinger(self, finger: str):
        self.chosenFinger = finger

class PlayerCPURandom(Player):
    def chooseFinger(self, fingerList: list[str]):
        self.chosenFinger = rng.choice(fingerList) 

class PlayerAI(Player):
    def chooseFinger(self, fingerList: list[str]):
        ... #TODO