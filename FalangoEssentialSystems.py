import random as rng
from math import floor

fingerNames: list[str] = ["thumb", "index","middle","ring","pinkie"]
phoneFingerOptions: list[str] = ["index","middle","ring"]
devilFingerOptions: list[str] = ["index","pinkie"]

specialPositions: dict = {
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

    - leftHand: bool
    - fingersDict: dict -> lista los dedos y su estado
    - specialPosition: str -> indica la posición especial de la mano si es que tiene una.
    """
    def __init__(self, leftHand: bool, inverted: bool):
        self.leftHand: bool = leftHand
        self.inverted: bool = inverted

        self.fingersDict: dict = { # Diccionario que indica los dedos abiertos y cerrados de una mano como True o False respectivamente
            "thumb": False,
            "index": False,
            "middle": False,
            "ring": False,
            "pinkie": False
        }

        self.specialPosition: str = ""
        self.sprite: str = ""

    def __str__(self):
        return f"{self.fingersDict}\n{self.specialPosition}"
    
    # datos numéricos
    def handCount(self) -> int: # retorna la cuenta de dedos que hay abiertos
        count: int = 0
        for finger in self.fingersDict: count += int(self.fingersDict[finger])
        return count

    def handNum(self) -> int: # Crea un número entre 0 y 31 que representa la posición actual de la mano
        num: int = 0
        power: int = 0
        for finger in self.fingersDict:
            num += int(self.fingersDict[finger]) * 2 ** power
            power += 1
        return num

    # booleanos
    def oneOpenFinger(self) -> bool:
        return self.handCount() == 1

    def twoOpenFingers(self) -> bool:
        return self.handCount() == 2
    
    def handOpened(self) -> bool:
        return self.handCount() == 5
    
    def handClosed(self) -> bool:
        return self.handCount() == 0

    def isSpecialPos(self, specialPos) -> bool:
        return self.specialPosition == specialPos

    # modificadores de atributos
    def evalHandSprite(self) -> str:
        spritePath: str = "mano/" # carpeta
        if not self.inverted: spritePath += "derecho"
        else: spritePath += "reves"
        spritePath += "/mano_"
        if self.inverted: spritePath += "reves_"
        num: int = self.handNum()
        if not self.inverted and not self.leftHand: num += 32
        elif self.inverted:
            num = 8 * (num//8 + 1) - 1 - num%8
            if self.leftHand: num += 32
        spritePath += str(num//10)
        spritePath += str(num%10)
        spritePath += ".png"
        return spritePath
    
    def evalHandPos(self): # evaluar si la mano tiene una posición especial
        if self.twoOpenFingers() and not(self.fingersDict["ring"]):
            for pos in specialPositions:
                if specialPositions[pos] == self.fingersDict:
                    self.specialPosition = pos
        else: self.specialPosition = ""
        self.sprite = self.evalHandSprite()

    def openFinger(self, finger: str): # abrir un dedo a secas
        self.fingersDict[finger] = True
        self.evalHandPos()
    
    def openFingerSpecial(self, finger: str): # abrir un dedo con las reglas de apertura de Falango
        i: int = fingerNames.index(finger)
        for j in range(5):
            if self.fingersDict[fingerNames[i]]: i = (i - 1) % 5
            else:
                self.openFinger(fingerNames[i])
                self.evalHandPos()
                return

    def closeFinger(self, finger: str): # Cerrar un dedo a secas
        self.fingersDict[finger] = False
        self.evalHandPos()
    
    def invertFinger(self, finger: str): # Invertir el estado actual de un dedo
        self.fingersDict[finger] = not(self.fingersDict[finger])
        self.evalHandPos()

    def closeHand(self):
        for finger in self.fingersDict: self.fingersDict[finger] = False
        self.specialPosition = ""
        self.evalHandPos()

    def openHand(self):
        for finger in self.fingersDict: self.fingersDict[finger] = True
        self.specialPosition = ""
        self.evalHandPos()

    def namesOfOpenFingers(self) -> list[str]: # devuelve una lista de los nombres de los dedos que están abiertos
        openFingersList: list[str] = []
        for finger in self.fingersDict:
            if self.fingersDict[finger]:
                openFingersList.append(finger)
        return openFingersList

class Player:
    """
    Clase base para los jugadores, donde se definen todas las cosas que aplican para ambos jugadores sin importar cómo son.

    Tienen 2 manos, un dedo escogido tanto para rondas como posiciones especiales, un ID, indicadores de uso para la tijera y la pistola para que solo se usen 1 vez por obtención, una cola de los últimos 2 dedos sacados para no sacar 3 veces seguidas el mismo y datos que van recopilando tanto para ser usados en las dificultades como para el historial de partidas
    """
    def __init__(self, playerID: int, inverted: bool):
        self.right: Hand = Hand(False, inverted)
        self.left: Hand = Hand(True, inverted)

        self.chosenFinger: str = ""

        self.playerID: int = playerID

        self.pistolUsed: bool = False
        self.scissorsUsed: bool = False

        self.lastTwoFingers: list[str] = ["", ""]

        self.Data: dict = {
            "fingerHistory": [],
            "fingerUses": {
                "thumb": 0,
                "index": 0,
                "middle": 0,
                "ring": 0,
                "pinkie": 0
            },
            "specialPositionsUsed": []
        }

    # Métodos comunes
    def updateFingerHistory(self, finger):
        self.lastTwoFingers[1] = self.fingerHistory[0]
        self.lastTwoFingers[0] = finger
    
    def twoInARow(self) -> bool:
        return self.lastTwoFingers[0] == self.lastTwoFingers[1] and self.lastTwoFingers != "" and self.lastTwoFingers != ""
    
    def openFingerList(self) -> list[str]:
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
        if self.left.specialPosition != "":
            self.Data["specialPositionsUsed"].append(self.left.specialPosition)
    
    def closeHands(self):
        self.right.closeHand()
        self.left.closeHand()
    
    # métodos específicos
    def chooseFinger():
        pass

class PlayerHuman(Player):
    def chooseFinger(self, finger: str):
        self.chosenFinger = finger

class PlayerCPURandom(Player):
    def chooseFinger(self, fingerList: list[str]):
        self.chosenFinger = fingerList[rng.randint(0,len(fingerList) - 1)]

class PlayerCPUDif(Player):
    def __init__(self, playerId: int, dif: int):
        super().__init__(playerId)
        self.dif: int = dif

    def chooseFinger(self, fingerList: list[str]):
        # TEMPORALMENTE el mismo de CPURandom
        self.chosenFinger = fingerList[rng.randint(0,len(fingerList) - 1)]