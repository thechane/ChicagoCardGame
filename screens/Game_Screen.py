import _pickle as cPickle
import gc
# #todo, remove for prod - debugging only
# import pprint
# import guppy import hpy
import inspect
import random
from copy import copy
from os import listdir
from os.path import isfile, join

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.logger import Logger
from kivy.metrics import Metrics, inch
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen

from brains.Brain import Brain
from brains.Common import (
    Widget_ToTop,
    Get_Next_Player,
    Get_Config_Bool,
    Configed_Bool,
    Goto_Link,
)  # , Debug_Mem
from brains.Particle import Particle


class Game_Screen(Screen):
    # #positional offsets
    circleXoffset = 0
    circleYoffset = 0
    xCardVector = 0.2
    yCardVector = 0.245
    circleScale = 0.2
    portrait = None
    smallScreen = None
    bigScreen = None
    showdownDropYoffset = 0
    # #Kivy Properties
    flashText = StringProperty("")  # #Text for the flash boxes
    infoText = StringProperty("")  # #Text for the scoring drop down
    dCardsize = ListProperty([])  # #Contains the size of the dis Cards
    currentPlayer = NumericProperty(1)  # #current active player

    def __init__(self, **kwargs):  # #Override Screen's constructor
        Logger.info("Game_Screen init Fired")
        super(
            Game_Screen, self
        ).__init__()  # #but also run parent class constructor (__init__)
        # self.hp = hpy()                                            ##Memory profiler
        # #Is false until first Main_Float_Resize (delayed) fires
        self.init = True
        self.holdIt = True
        self.tutor = None
        # prevents binding callback to call / don't call Chicago buttons more than once
        self.boundChicagoButtons = False
        self.tutorialRefPress = (
            False  # Prevents multiple bindings for tutorial link refs
        )
        self.dealingCards = False  # #active when cards are being dealt out
        self.flashTrigger = Clock.create_trigger(self._Flash_Box)
        self.smallCardOffset = (
            (0.13, 0.23),  # p1c0Image
            (0.105, 0.26),  # p1c1Image
            (0.07, 0.29),  # p1c2Image
            (0.045, 0.32),  # p1c3Image
            (0.02, 0.35),  # p1c4Image
            (0.03, 0.03),  # p2c0Image
            (0.055, 0.06),  # p2c1Image
            (0.08, 0.09),  # p2c2Image
            (0.105, 0.12),  # p2c3Image
            (0.13, 0.15),  # p2c4Image
            (0.17, 0.13),  # p3c0Image
            (0.145, 0.1),  # p3c1Image
            (0.115, 0.078),  # p3c2Image
            (0.095, 0.05),  # p3c3Image
            (0.07, 0.02),  # p3c4Image
            (0.17, 0.22),  # p4c0Image
            (0.14, 0.25),  # p4c1Image
            (0.11, 0.28),  # p4c2Image
            (0.085, 0.31),  # p4c3Image
            (0.06, 0.34),  # p4c4Image
        )
        self.chicago_sound = SoundLoader.load("./sounds/chicago.wav")
        self.clunk_sound = SoundLoader.load("./sounds/dropclunk.wav")
        self.showdown_win = SoundLoader.load("./sounds/zap.wav")
        self.glitch_sound = SoundLoader.load("./sounds/glitch.wav")
        self.tocktick_sound = SoundLoader.load("./sounds/tocktick.wav")
        self.ticktock_sound = SoundLoader.load("./sounds/ticktock.wav")
        self.move_sound = SoundLoader.load("./sounds/move-card.wav")
        self.thud_sound = SoundLoader.load("./sounds/thud.wav")
        self.drop_sound = SoundLoader.load("./sounds/carddrop.wav")
        self.tap_sound = SoundLoader.load("./sounds/tap.wav")
        self.tap_sound = SoundLoader.load("./sounds/tap.wav")
        self.dealCard_sound = SoundLoader.load(
            "./sounds/dealing-card.wav"
        )  # #https://www.freesound.org/people/f4ngy/ (no edits)
        self.cheat_sound = SoundLoader.load("./sounds/cheat.wav")
        self.dealerPlayer = (
            kwargs.get("playerCount") - 1
        )  # #player that started last game
        self.stats = {}
        self.callChicago = []
        self.stats[
            "player"
        ] = {}  # #Either None or No, populated during chicago decision round
        self.setConfig = {
            "handCount": kwargs.get("handCount"),  # #Number of cards in a hand
            # #Number of opening poker rounds
            "pokerRoundCount": kwargs.get("rounds"),
            "pokerRoundScoring": kwargs.get(
                "pokerRoundScoring"
            ),  # #Score every poker round?
            "pokerAfterShowdownScoring": kwargs.get("pokerAfterShowdownScoring"),
            "chicagoTwo": kwargs.get(
                "chicagoTwo"
            ),  # #Score 25 if ending Chicago on a 2
            "cardExchangePointsLimit": kwargs.get("cardExchangePointsLimit"),
            "straightFlushValue": kwargs.get("straightFlushValue"),
            "fourOfaKindReset": kwargs.get("fourOfaKindReset"),
            "viewDiscards": kwargs.get("viewDiscards"),
            "negativeScoring": kwargs.get("negativeScoring"),
            "chicagoDestroy": kwargs.get("chicagoDestroy"),
        }  # #Score 8 points if you destroy a chicago
        Logger.info("DEBUG:setConfig:" + str(self.setConfig))
        self.cardFilePath = "./images/PNG-cards-1.3"
        self.files = [
            f for f in listdir(self.cardFilePath) if isfile(join(self.cardFilePath, f))
        ]  # List of files
        try:
            self.B = Brain(winner=kwargs.get("gameData")["winner"])
        except:
            self.B = Brain()
        if kwargs.get("gameData") is None:
            Logger.info("------------NEWGAME------------")
            kwargs["nextTurn"] = True
            self.Reset_Game(kwargs)

        else:
            # #Import saved data that's taken at the start of each human players End_Turn call
            self.hand = kwargs.get("gameData")["hand"]
            self.gameState = kwargs.get("gameData")["gameState"]
            self.currentPlayer = kwargs.get("gameData")["currentPlayer"]
            self.dealerPlayer = kwargs.get("gameData")["dealerPlayer"]
            self.setConfig = kwargs.get("gameData")["setConfig"]
            self.discardNumber = kwargs.get("gameData")["discardNumber"]
            self.stats = kwargs.get("gameData")["stats"]
            self.B.playerCantPlaySuit = kwargs.get("gameData")["brainSuits"]
            self.B.winner = kwargs.get("gameData")["winner"]

            # #tutorial can not be on unless new game
            App.get_running_app().config.set("General", "tutorial", False)

            # #adjust game state for the reload
            self.gameState["tmpActiveCard"] = None
            if self.gameState["activeCard"] is not None:
                self.ids["activeCardImage"].color = [1, 1, 1, 1]
                self.ids["activeCardImage"].source = (
                    self.cardFilePath
                    + "/"
                    + str(self.gameState["activeCard"][1])
                    + "_of_"
                    + self.gameState["activeCard"][2]
                    + ".png"
                )
            for pNum in self.hand:
                for cardNum, cardName in enumerate(self.hand[pNum]["showDownDiscards"]):
                    dCard = self.ids[
                        "p" + str(pNum) + "c" + str(cardNum) + "DiscardImage"
                    ]
                    dCard.source = self.cardFilePath + "/" + cardName
            self.gameState["doubleTapConfirm"] = False
            Logger.info(
                "Loaded in game data, current player now " +
                str(self.currentPlayer)
            )

            def nextP(dt):
                self.B.Next_Play(self)

            Clock.schedule_once(nextP, 3)

    def __del__(self):
        Logger.info("__del__ FIRED")
        self.holdIt = None
        self.setConfig = None
        self.chicago_sound = None
        self.showdown_win = None
        self.move_sound = None
        self.chunk_sound = None
        self.glitch_sound = None
        self.tocktick_sound = None
        self.ticktock_sound = None
        self.thud_sound = None
        self.drop_sound = None
        self.tap_sound = None
        self.dealCard_sound = None
        self.currentPlayer = 0
        self.dealerPlayer = None
        self.stats = None
        self.callChicago = None
        self.smallCardOffset = None
        self.cardFilePath = None
        self.files = None
        self.hand = None
        self.gameState = None
        self.currentPlaye = None
        self.dealerPlayer = None
        self.setConfig = None
        self.discardNumber = None
        self.B = None
        self.C = None

    def on_currentPlayer(self, x, y):
        Logger.info("on_currentPlayer fired:" + str(x) + ":" + str(y))
        if self.init is False:
            self.B.Next_Play(self)

    def on_leave(self):
        Logger.info("on_leave FIRED")
        self.holdIt = True
        if self.hand[self.currentPlayer]["cpu"] is False:
            for sID in self.hand[self.currentPlayer]["posindex"]:
                card = self.ids["card" + str(sID)]
                anim = Animation(
                    x=self.xpos_home[sID], y=0 - card.height, t="in_out_quad"
                )
                anim.start(card)

    def Check_Graphics(self):
        Logger.info("Check_Graphics FIRED")
        if Configed_Bool("General", "simplebackground") is True:
            self.ids["backGroundImage"].source = "./images/simpleTable.jpg"
        else:
            self.ids["backGroundImage"].source = "./images/greenTable.jpg"
        if Configed_Bool("General", "simplecardback") is True:
            self.cardSmallBackImagePath = "./images/back/simpleback_small.png"
            self.cardBackImagePath = "./images/back/simpleback.png"
        else:
            self.cardSmallBackImagePath = "./images/back/niceback_small.png"
            self.cardBackImagePath = "./images/back/niceback_medium.png"
            # self.cardSmallBackImagePath = './images/back/usa.png'
            # self.cardBackImagePath = './images/back/usa.png'
        for pNum in self.hand:
            for index in range(0, 5):
                self.ids[
                    "p" + str(pNum) + "c" + str(index) + "Image"
                ].source = self.cardSmallBackImagePath

    def on_enter(self):
        Logger.info("on_enter FIRED")
        self.Check_Graphics()
        iF = self.ids["infoFloat"]
        tI = self.ids["tableImage"]
        if Configed_Bool("General", "table") is True and tI not in iF.children:
            Logger.info("table image added")
            iF.add_widget(tI)
            Widget_ToTop(iF, self.ids["dealerLabel"])
            for pNum in self.hand:
                Widget_ToTop(iF, self.ids["p" + str(pNum) + "nameLabel"])
                for index in range(0, 5):
                    Widget_ToTop(
                        iF, self.ids["p" + str(pNum) +
                                     "c" + str(index) + "Image"]
                    )
                    Widget_ToTop(
                        iF,
                        self.ids["p" + str(pNum) + "c" +
                                 str(index) + "DiscardImage"],
                    )
        elif Configed_Bool("General", "table") is False and tI in iF.children:
            Logger.info("table image removed")
            iF.remove_widget(tI)
        if self.holdIt is True:
            def unHoldit(dt):
                self.holdIt = False

            Clock.schedule_once(unHoldit, 2)
            # self.hand[2]['score'] = 52
        if self.hand[self.currentPlayer]["cpu"] is False and self.init is False:
            for sID in self.hand[self.currentPlayer]["posindex"]:
                if self.hand[self.currentPlayer]["cardid"][sID] == "DONE":
                    continue
                anim = Animation(x=self.xpos_home[sID], y=0, t="in_out_quad")
                anim.start(self.ids["card" + str(sID)])

    def _Flash_Box(self, dt):
        fL = self.ids["flashLabel"]
        mF = self.ids["mainFloat"]
        xpos = (mF.width / 2) - (fL.width / 2)
        fL.pos = xpos, 0 - fL.height
        anim = Animation(x=xpos, y=fL.height, t="out_quint", d=0.3)
        anim = anim + Animation(x=xpos, y=fL.height + 10, d=1.2)
        anim = anim + Animation(x=xpos, y=fL.height - 10, d=1.2)
        anim = anim + Animation(x=xpos, y=0 - fL.height, t="in_quint", d=0.3)
        Widget_ToTop(mF, fL)
        anim.start(fL)

    def Flash_Box(self, message):
        Logger.info("Flash_Box FIRED")
        self.flashText = message
        if Configed_Bool("General", "sound") is True:
            self.glitch_sound.play()
        self.flashTrigger()

    def Tutorial_Text(self):
        def cardText(cardID):
            tmp = cardID.split("_of_")
            suitTmp = tmp[1].split(".")
            if tmp[0] == "11":
                tmp[0] = "jack"
            elif tmp[0] == "12":
                tmp[0] = "queen"
            elif tmp[0] == "13":
                tmp[0] = "king"
            elif tmp[0] == "14":
                tmp[0] = "ace"
            return "Suggested card to play, " + tmp[0] + " of " + suitTmp[0]

        if self.hand[self.currentPlayer]["cpu"] is True:
            return "... wait for the CPU players\nto finish their turns"
        elif self.gameState["controlPlayer"] is None:
            if self.hand[self.currentPlayer]["canDiscard"] is False:
                return "You can't exchange cards with\nthis many points - hit End Turn"
            elif self.gameState["roundNumber"] == self.setConfig["pokerRoundCount"]:
                return (
                    "Try to build a good showdown\nhand by discarding low value cards"
                )
            else:
                return "Try to build a good poker hand\nby discarding cards that do not help\noff the left or right of the screen"
        elif (
                self.gameState["controlPlayer"] is not None
                and self.gameState["chicago"] < 0
        ):
            # #Chicago Question
            if (
                    self.B.Chicago_Question(
                        self.setConfig, self.hand, self.currentPlayer)
                    is True
            ):
                return "Decent enough showdown hand\nsuggest calling Chicago"
            else:
                return "Weak showdown hand\nsuggest No Chicago call"
        elif self.gameState["chicago"] == self.currentPlayer:
            # #Chicago
            sID = self.B.Showdown_Turn_Self_Chicago(
                self.hand[self.currentPlayer]["cardid"]
            )
            return cardText(self.hand[self.currentPlayer]["cardid"][sID])
        elif self.gameState["chicago"] > 0:
            # #Other Chicago
            sID = self.B.Showdown_Turn_Other_Chicago(
                self.hand[self.currentPlayer]["cardid"],
                self.gameState["activeCard"],
                self.currentPlayer,
            )
            return cardText(self.hand[self.currentPlayer]["cardid"][sID])
        elif self.gameState["chicago"] == 0:
            # #Showdown without Chicago CPU play fired
            inControl = False
            if self.currentPlayer == self.gameState["controlPlayer"]:
                inControl = True
            sID = self.B.Showdown_Turn_No_Chicago(
                self.hand[self.currentPlayer]["cardid"],
                self.gameState["activeCard"],
                inControl,
                self.currentPlayer,
            )
            return cardText(self.hand[self.currentPlayer]["cardid"][sID])

    def Hide_Tutorial(self):
        self.ids["tutorialLO"].clear_widgets()
        self.ids["tutorialLO2"].clear_widgets()
        if self.init is True:
            return True
        elif self.tutor == "showdownEnd":
            App.get_running_app().config.set("General", "tutorial", False)
            self.ids["helpButton"].disabled = False
        elif self.tutor == "start":
            self.Show_Tutorial(**{"tutor": "poker1"})
        else:
            self.ids["helpButton"].disabled = False

    def Show_Tutorial(self, **kwargs):
        tutorials = (
            "start",
            "poker1",
            "poker2",
            "poker3",
            "poker4",
            "chicagoQuestion",
            "showdownStart",
            "showdownEnd",
        )
        Logger.info(
            "Show_Tutorial FIRED from "
            + str(inspect.stack()[2][3])
            + "("
            + str(inspect.stack()[2][2])
            + ") - kwargs = "
            + str(kwargs)
        )
        tFile = "./tutorial/help.markup"
        if kwargs.get("tutor") in tutorials:
            self.tutor = kwargs.get("tutor")
            tFile = "./tutorial/" + self.tutor + ".markup"
        self.ids["helpButton"].disabled = True
        try:
            self.ids["tutorialLO"].add_widget(self.ids["tutorialLabelPadding"])
            self.ids["tutorialLO2"].add_widget(
                self.ids["closeTutorialButtonPadding"])
            self.ids["tutorialLO"].add_widget(self.ids["svID"])
            # self.ids['tutorialLO'].add_widget(self.ids['tutorialLabel'])
            self.ids["tutorialLO2"].add_widget(self.ids["closeTutorialButton"])
            self.ids["tutorialLO"].add_widget(
                self.ids["tutorialLabelPadding2"])
            self.ids["tutorialLO2"].add_widget(
                self.ids["closeTutorialButtonPadding2"])
        except:
            Logger.error("tutorial widgets already present")
        with open(tFile, "r") as myfile:
            data = myfile.read()
        if Metrics.dpi_rounded >= 320 and self.portrait is False:
            data = data.replace("TITLESIZE", str("15sp"))
            data = data.replace("NORMALSIZE", str("14sp"))
        elif Metrics.dpi_rounded >= 320:
            data = data.replace("TITLESIZE", str("14sp"))
            data = data.replace("NORMALSIZE", str("13sp"))
        else:
            data = data.replace("TITLESIZE", str("18sp"))
            data = data.replace("NORMALSIZE", str("16sp"))
        data = data.replace("GAMEHINTTXT", self.Tutorial_Text())
        self.ids["tutorialLabel"].text = data
        # Logger.info(data)
        self.ids["svID"].scroll_y = 1
        if self.tutorialRefPress is False:
            self.ids["tutorialLabel"].bind(on_ref_press=Goto_Link)
            self.tutorialRefPress = True

    def Reset_Game(self, kwargs):
        try:
            playerInfo = kwargs.get("players")
            playerCount = kwargs.get("playerCount")
        except:
            playerInfo = None
            playerCount = None
        Logger.info(
            "-----------------RESET FIRED---------------------" + str(kwargs))
        self.gameState = {
            "discards": set(),  # # empty set to hold the discard pile
            "deck": set(self.files),  # # set of cards that = filename
            "tmpActiveCard": None,  # #Stores temp version of activeCard for transition between turns
            # #Showdown active card (current scatterID,card value,card suit)
            "activeCard": None,
            "controlPlayer": None,  # #Player Number who is in control, set when showdown starts
            "tmpControlPlayer": None,  # #player who has stolen control mid showdown
            "roundNumber": 1,  # #current poker round number, = 0 when in showdown
            "discardFlag": False,  # #set to True each round and soon as any card is discarded
            "doubleTapConfirm": False,  # #set to true when a double tap hits the screen
            "chicago": -1  # #Chicago flag, -1 = N/A, -2 = decision round,
            # #0 = inactive, any other num = player who called it
        }
        # #Set up stats, if we can increment we're in business, otherwise init the data
        try:
            self.stats["plays"] += 1
        except:
            self.stats["player"] = {}
            self.stats["plays"] = 0
            for pNum in range(1, playerCount):
                self.stats["player"][pNum] = {
                    "pokerWins": 0,
                    "highestPokerHand": 0,
                    "showdownWins": 0,
                    "chicagoWins": 0,
                    "chicagoLosses": 0,
                }

        self.discardNumber = {}
        self.pressed_down = ListProperty([0, 0])
        self.pressed_up = ListProperty([0, 0])
        self.B.playerCantPlaySuit = ([], [], [], [])
        tmpHand = []
        tmpIndex = []

        if playerCount is None:  # new game
            playerCount = len(self.hand) + 1
        else:  # new round
            self.hand = {}

        for index in range(0, self.setConfig["handCount"]):
            tmpHand.append(None)
            tmpIndex.append(index)

        # #ensure we know the graphic settings first
        self.Check_Graphics()
        # #then reset the data
        for index in range(1, playerCount):
            cpu = False
            try:
                if int(kwargs.get("p" + str(index) + "CPU")) == 1:
                    cpu = True
            except:
                pass

            name = kwargs.get("Player" + str(index))
            score = 0
            canDiscard = True
            if playerInfo is None:
                cpu = self.hand[index]["cpu"]
                name = self.hand[index]["name"]
                canDiscard = self.hand[index]["canDiscard"]
            try:
                score = self.hand[index]["score"]
            except:
                pass

            self.hand[index] = {
                "cardid": copy(tmpHand),
                "posindex": copy(tmpIndex),
                "hand": None,  # #Name of hand (straight, pair...)
                "showDownDiscards": [],  # #stored cards discarded in the showdown
                # #score, highcard value, highcard suitvalue
                "handScore": (0, 0, 0),
                "score": score,  # #actual Chicago points total
                "canDiscard": canDiscard,
                "cpu": cpu,
                "chicagoed": False,
                "roundCount": 0,  # #how many poker rounds this player has done
                "risk": random.randint(
                    0, 9
                ),  # #0 takes little to no risks, 9 takes big risks
                "name": name,
            }
            self.stats["player"][index]["name"] = name
            self.discardNumber[index] = []
            self.Deal_Cards(index, None, None, None, None, None)
            Logger.info("Hand set for player " + str(index))
            Logger.info(str(self.hand[index]["hand"]))
        self.Update_Info(None)

        if self.init is False:
            self.holdIt = True
            gc.collect()
            # Logger.info('Unreachable objects:')
            # Logger.info(str(gc.collect()))
            # Logger.info('Remaining Garbage:')
            # Logger.info(str(pprint.pprint(gc.garbage)))
            self.Main_Float_Resize()

        if kwargs.get("nextTurn") is True:
            newPlayer = Get_Next_Player(self.dealerPlayer, len(self.hand))
            if newPlayer == self.currentPlayer:
                self.B.Next_Play(self)
            else:
                self.currentPlayer = newPlayer

    def Save_Game(self):
        Logger.info("Save_Game Fired")
        data = {
            "hand": copy(self.hand),
            "gameState": copy(self.gameState),
            "currentPlayer": copy(self.currentPlayer),
            "dealerPlayer": copy(self.dealerPlayer),
            "setConfig": copy(self.setConfig),
            "discardNumber": copy(self.discardNumber),
            "stats": copy(self.stats),
            "brainSuits": copy(self.B.playerCantPlaySuit),
            "winner": copy(self.B.winner),
        }
        try:
            f = open(App.get_running_app().user_data_dir + "/game.dat", "w")
            cPickle.dump(data, f)
            f.close()
        except:
            Logger.error("Save_Game Failed")

    def Recalc_Dealer(self):
        Logger.info("FIRED: Recalc_Dealer")
        iF = self.ids["infoFloat"]
        dealerXoffset = iF.height * self.circleScale / 6
        dealerYoffset = iF.height * self.circleScale / 3
        self.dealerPos = [
            [
                iF.center_x + dealerXoffset + self.circleXoffset,
                iF.center_y
                + (iF.height * self.circleScale)
                - self.circleYoffset
                + dealerYoffset,
            ],
            [
                iF.center_x + dealerXoffset + self.circleXoffset,
                iF.center_y
                + (iF.height * self.circleScale)
                - self.circleYoffset
                - dealerYoffset,
            ],
            [
                iF.center_x - dealerXoffset + self.circleXoffset,
                iF.center_y
                + (iF.height * self.circleScale)
                - self.circleYoffset
                - dealerYoffset,
            ],
            [
                iF.center_x - dealerXoffset + self.circleXoffset,
                iF.center_y
                + (iF.height * self.circleScale)
                - self.circleYoffset
                + dealerYoffset,
            ],
        ]
        Logger.info(
            "recalc dealer for player "
            + str(self.dealerPlayer)
            + " to:"
            + str(self.dealerPos)
        )
        self.Move_Dealer_Chip()

    def Recalc_Small_Cards(self):
        iF = self.ids["infoFloat"]
        counter = 0
        self.smallCardPos = []
        self.nameLabelPos = []
        for playerNum in self.hand:
            tmpList = []
            for _cardIndex in range(0, self.setConfig["handCount"]):
                x = 0
                if playerNum == 1 or playerNum == 2:
                    x = (
                        iF.center_x
                        + self.circleXoffset
                        + iF.height * self.smallCardOffset[counter][0]
                    )
                else:
                    x = (
                        iF.center_x
                        + self.circleXoffset
                        - iF.height * self.smallCardOffset[counter][0]
                    )
                y = (
                    iF.center_y
                    + iF.height * self.smallCardOffset[counter][1]
                    - self.circleYoffset
                )
                tmpList.append([x, y])
                counter = counter + 1
            self.smallCardPos.append(tmpList)

    def Recalc_Discard_Cards(self):
        iF = self.ids["infoFloat"]
        counter = 0
        self.discardCardPos = []
        customOffset = 0
        if self.portrait is False and self.smallScreen is False:
            customOffset = iF.width * 0.026
            self.dCardsize = iF.height * 0.13, iF.height * 0.21
        else:
            self.dCardsize = iF.height * 0.12, iF.height * 0.18
        xOffset = iF.height * self.circleScale + customOffset
        for playerNum in self.hand:
            tmpList = []
            if Get_Config_Bool(self.setConfig["viewDiscards"]) is True:
                xOffset = (iF.height * self.circleScale + customOffset) - self.ids[
                    "p1c0DiscardImage"
                ].width * 0.2
            for _cardIndex in range(0, self.setConfig["handCount"]):
                x = 0
                y = 0
                self.ids[
                    "p" + str(playerNum) + "c" +
                    str(_cardIndex) + "DiscardImage"
                ].size = self.dCardsize
                if Get_Config_Bool(self.setConfig["viewDiscards"]) is True:
                    xOffset = xOffset + \
                        self.ids["p1c0DiscardImage"].width * 0.2
                if playerNum == 2:
                    x = iF.center_x + self.circleXoffset + xOffset
                    y = (
                        iF.center_y
                        + (iF.height * self.circleScale)
                        - self.circleYoffset
                        + (iF.height * self.circleScale / 6)
                    )
                elif playerNum == 1:
                    x = iF.center_x + self.circleXoffset + xOffset
                    y = (
                        iF.center_y
                        + (iF.height * self.circleScale)
                        - self.circleYoffset
                        - (iF.height * self.circleScale)
                    )
                elif playerNum == 3:
                    x = (
                        iF.center_x + self.circleXoffset - xOffset - iF.height * 0.12
                    )  # iF.height calc must match Kivy file
                    y = (
                        iF.center_y
                        + (iF.height * self.circleScale)
                        - self.circleYoffset
                        - (iF.height * self.circleScale)
                    )
                elif playerNum == 4:
                    x = (
                        iF.center_x + self.circleXoffset - xOffset - iF.height * 0.12
                    )  # iF.height calc must match Kivy file
                    y = (
                        iF.center_y
                        + (iF.height * self.circleScale)
                        - self.circleYoffset
                        + (iF.height * self.circleScale / 6)
                    )
                tmpList.append([x, y])
                counter = counter + 1
            if playerNum == 1 or playerNum == 2:
                self.discardCardPos.insert(0, tmpList)
            else:
                self.discardCardPos.append(tmpList)
        Logger.info("recalced discardCardPos: " + str(self.discardCardPos))

    def Deal_Smallcards(self, index):
        Logger.info("Deal_Smallcards fired with index " + str(index))
        # Logger.info('deal_smallcards fired -- INDEX = ' + str(index))
        self.dealingCards = True

        def callback(a, w):
            self.Deal_Smallcards(index + 1)
            return True

        if index < self.setConfig["handCount"] * len(self.hand):
            self.ids["endTurnButton"].disabled = True
            self.ids["yesChicagoButton"].disabled = True
            self.ids["noChicagoButton"].disabled = True
            playerOffset = int(index / self.setConfig["handCount"]) + 1
            player = None
            if self.dealerPlayer + playerOffset > len(self.hand):
                player = self.dealerPlayer + playerOffset - len(self.hand)
            else:
                player = self.dealerPlayer + playerOffset
            card = index % self.setConfig["handCount"]
            anim = None
            Logger.info("Anim for player " +
                        str(player) + " card " + str(card))
            scW = self.ids["p" + str(player) + "c" + str(card) + "Image"]
            if player > len(self.hand) or self.hand[player]["cardid"][card] == "DONE":
                # #if the card is done do not move it
                anim = Animation(x=scW.pos[0], y=scW.pos[1], d=0.1)
            else:
                anim = Animation(
                    x=self.smallCardPos[player - 1][card][0],
                    y=self.smallCardPos[player - 1][card][1],
                    d=0.1,
                    t="in_out_quad",
                )
            anim.bind(on_complete=callback)
            # #first position small card relative to dealer
            scW.pos = self.Position_Small_Card_Offscreen(scW)
            # #Then start the recursive animation call
            anim.start(scW)
            return True
        else:
            self.dealingCards = False

    def Position_Small_Card_Offscreen(self, scW):
        iF = self.ids["infoFloat"]
        if self.dealerPlayer == 1:
            return iF.width + scW.width * 2, iF.height + scW.height * 2
        elif self.dealerPlayer == 2:
            return iF.width + scW.width * 2, 0 - scW.height * 2
        elif self.dealerPlayer == 3:
            return 0 - scW.width * 2, 0 - scW.height * 2
        elif self.dealerPlayer == 4:
            return 0 - scW.width * 2, iF.height + scW.height * 2

    def Move_Dealer_Chip(self):
        dealerAnim = Animation(
            x=self.dealerPos[int(self.dealerPlayer) - 1][0],
            y=self.dealerPos[int(self.dealerPlayer) - 1][1],
            d=0.5,
        )
        dealerAnim.start(self.ids["dealerLabel"])

    def Main_Float_Resize(self):
        Logger.info("Main_Float_Resize fired")
        buttonState = [False, False]
        showHand = False
        if self.hand[self.currentPlayer]["cpu"] is False and self.init is False:
            showHand = True
        if self.ids["endTurnButton"].disabled is True:
            buttonState[0] = True
        else:
            self.ids["endTurnButton"].disabled = True
        if self.ids["yesChicagoButton"].disabled is True:
            buttonState[1] = True
        else:
            self.ids["yesChicagoButton"].disabled = True
            self.ids["noChicagoButton"].disabled = True
        self.refs = [
            self.ids["tutorialLabelPadding"].__self__,
            self.ids["closeTutorialButtonPadding"].__self__,
            self.ids["tutorialLabel"].__self__,
            self.ids["closeTutorialButton"].__self__,
            self.ids["tutorialLabelPadding2"].__self__,
            self.ids["closeTutorialButtonPadding2"].__self__,
            self.ids["tableImage"].__self__,
            self.ids["svID"].__self__,
        ]
        self.Hide_Tutorial()

        def Delayed_Resize(dt):
            # #Dealer Chip pos
            Logger.info("Delayed_Resize FIRED")
            self.Update_Player_Circle()
            self.Recalc_Dealer()
            # self.ids['dealerLabel'].pos = self.dealerPos[int(self.dealerPlayer) - 1][0],self.dealerPos[int(self.dealerPlayer) - 1][1]
            # #smallCard positions
            self.Recalc_Small_Cards()
            self.Recalc_Discard_Cards()
            # #DEAL SMALLCARDS giving them 2 seconds to wait since we want layout sizes fully calculated
            self.Deal_Smallcards(0)
            # if the small dis cards are on the screen, re adjust them
            for playerNum in self.hand:
                plab = self.ids["p" + str(playerNum) + "nameLabel"]
                if self.smallScreen:
                    plab.font_size = "14sp"
                else:
                    plab.font_size = "20sp"
                for index in self.hand[playerNum]["posindex"]:
                    dCard = self.ids[
                        "p" + str(playerNum) + "c" +
                        str(index) + "DiscardImage"
                    ]
                    if (
                            "/back/" not in dCard.source
                    ):  # #If not showing the back of a card
                        animDiscard = Animation(
                            x=self.discardCardPos[playerNum - 1][index][0],
                            y=self.discardCardPos[playerNum - 1][index][1],
                            t="in_out_quad",
                        )
                        animDiscard.start(dCard)
            # #see on_touch_up for usage of:
            self.card_xsize_rightvector = self.ids["card0"].size[0] * 0.9
            self.card_xsize_leftvector = self.ids["card0"].size[0] * 0.1
            self.card_ysize_bottomvector = self.ids["card0"].size[1] * 0.60
            self.card_ysize_vector = self.ids["card0"].size[1] * 0.5
            if buttonState[0] is False and self.gameState["controlPlayer"] is None:
                self.ids["endTurnButton"].disabled = False
            if buttonState[1] is False:
                self.ids["yesChicagoButton"].disabled = False
                self.ids["noChicagoButton"].disabled = False
            if showHand is True:
                self.B.Next_Play(self)
            if self.init is True and Configed_Bool("General", "tutorial") is True:
                self.Show_Tutorial(**{"tutor": "start"})
            self.holdIt = False
            self.init = False

        Clock.unschedule(Delayed_Resize, all=True)
        Clock.schedule_once(Delayed_Resize, 2)
        self.Update_Info(None)

    def on_size(self, screen, size):
        Logger.info(
            "on_size fired, "
            + str(screen)
            + ","
            + str(size)
            + ","
            + str(self.width)
            + ","
            + str(self.height)
        )
        if self.width < self.height:
            self.portrait = True
        else:
            self.portrait = False
        smallWidth = inch(2.5)
        bigWidth = inch(7)
        if self.portrait is False:
            smallWidth = inch(3.5)
            bigWidth = inch(10)
        if self.width <= smallWidth:
            self.smallScreen = True
            self.bigScreen = False
        elif self.width >= bigWidth:
            self.bigScreen = True
            self.smallScreen = False
        else:
            self.smallScreen = False
            self.bigScreen = False
        # #Flag to stop other on screen positioning routines
        Logger.info(
            "Screen Flags, bigScreen = "
            + str(self.bigScreen)
            + ", smallScreen = "
            + str(self.smallScreen)
        )
        self.holdIt = True
        self.Screen_Size_Calcs()
        self.Main_Float_Resize()

    def Screen_Size_Calcs(self):
        # #use this to repos activeCardImage, showDownLabel + all game info graphics and font sizes
        Logger.info("Screen_Size_Calcs fired")
        if (self.width <= self.height + self.width * 0.1) and (
                self.width >= self.height - self.width * 0.1
        ):
            # #~ square
            Logger.info("Square")
            try:
                self.ids["tableImage"].size_hint = 0.65, 0.55
                self.circleXoffset = self.width / 4
                self.circleYoffset = self.height / 10
                self.showdownDropYoffset = self.height / 3.5
            except:
                pass
            self.xCardVector = 0.18
            self.yCardVector = 0.28
        elif self.width > self.height:
            # #Landscape
            # #repos info and showdown drop
            Logger.info("Landscape")
            try:
                self.ids["tableImage"].size_hint = 0.5, 0.55
                self.circleXoffset = self.width / 4
                self.circleYoffset = self.height / 10
                self.showdownDropYoffset = self.height / 3.5
            except:
                pass
            self.xCardVector = 0.15
            self.yCardVector = 0.35
        elif self.height > self.width:
            # #portrait
            Logger.info("Portrait")
            try:
                self.ids["tableImage"].size_hint = 1, 0.45
                self.circleXoffset = 0
                self.circleYoffset = 0
                self.showdownDropYoffset = 0
            except:
                pass
            self.xCardVector = 0.25
            self.yCardVector = 0.245
        try:
            for scatterID in self.hand[self.currentPlayer]["posindex"]:
                self.ids["card" + str(scatterID)].size_hint = (
                    self.xCardVector,
                    self.yCardVector,
                )
            self.ids["activeCardImage"].size_hint = self.xCardVector, self.yCardVector
            self.ids["showDownLabel"].size_hint = (
                self.xCardVector + 0.1,
                self.yCardVector + 0.055,
            )
        except:
            pass

        try:
            self.xpos_center = self.center_x - (self.ids["card0"].size[0] / 2)
            self.ypos_center = self.center_y - (self.ids["card0"].size[1] / 2)
        except:
            # #match to size hint in kv file
            self.xpos_center = self.center_x - \
                (self.width * self.xCardVector / 2)
            self.ypos_center = self.center_y - \
                (self.height * self.yCardVector / 2)
        # #Card home pos
        xpos = (self.width - self.width * 0.1) / 6
        self.xpos_home = [
            xpos - (xpos / 2),  # #card0 home x pos
            xpos * 2 - (xpos / 2),  # #card1 home x pos
            xpos * 3 - (xpos / 2),  # #card2 is central
            xpos * 4 - (xpos / 2),  # #card3 home x pos
            xpos * 5 - (xpos / 2),  # #card4 home x pos
        ]

        Logger.info("on_size finished")
        # #Hide Cards
        try:
            # #Move them off screen and show the Display Cards Button
            for scatterID in self.hand[self.currentPlayer]["posindex"]:
                self.ids["card" + str(scatterID)].pos = (
                    int(self.xpos_center),
                    0 - self.ids["card0"].size[1] * 2,
                )
        except:
            return False

    def on_touch_down(self, touch):
        Logger.info("on_touch_down FIRED")
        self.pressed_down = touch.pos
        super(Game_Screen, self).on_touch_down(touch)

        if self.manager.current != "gameScreen":
            return True
        elif self.ids["tutorialLO"].children:  # #if tutorial box is open
            return False
        elif self.ids["endTurnButton"].collide_point(*self.pressed_down) is True:
            return True
        # todo remove from production
        #         elif touch.is_triple_tap:
        #             self.hand[self.currentPlayer]['score'] += 10
        #             if Configed_Bool("General", "sound") is True:
        #                 self.cheat_sound.play()
        elif touch.is_double_tap:
            Logger.info("double tap: " + str(self.pressed_down))
            # #First off don't go showing CPU players hand
            if self.hand[self.currentPlayer]["cpu"] is True:
                return True
            # #Tell on touch up to allow the call through
            self.gameState["doubleTapConfirm"] = True
            # #... and flip the cards
            someCardsFaceDown = False
            for scatterID in self.hand[self.currentPlayer]["posindex"]:
                if self.hand[self.currentPlayer]["cardid"][scatterID] == "DONE":
                    continue
                cardImage = self.ids["card" + str(scatterID) + "Image"]
                if cardImage.source == self.cardBackImagePath:
                    someCardsFaceDown = True
                    break
            if someCardsFaceDown is True:
                for sID in self.hand[self.currentPlayer]["posindex"]:
                    if self.hand[self.currentPlayer]["cardid"][sID] == "DONE":
                        continue
                    cImage = self.ids["card" + str(sID) + "Image"]
                    cImage.source = (
                        self.cardFilePath
                        + "/"
                        + self.hand[self.currentPlayer]["cardid"][sID]
                    )
            else:
                # #otherwise blank the hand out if ALL are face up
                okToBlankAllCards = True
                for sID in self.hand[self.currentPlayer]["posindex"]:
                    if self.hand[self.currentPlayer]["cardid"][sID] == "DONE":
                        continue
                    cImage = self.ids["card" + str(sID) + "Image"]
                    if cImage.source == self.cardBackImagePath:
                        okToBlankAllCards = False
                        break
                if okToBlankAllCards is True:
                    for sID in self.hand[self.currentPlayer]["posindex"]:
                        if self.hand[self.currentPlayer]["cardid"][sID] == "DONE":
                            continue
                        cImage = self.ids["card" + str(sID) + "Image"]
                        cImage.source = self.cardBackImagePath
            # #ID hand and give fun text message if >= 1 pair and not in Showdown
            if self.gameState["controlPlayer"] is None:
                try:
                    self.Alarm_on_ID(
                        self.B.ID_Hand(self.hand[self.currentPlayer]["cardid"])
                    )
                except:
                    pass
            return False
        elif self.gameState["chicago"] == -2:
            return False
        elif (
                self.ids["infoLabel"].collide_point(*self.pressed_down) is True
                or self.ids["infoLabel2"].collide_point(*self.pressed_down) is True
                or self.ids["infoLabel3"].collide_point(*self.pressed_down) is True
        ):
            self.Display_Scores()
            return True
        # todo This routine is a bit crap - should improve
        elif (
                self.gameState["controlPlayer"] is not None
                and Get_Config_Bool(self.setConfig["viewDiscards"]) is True
        ):
            # #check for showdown discard card check
            for pNum in range(1, len(self.hand) + 1):
                for cNum in range(0, len(self.hand[pNum]["posindex"])):
                    tmp = "p" + str(pNum) + "c" + str(cNum) + "DiscardImage"
                    if self.ids[tmp].collide_point(*self.pressed_down) is True:
                        self.Display_Showdown_Cards(pNum, False)
                        return True
        else:
            Logger.info("pressed down:" + str(self.pressed_down))
        return True

    def Call_Chicago(self):
        self.gameState["chicago"] = copy(self.currentPlayer)
        self.gameState["controlPlayer"] = copy(self.currentPlayer)
        self.callChicago = []
        self.Update_Info(None)

    def Skip_Chicago(self):
        Logger.info("Skip_Chicago fired for player " + str(self.currentPlayer))
        if (
                self.hand[self.currentPlayer]["cpu"] is False
                and Configed_Bool("General", "sound") is True
        ):
            self.dealCard_sound.play()
        self.callChicago.append("No")
        faceUp = (None, None)
        newPlayer = None
        if self.callChicago.count("No") == len(self.hand):
            newPlayer = copy(self.gameState["controlPlayer"])
            self.callChicago = []
            self.gameState["chicago"] = 0
        else:
            newPlayer = Get_Next_Player(
                self.currentPlayer, len(list(self.hand.keys())))
        self.Update_Info(None)
        self.Anim_Cards_End_Turn(faceUp, newPlayer)

    def Display_Chicago_Buttons(self):
        Logger.info("Display_Chicago_Buttons fired")
        self.ids["endTurnButton"].disabled = True
        self.gameState["chicago"] = -2
        self.Display_Scores()
        if Configed_Bool("General", "sound") is True:
            self.chicago_sound.play()
        yb = self.ids["yesChicagoButton"]
        nb = self.ids["noChicagoButton"]
        Widget_ToTop(self.ids["mainFloat"], yb)
        Widget_ToTop(self.ids["mainFloat"], nb)
        yAnimIn = Animation(x=0 - yb.width, y=yb.pos[1], d=0.3)
        nAnimIn = Animation(
            x=self.ids["mainFloat"].width + nb.width, y=nb.pos[1], d=0.3
        )

        if Configed_Bool("General", "tutorial") is True:
            self.Show_Tutorial(**{"tutor": "chicagoQuestion"})

        if yb.pos[0] == 0 - yb.width:  # #if Button is not already displayed
            yAnimOut = Animation(x=0, y=yb.pos[1], d=0.3)
            nAnimOut = Animation(
                x=self.ids["mainFloat"].width - nb.width, y=nb.pos[1], d=0.3
            )

            def enYNButton(anim, widget):
                widget.disabled = False

            def common_button():
                yb.disabled = True
                nb.disabled = True
                yAnimIn.start(yb)
                nAnimIn.start(nb)
                if Configed_Bool("General", "tutorial") is True:
                    self.Show_Tutorial(**{"tutor": "showdownStart"})

            def yes_button_callback(instance):
                self.Display_Scores()
                common_button()
                self.Call_Chicago()
                return False

            def no_button_callback(instance):
                self.Display_Scores()
                common_button()
                self.Skip_Chicago()
                return False

            if self.boundChicagoButtons is False:
                yb.bind(on_release=yes_button_callback)
                nb.bind(on_release=no_button_callback)
                self.boundChicagoButtons = True
            yAnimOut.bind(on_complete=enYNButton)
            nAnimOut.bind(on_complete=enYNButton)
            yAnimOut.start(yb)
            nAnimOut.start(nb)

    def Move_All_Home(self, enableEndTurnFlag):
        Logger.info("Move_All_Home fired")
        if (
                self.gameState["controlPlayer"] is not None
                and self.gameState["tmpActiveCard"] is None
        ):
            self.ids["endTurnButton"].disabled = True
        if Configed_Bool("General", "sound") is True:
            self.move_sound.play()

        def Move_Home(scatterID, toXhomeIndex, toYpos, speed, lastCard):
            card = self.ids["card" + str(scatterID)]
            if Configed_Bool("General", "fastPlay") is True:
                speed = speed / 2
            anim = Animation(x=self.xpos_home[toXhomeIndex], y=toYpos, d=speed)

            def animation_complete(a, w):
                if enableEndTurnFlag is True and self.gameState["chicago"] > 0:
                    # #if in poker round only
                    if (
                            self.gameState["chicago"] < 1
                            and self.gameState["chicago"] > -2
                            and self.gameState["tmpControlPlayer"] is None
                            and self.gameState["controlPlayer"] is None
                            and self.hand[self.currentPlayer]["cpu"] is False
                    ):
                        self.ids["endTurnButton"].disabled = False

            if lastCard is True:
                anim.bind(on_complete=animation_complete)
            anim.start(card)
            cardImage = self.ids["card" + str(scatterID) + "Image"]
            if cardImage.source != self.cardBackImagePath:
                cardImage.source = (
                    self.cardFilePath
                    + "/"
                    + self.hand[self.currentPlayer]["cardid"][scatterID]
                )

        for cardxPos, scatterID in enumerate(self.hand[self.currentPlayer]["posindex"]):
            if self.hand[self.currentPlayer]["cardid"][scatterID] == "DONE" or (
                    self.gameState["tmpActiveCard"] is not None
                    and scatterID == self.gameState["tmpActiveCard"][0]
            ):
                continue
            lastCard = False
            if cardxPos == len(self.hand[self.currentPlayer]["posindex"]) - 1:
                lastCard = True
            Move_Home(scatterID, cardxPos, 0, 0.2, lastCard)
        self.Refocus_Cards()

    def on_touch_up(self, touch):
        Logger.info("on_touch_up FIRED")
        self.pressed_up = touch.pos
        super(Game_Screen, self).on_touch_up(touch)

        # #Check we are not pushing buttons or clicking above the card line
        if self.ids["tutorialLO"].children:  # #if tutorial box is open
            return False
        elif self.ids["endTurnButton"].collide_point(*self.pressed_up) is True:
            return True
        elif self.ids["menuButton"].collide_point(*self.pressed_up) is True:
            return True
        try:
            if (
                    self.pressed_down[1] > self.ids["card0"].size[1] + 10
                    and self.gameState["doubleTapConfirm"] is False
            ):
                return True
        except:
            pass
            # to combat this:
            # elif self.pressed_down[1] > self.ids['card0'].size[1] + 10 and self.gameState['doubleTapConfirm'] is False:
            # TypeError: 'kivy.properties.ListProperty' object has no attribute '__getitem__'

        # #If we are in showdown monitor the dropbox
        if (
                self.gameState["controlPlayer"] is not None
                and self.gameState["chicago"] >= 0
        ):
            box = self.ids["showDownLabel"]

            # #If a card has been discarded in middle box
            if box.collide_point(*self.pressed_up) is True:
                anim = Animation(
                    x=box.pos[0] + (box.width / 2) -
                    (self.ids["card0"].width / 2),
                    y=box.pos[1] + (box.height / 2) -
                    (self.ids["card0"].height / 2),
                    d=0.5,
                )
                self.ids["endTurnButton"].disabled = True
                for scatterID in self.hand[self.currentPlayer]["posindex"]:
                    # #skip if current card already active
                    if self.hand[self.currentPlayer]["cardid"][scatterID] == "DONE" or (
                            self.gameState["tmpActiveCard"] is not None
                            and self.gameState["tmpActiveCard"][0] == scatterID
                    ):
                        continue
                    card = self.ids["card" + str(scatterID)]
                    if card.collide_point(*self.pressed_up) is True:
                        cardID = self.B.ID_Card(
                            self.hand[self.currentPlayer]["cardid"][scatterID]
                        )
                        # #Check suits match if player has on available
                        if (
                                self.gameState["activeCard"] is not None
                                and self.gameState["activeCard"][2] != cardID[1]
                                and self.B.Does_Player_Have_Matching_Suit(
                                    self.hand[self.currentPlayer]["cardid"],
                                    self.gameState["activeCard"][2],
                                )
                                is True
                        ):
                            self.Flash_Box(
                                "Must play same\nsuit when available")
                        else:
                            self.gameState["tmpActiveCard"] = (
                                scatterID,
                                cardID[0],
                                cardID[1],
                            )

                            def enableETbutton(a, w):
                                self.ids["endTurnButton"].disabled = False

                            anim.bind(on_complete=enableETbutton)
                            anim.start(card)
                        self.Move_All_Home(True)
                        break
            else:
                if self.gameState["tmpActiveCard"] is not None:
                    for scatterID in self.hand[self.currentPlayer]["posindex"]:
                        card = self.ids["card" + str(scatterID)]
                        if (
                                card.collide_point(*self.pressed_up) is True
                                and self.gameState["tmpActiveCard"][0] == scatterID
                        ):
                            self.gameState["tmpActiveCard"] = None
                            self.Move_All_Home(False)
                            break

        # #REORDER HAND
        movedCard = False
        for cardxPos, scatterID in enumerate(self.hand[self.currentPlayer]["posindex"]):
            if self.hand[self.currentPlayer]["cardid"][scatterID] == "DONE" or (
                    self.gameState["tmpActiveCard"] is not None
                    and self.gameState["tmpActiveCard"][0] == scatterID
            ):
                continue
            card = self.ids["card" + str(scatterID)]
            if (
                    card.collide_point(*self.pressed_up) is False
            ):  # if last known up location does not collide with a card
                continue
            movedCard = True
            if (
                    (
                        card.pos[0] > int(
                            self.right - self.card_xsize_rightvector)
                        and card.pos[1] > self.card_ysize_vector
                    )
                    or (
                    card.pos[0] < 0 - self.card_xsize_leftvector
                    and card.pos[1] > self.card_ysize_vector
                    )
                    or (card.pos[1] < 0 - self.card_ysize_bottomvector)
            ):
                if self.gameState["controlPlayer"] is None:
                    self.Discard_Card(scatterID)
                    return
                else:
                    self.Flash_Box(
                        "No exchanging of cards\nduring the showdown")

            if self.Reorder_Hand(cardxPos, scatterID, card.pos[0]) is True:
                break

        # #MOVE CARDS TO NEW POSITIONS
        if movedCard is True:
            self.Move_All_Home(True)
        Logger.info("--------------DEBUGGING-------------------")
        Logger.info("CURRENTPLAYER = " + str(self.currentPlayer))
        for index in self.hand:
            Logger.info("HAND for player : " + self.hand[index]["name"])
            Logger.info(str(self.hand[index]["cardid"]))
            Logger.info("can discard = " + str(self.hand[index]["canDiscard"]))
            # Logger.info(str(self.hand[index]['posindex']))
            # Logger.info('showDownDiscards = ' + str(self.hand[index]['showDownDiscards']))
            # Logger.info('roundCount = ' + str(self.hand[index]['roundCount']))
            # Logger.info('stats = ' + str(self.stats['player'][index]))
            Logger.info("   ---   ")
        Logger.info("gameState:")
        Logger.info("roundNumber = " + str(self.gameState["roundNumber"]))
        Logger.info("activeCard = " + str(self.gameState["activeCard"]))
        Logger.info("tmpActiveCard = " + str(self.gameState["tmpActiveCard"]))
        Logger.info("chicago = " + str(self.gameState["chicago"]))
        Logger.info("controlPlayer = " + str(self.gameState["controlPlayer"]))
        Logger.info("tmpControlPlayer = " +
                    str(self.gameState["tmpControlPlayer"]))
        # Logger.info('discardFlag = ' + str(self.gameState['discardFlag']))
        # Logger.info('discardNumber lists = ' + str(self.discardNumber))
        # Logger.info('doubleTapConfirm = ' + str(self.gameState['doubleTapConfirm']))
        Logger.info("screens = " + str(self.manager.screen_names))
        Logger.info("small screen = " + str(self.smallScreen))
        Logger.info("screen portrate = " + str(self.portrait))
        Logger.info("big screen = " + str(self.bigScreen))
        Logger.info("------------------------------------------")
        return True

    def Reorder_Hand(self, cardStartPos, scatterID, xpos):
        Logger.info(
            "Reorder_Hand Fired, Pos Index:"
            + str(self.hand[self.currentPlayer]["posindex"])
        )
        newPosIndex = []
        for index in range(0, self.setConfig["handCount"]):
            newPosIndex.append(None)
        madeSwitch = False
        # Have we gone left or right?
        if xpos < self.xpos_home[cardStartPos]:
            Logger.info("We are going left")
            counter = 0
            for cardPos in range(0, self.setConfig["handCount"]):
                counter += 1
                # if card are not the same and moved scatter xpos is < (left) of the current home pos
                if newPosIndex[cardPos] != scatterID and xpos < self.xpos_home[cardPos]:
                    madeSwitch = True
                    Logger.info(
                        "madeSwitch (positions):"
                        + str(cardStartPos)
                        + "->"
                        + str(cardPos)
                    )
                    newPosIndex[cardPos] = scatterID
                    break
                else:
                    newPosIndex[cardPos] = copy(
                        self.hand[self.currentPlayer]["posindex"][cardPos]
                    )
            for index in range(counter, cardStartPos + 1):
                newPosIndex[index] = copy(
                    self.hand[self.currentPlayer]["posindex"][index - 1]
                )
            for index in range(cardStartPos + 1, self.setConfig["handCount"]):
                newPosIndex[index] = copy(
                    self.hand[self.currentPlayer]["posindex"][index]
                )
        else:
            Logger.info("We are going right")
            counter = self.setConfig["handCount"]
            for cardPos in reversed(range(0, self.setConfig["handCount"])):
                counter -= 1
                # if card are not the same and moved scatter xpos is < (left) of the current home pos
                if newPosIndex[cardPos] != scatterID and xpos > self.xpos_home[cardPos]:
                    madeSwitch = True
                    Logger.info(
                        "madeSwitch (positions):"
                        + str(cardStartPos)
                        + "->"
                        + str(cardPos)
                    )
                    newPosIndex[cardPos] = scatterID
                    break
                else:
                    newPosIndex[cardPos] = copy(
                        self.hand[self.currentPlayer]["posindex"][cardPos]
                    )
            for index in range(counter - 1, cardStartPos - 1, -1):
                newPosIndex[index] = copy(
                    self.hand[self.currentPlayer]["posindex"][index + 1]
                )
            for index in range(cardStartPos - 1, -1, -1):
                newPosIndex[index] = copy(
                    self.hand[self.currentPlayer]["posindex"][index]
                )
        if madeSwitch:
            self.hand[self.currentPlayer]["posindex"] = newPosIndex
        return madeSwitch

    def Deal_Cards(self, playerNumber, *discarded):
        Logger.info(
            "Deal_Cards Fired, player num:"
            + str(playerNumber)
            + ", discards = "
            + str(discarded)
        )
        self.dealingCards = True
        # Logger.info('Deal_Cards Fired for player ' + str(playerNumber))
        newCards = []
        if len(self.gameState["deck"]) < len(
                discarded
        ):  # #If deck is running too low and we have more discarded cards than we can replace
            newCards = list(self.gameState["deck"])  # #give deck to newCards
            self.gameState["deck"] = self.gameState[
                "discards"
            ]  # #put the discards back into the deck (remember they are given out randomly unlike in real life
            self.gameState["discards"] = set()  # #and then empty the
            newCards = newCards + random.sample(
                sorted(self.gameState["deck"]), len(discarded) - len(newCards)
            )
        else:
            newCards = random.sample(
                sorted(self.gameState["deck"]), len(discarded))
        self.gameState["deck"] = self.gameState["deck"] - set(newCards)
        if (
                discarded[0] is not None
        ):  # #Since none will only be possible is all discards are None (new game)
            self.gameState["discards"] = self.gameState["discards"] | set(
                discarded)

        for discard in discarded:
            for index, card in enumerate(self.hand[playerNumber]["cardid"]):
                if discard is card:
                    self.hand[playerNumber]["cardid"][index] = newCards.pop()
                    cardImage = self.ids["card" + str(index) + "Image"]
                    # cardImage.source = self.cardFilePath + '/' + self.hand[playerNumber][index]
                    cardImage.source = self.cardBackImagePath
                    if self.ids["card0"].pos[1] > 0 - self.ids["card0"].height:
                        self.Center_Pos(index)
                    break
        self.dealingCards = False
        # Logger.info('DECK')
        # Logger.info( str(len(self.gameState['deck'])) )
        # Logger.info( str(set(self.gameState['deck'])) )
        # Logger.info('DISCARDS (' + str(len(self.gameState['discards'])) + ')')
        # Logger.info( str(set(self.gameState['discards'])) )

    def Blank_Card(self, scatterID):
        cardImage = self.ids["card" + str(scatterID) + "Image"]
        cardImage.source = self.cardBackImagePath

    # #forces reordering of widget tree to keep the x-index for the scatters as we want them
    def Refocus_Cards(self):
        layout = self.ids["mainFloat"]
        for scatterID in self.hand[self.currentPlayer]["posindex"]:
            card = self.ids["card" + str(scatterID)]
            Widget_ToTop(layout, card)

    def Center_Pos(self, cardNumber):
        card = self.ids["card" + str(cardNumber)]
        anim = Animation(
            x=self.xpos_center + cardNumber * 20, y=self.ypos_center, d=0.2
        )
        anim.start(card)

    def Discard_Card(self, scatterID):
        Logger.info("Discard_Card fired")
        if self.hand[self.currentPlayer]["canDiscard"] is False:
            self.Flash_Box(
                "No more discards allowed\nonce score is at or above "
                + str(self.setConfig["cardExchangePointsLimit"])
            )
            self.Center_Pos(scatterID)
            return

        if (
                self.gameState["doubleTapConfirm"] is True
                and self.gameState["discardFlag"] is True
        ):
            self.Flash_Box("No more discards\nallowed for this round")
            self.Center_Pos(scatterID)
            return
        elif self.gameState["doubleTapConfirm"] is True:
            self.gameState[
                "doubleTapConfirm"
            ] = False  # #discardFlag must be False and so we can cancel this doubleTapConfirm

        if len(self.discardNumber[self.currentPlayer]) >= 5:
            self.Flash_Box(
                "You can not discard the\nsame card twice in one round")
            self.Center_Pos(scatterID)
            return
        elif scatterID in self.discardNumber[self.currentPlayer]:
            self.Flash_Box("You can only discard\ncards once per round")
            self.Center_Pos(scatterID)
            return
        if Configed_Bool("General", "sound") is True:
            self.drop_sound.play()
        self.gameState["discardFlag"] = True

        def dealIt(dt):
            self.discardNumber[self.currentPlayer].append(scatterID)
            self.Deal_Cards(
                self.currentPlayer, self.hand[self.currentPlayer]["cardid"][scatterID]
            )

        Clock.schedule_once(dealIt, 0.3)

    def Alarm_on_ID(self, result):
        Logger.info("Alarm_on_ID fired")
        if result[1] > 1000 and self.hand[self.currentPlayer]["hand"] != result[0]:
            self.Fun_Text(result[0], self.currentPlayer, "yellow", 1)
            self.hand[self.currentPlayer]["hand"] = result[0]
            # play sound if no other human players
            otherHumans = False
            for p in self.hand:
                if p == self.currentPlayer:
                    continue
                if self.hand[p]["cpu"] is False:
                    otherHumans = True
                    break
            if otherHumans is False:
                if Configed_Bool("General", "sound") is True:
                    self.tap_sound.play()

    def Fun_Text(self, text, player, color, delay):
        Logger.info("Fun_Text FIRED")
        with Particle(size_hint_x=0.01, width=self.ids["infoFloat"].width * 0.01) as P:
            effect = None
            if player is not None and Configed_Bool("General", "effects") is True:
                effect = self.B.Choose_Effect(text)
                if effect is not None:
                    nameLabel = self.ids["p" + str(player) + "nameLabel"]
                    xpos = nameLabel.pos[0] + nameLabel.width * 0.5
                    ypos = nameLabel.pos[1]
                    P.show(id=effect, x=xpos, y=ypos,
                           layout=self.ids["infoFloat"])
                    # P.show(id = effect, x = self.width * 0.5, y = self.height * 0.5 + P.height)
            Logger.info("effect = " + str(effect))

            def animation_complete(anim, widget):
                self.ids["mainFloat"].remove_widget(widget)
                if widget.doneCount == len(text) - 1:
                    self.holdIt = False
                    if effect is not None:
                        P.unshow(self.ids["infoFloat"])
                return True

            self.holdIt = True
            xpos = self.ids["infoFloat"].width * 0.075
            ypos = self.ids["infoFloat"].height * 0.8
            # #text adjustments
            if Configed_Bool("General", "effects") is True and (
                    ("showdown" in text) or ("unbeatable" in text)
            ):
                color = "blue"  # #yellow clashes with effects
            if Configed_Bool("General", "simplefuntext") is True:
                color = "simple" + color
                if self.smallScreen is True and Metrics.dpi_rounded < 320:
                    color = color + "25pt/"
                elif (
                        Metrics.dpi_rounded >= 240 and self.smallScreen is False
                ) or self.bigScreen is True:
                    color = color + "150pt/"
                else:
                    color = color + "50pt/"
            else:
                if self.smallScreen is True and Metrics.dpi_rounded < 320:
                    color = color + "50pt/"
                elif (
                        Metrics.dpi_rounded >= 240 and self.smallScreen is False
                ) or self.bigScreen is True:
                    color = color + "150pt/"
                else:
                    color = color + "100pt/"
            if self.portrait is True:
                ypos = self.ids["infoFloat"].height * 0.55

            height = 0
            width = None
            for doneCount, char in enumerate(text):
                l = Image()
                l.size_hint = None, None
                if char == " ":
                    xpos = self.ids["infoFloat"].width * 0.075
                    ypos = ypos - height
                else:
                    l.source = (
                        "./images/funtext/funtext" + color + char.lower() + ".png"
                    )
                    l.width = l.texture_size[0]
                    l.height = l.texture_size[1]
                    l.pos = 0 - l.width, ypos
                    self.ids["mainFloat"].add_widget(l)
                    l.doneCount = doneCount
                    anim = Animation(x=xpos, y=ypos, t="in_quad")
                    anim = anim + Animation(x=xpos, y=ypos + 10, d=delay)
                    anim = anim + Animation(
                        x=self.ids["mainFloat"].width + l.width,
                        y=ypos + 10,
                        t="in_expo",
                    )
                    anim.bind(on_complete=animation_complete)
                    anim.start(l)
                    if width is None and height == 0 and char != "_":
                        width = copy(l.width)
                        height = copy(l.height)
                    if char == "_":
                        xpos = xpos + width
                    else:
                        xpos = xpos + l.width

    def Update_Info(self, infoString):
        Logger.info("Update_Info FIRED")
        self.Update_Player_Circle()
        size = 20
        if self.bigScreen is True:
            size = 22
        padding = " "
        if self.portrait is False:
            padding = "  "
        if infoString is None:
            iString = (
                padding
                + "[size="
                + str(size)
                + "sp][color=0000ff]\n Scorecard\n[/color]"
            )
            iString += "[color=0000ff][/color]"
            for p in self.hand:
                iString += padding + "[color=0000ee] "
                iString += (
                    self.hand[p]["name"][0:7] + " : " +
                    str(self.hand[p]["score"])
                )
                if p == self.gameState["chicago"]:
                    iString += "[/color][color=ff0000] -CHICAGO"
                elif p == self.gameState["controlPlayer"]:
                    iString += "[/color][color=ffff00] -control"
                elif p == self.gameState["tmpControlPlayer"]:
                    iString += "[/color][color=caca00] -stealin"
                iString += "\n[/color]"
            if self.smallScreen is False:
                iString += "\n"
            if self.bigScreen is True:
                iString += "\n"
            iString += "\n[color=0000ee]"
            if self.gameState["controlPlayer"] is None:
                # #Poker Rounds
                if self.portrait is True and self.smallScreen is True:
                    iString += (
                        padding
                        + "[b]Pkr Rnd: "
                        + str(self.gameState["roundNumber"])
                        + "/"
                    )
                else:
                    iString += (
                        padding
                        + " [b]Poker Round: "
                        + str(self.gameState["roundNumber"])
                        + " of "
                    )
                iString += str(self.setConfig["pokerRoundCount"]) + "[/b]"
            elif self.gameState["activeCard"] is None and self.gameState["chicago"] < 0:
                # #Calling Chicago?
                if self.portrait is True and self.smallScreen is True:
                    iString += padding + "Chicago?"
                else:
                    iString += padding + " Call Chicago?"
            else:
                # #Showdown
                if self.portrait is True and self.smallScreen is True:
                    iString += (
                        padding
                        + "Ctl:"
                        + self.hand[self.gameState["controlPlayer"]
                                    ]["name"][0:7]
                    )
                else:
                    iString += (
                        padding
                        + " Control:"
                        + self.hand[self.gameState["controlPlayer"]
                                    ]["name"][0:7]
                    )
                iString += (
                    "(" +
                    str(self.hand[self.gameState["controlPlayer"]]
                        ["score"]) + ")"
                )
            if self.smallScreen is True or (
                    self.smallScreen is False
                    and self.bigScreen is False
                    and self.portrait is False
            ):
                iString += "[/size][/color]"
            else:
                iString += "[/size][size=10sp]\n[/size][/color]"
            self.infoText = iString
        else:
            pass

    def Display_Scores(self):
        Logger.info("Display_Scores Fired")
        self.Update_Info(None)
        tB = self.ids["topBoxLayout"]
        il = self.ids["infoLabel"]
        tB2 = self.ids["topBoxLayout2"]
        topBut = self.ids["menuButton"]
        if (
                self.gameState["chicago"] == -2
        ):  # we want to extend further down due to larger
            topBut = self.ids["yesChicagoButton"]  # sized chicago buttons

        # #Calc the outYpos
        outYpos = (self.pos[1] + self.height) - il.height - topBut.height

        def upAnim(a, w):
            upA = Animation(x=il.pos[0], y=tB.pos[1], d=0.5)
            upA.start(il)

        def leftAnim(a, w):
            leftA = Animation(x=il.pos[0], y=tB.pos[1], d=0.5)
            leftA.start(self.ids["topBoxLayout2"])

        if il.pos[1] == outYpos:
            rightAnim = Animation(x=self.width, y=tB.pos[1], d=0.5)
            rightAnim.bind(on_complete=upAnim)
            rightAnim.start(tB2)
        elif il.pos[1] == tB.pos[1]:
            downAnim = Animation(x=il.pos[0], y=outYpos, d=0.5)
            downAnim.bind(on_complete=leftAnim)
            downAnim.start(il)
        return True

    def Display_Showdown_Cards(self, pNum, allFlag):
        Logger.info("Display_Showdown_Cards FIRED")
        mainFloat = self.ids["mainFloat"]

        def animation_complete(anim, widget):
            widget.parent.remove_widget(widget)
            return True

        cardList = copy(self.hand[pNum]["showDownDiscards"])
        if allFlag is True:
            for cardName in self.hand[pNum]["cardid"]:
                if cardName == "DONE":
                    continue
                cardList.append(cardName)
        for doneCount, cardName in enumerate(cardList):
            c = Image()
            c.size_hint = self.xCardVector, self.yCardVector
            c.source = self.cardFilePath + "/" + cardName
            xpos = self.xpos_center + (c.width * 0.25) * (
                len(self.hand[pNum]["showDownDiscards"]) - doneCount
            )
            yPos = self.ypos_center + c.height
            c.pos = mainFloat.width + c.width, yPos
            mainFloat.add_widget(c)
            anim = Animation(x=xpos, y=self.ypos_center, t="in_quad")
            anim = anim + Animation(x=xpos, y=yPos, d=2.5)
            anim = anim + Animation(x=c.width +
                                    mainFloat.width, y=yPos, t="in_expo")
            anim.bind(on_complete=animation_complete)
            anim.start(c)

    def Update_Player_Circle(self):
        Logger.info("Update_Player_Circle FIRED")
        for player in self.hand:
            plabel = self.ids["p" + str(player) + "nameLabel"]
            plabel.text = self.hand[player]["name"][0:7]
            if (
                    self.gameState["controlPlayer"] is not None
                    and player == self.gameState["controlPlayer"]
            ):
                plabel.color = 0.1, 1, 1, 1
            elif player == self.currentPlayer:
                # plabel.font_name = './fonts/Hack-Bold.ttf'
                plabel.color = 0.1, 0, 1, 1
            else:
                # plabel.font_name = './fonts/Hack-Regular.ttf'
                plabel.color = 0, 0, 0, 1
        # #Remove text for non players
        for player in range(4, len(self.hand), -1):
            plabel = self.ids["p" + str(player) + "nameLabel"]
            plabel.text = ""

    def End_Turn(self, **kwargs):
        newPlayer = copy(self.currentPlayer)
        self.ids["showDownLabel"].text = ""
        # #Check if game has been terminated
        # #this is a bit of a hack, when all CPU players and newgame starts - the game continues in the background along side the newgame
        # #somehow running without a screen
        try:
            if "gameScreen" in self.manager.screen_names:
                pass
        except:
            # #If this check fails that screen has terminated
            self.Reset_Game({"nextTurn": False, "killGame": True})
            self.clear_widgets()
            return False
        # #Prevents ending turn with no cards assigned
        if self.gameState["roundNumber"] == 1 and set(
                self.hand[self.currentPlayer]["cardid"]
        ) == set([None, None, None, None, None]):
            return True

        # #Prevent players from not entering a card during showdown
        if (
                self.gameState["controlPlayer"] is not None
                and self.gameState["controlPlayer"] == self.currentPlayer
                and self.gameState["tmpActiveCard"] == None
                and self.gameState["chicago"] >= 0
        ):
            self.ids["showDownLabel"].text = "Discard a card\nhere to continue"
            return

        Logger.info(
            "---------------ENDING TURN for player "
            + str(self.currentPlayer)
            + "----------------"
        )
        if (
                self.hand[self.currentPlayer]["cpu"] is False
                and Configed_Bool("General", "sound") is True
        ):
            self.dealCard_sound.play()
        Logger.info("chicago state = " + str(self.gameState["chicago"]))
        Logger.info("controlPlayer = " + str(self.gameState["controlPlayer"]))
        Logger.info("tmpControlPlayer = " +
                    str(self.gameState["tmpControlPlayer"]))
        Logger.info("activeCard = " + str(self.gameState["activeCard"]))
        Logger.info("tmpActiveCard = " + str(self.gameState["tmpActiveCard"]))
        Logger.info("poker round count = " +
                    str(self.setConfig["pokerRoundCount"]))
        Logger.info("round number = " + str(self.gameState["roundNumber"]))
        Logger.info(str(self.hand))

        def check_winner():
            # #Overall winner check
            for pNum in self.hand:
                if self.hand[pNum]["score"] >= 52:
                    Logger.info("We have a Winner!!!")
                    self.stats["winner"] = pNum
                    for pNum in range(1, len(self.hand) + 1):
                        self.stats["player"][pNum]["score"] = self.hand[pNum]["score"]
                    self.Save_Game()
                    self.manager.current = "gameOverScreen"
                    return True
            return False

        # #Touch up turns end button back on once hand is ready - forces tap confirm on endturn
        self.ids["endTurnButton"].disabled = True
        self.ids["yesChicagoButton"].disabled = True
        self.ids["noChicagoButton"].disabled = True

        newShowdownRound = False
        if (
                self.gameState["activeCard"] is None
                and self.gameState["controlPlayer"] is not None
        ):
            Logger.info("newShowdownRound detected and set")
            newShowdownRound = True

        faceUp = (None, None)
        showdownCompleteFlag = False

        if (
                self.gameState["controlPlayer"] is not None
                # #in Showdown / Chicago
                and self.gameState["tmpActiveCard"] is not None
                and (  # #and a card has been played
                self.gameState["activeCard"] is None
                or (  # #and no current active card OR
                    self.gameState["tmpActiveCard"][2]
                    == self.gameState["activeCard"][2]
                    # # cards suits match
                    and self.gameState["tmpActiveCard"][1]
                    > self.gameState["activeCard"][1]
                    # # top card value is greater
                )
                )
        ):
            if Configed_Bool("General", "sound") is True:
                self.tocktick_sound.play()
            self.gameState["activeCard"] = copy(
                self.gameState["tmpActiveCard"])
            faceUp = (
                self.gameState["tmpActiveCard"][0],
                copy(
                    self.hand[self.currentPlayer]["cardid"][
                        self.gameState["tmpActiveCard"][0]
                    ]
                ),
            )
            self.gameState["tmpActiveCard"] = None
            self.ids["activeCardImage"].color = [1, 1, 1, 1]
            self.ids["activeCardImage"].source = (
                self.cardFilePath
                + "/"
                + self.hand[self.currentPlayer]["cardid"][
                    self.gameState["activeCard"][0]
                ]
            )
            self.gameState["tmpControlPlayer"] = copy(self.currentPlayer)
            self.hand[self.currentPlayer]["showDownDiscards"].append(
                copy(
                    self.hand[self.currentPlayer]["cardid"][
                        self.gameState["activeCard"][0]
                    ]
                )
            )
            self.hand[self.currentPlayer]["cardid"][
                self.gameState["activeCard"][0]
            ] = "DONE"
            Logger.info(
                "tmpControlPlayer changed to " +
                str(self.gameState["tmpControlPlayer"])
            )
            self.ids["card" + str(self.gameState["activeCard"][0])].pos = (
                int(self.xpos_center),
                0 - self.ids["card0"].size[1] * 2,
            )
        elif (
                self.gameState["controlPlayer"] is not None
                # #in showdown / chicago
                and self.gameState["tmpActiveCard"] is not None
                # #card has been played but since above not true it is a discard in Chicago round
        ):
            if Configed_Bool("General", "sound") is True:
                self.ticktock_sound.play()
            if (
                    self.gameState["tmpActiveCard"][2] != self.gameState["activeCard"][2]
            ):  # #suits do not match
                self.B.playerCantPlaySuit[self.currentPlayer - 1].append(
                    self.gameState["activeCard"][2]
                )
            Logger.info("player " + str(self.currentPlayer) +
                        " does NOT take control")
            faceUp = (
                self.gameState["tmpActiveCard"][0],
                copy(
                    self.hand[self.currentPlayer]["cardid"][
                        self.gameState["tmpActiveCard"][0]
                    ]
                ),
            )
            # #animate discarded showdown card away to the dealer
            card = self.ids["card" + str(self.gameState["tmpActiveCard"][0])]
            dACanim = Animation(x=self.width + card.width,
                                y=card.pos[0], d=0.25)

            def donedACanim(a, w):
                # #move scatter back down under main hand and turn face down
                w.pos = [self.xpos_center, 0 - w.size[1] * 2]
                w.source = self.cardBackImagePath

            dACanim.bind(on_complete=donedACanim)
            dACanim.start(card)
            self.hand[self.currentPlayer]["showDownDiscards"].append(
                copy(
                    self.hand[self.currentPlayer]["cardid"][
                        self.gameState["tmpActiveCard"][0]
                    ]
                )
            )
            self.hand[self.currentPlayer]["cardid"][
                self.gameState["tmpActiveCard"][0]
            ] = "DONE"
            self.gameState["tmpActiveCard"] = None
        elif self.gameState["controlPlayer"] is None:
            # #reset non-showdown flags
            Logger.info("this is a poker round")
            self.gameState["doubleTapConfirm"] = False
            self.gameState["discardFlag"] = False
        elif self.gameState["tmpActiveCard"] is None:
            # #This should never happen
            pass

        # #Check for showdown status
        # None = middle of showdown, >0 means end showdown round, 0 = start of showdown
        showdownRoundCompleteFlag = None
        if (
                showdownCompleteFlag is False
                and newShowdownRound is False
                and self.gameState["controlPlayer"] is not None
                and self.gameState["tmpControlPlayer"] is not None
                and self.gameState["tmpControlPlayer"] != self.gameState["controlPlayer"]
                and self.gameState["chicago"] > 0
        ):
            showdownCompleteFlag = True
        if self.gameState["controlPlayer"] is not None:
            for pNum in self.hand:
                Logger.info(
                    "PlayerNum "
                    + str(pNum)
                    + " hand = "
                    + str(self.hand[pNum]["cardid"])
                )
                if showdownRoundCompleteFlag is None:
                    showdownRoundCompleteFlag = self.hand[pNum]["cardid"].count(
                        "DONE")
                elif showdownRoundCompleteFlag != self.hand[pNum]["cardid"].count(
                        "DONE"
                ):
                    showdownRoundCompleteFlag = None
                    break
            if showdownRoundCompleteFlag == 5:
                showdownCompleteFlag = True
        Logger.info("showdownCompleteFlag = " + str(showdownCompleteFlag))
        Logger.info("showdownRoundCompleteFlag = " +
                    str(showdownRoundCompleteFlag))

        if showdownCompleteFlag is True:
            Logger.info("DEBUGGING checks for showdown winner")
            if Configed_Bool("General", "tutorial") is True:
                self.Show_Tutorial(**{"tutor": "showdownEnd"})
            kwargs["debugSave"] = True
            if Configed_Bool("General", "sound") is True:
                self.showdown_win.play()
            winner = None
            if self.gameState["chicago"] > 0:
                Logger.info("Scoring CHICAGO showdown")
                if (
                        self.gameState["tmpControlPlayer"]
                        != self.gameState["controlPlayer"]
                ):
                    winner = self.gameState["tmpControlPlayer"]
                    if Configed_Bool("General", "sound") is True:
                        self.clunk_sound.play()
                    self.hand[self.gameState["chicago"]]["score"] = (
                        self.hand[self.gameState["chicago"]]["score"] - 15
                    )
                    self.stats["player"][self.gameState["chicago"]][
                        "chicagoLosses"
                    ] += 1
                    if (
                            self.hand[self.gameState["chicago"]]["score"] < 0
                            and Get_Config_Bool(self.setConfig["negativeScoring"]) is False
                    ):
                        self.hand[self.gameState["chicago"]]["score"] = 0
                    if Get_Config_Bool(self.setConfig["chicagoDestroy"]) is True:
                        self.hand[winner]["score"] += 8
                else:
                    winner = self.gameState["chicago"]
                    if (
                            Get_Config_Bool(
                                self.setConfig["chicagoTwo"]) is True
                            and self.gameState["activeCard"][1] == 2
                    ):
                        self.hand[winner]["score"] += 25
                    else:
                        self.hand[winner]["score"] += 15
                    self.stats["player"][winner]["chicagoWins"] += 1
                    self.hand[winner]["chicagoed"] = True
            else:
                winner = self.gameState["tmpControlPlayer"]
                Logger.info(
                    "Scoring NON-CHICAGO showdown, winner = " + str(winner))
                self.hand[winner]["score"] += 5
                self.stats["player"][winner]["showdownWins"] += 1
                if (
                        Get_Config_Bool(
                            self.setConfig["pokerAfterShowdownScoring"]) is True
                        and self.hand[self.currentPlayer]["score"] < 52
                ):
                    Logger.info("Scoring poker after showdown")
                    self.B.Score_Hand(
                        self.hand,
                        self.setConfig["straightFlushValue"],
                        Get_Config_Bool(self.setConfig["fourOfaKindReset"]),
                        self.stats,
                    )
            # # SHOWDOWN COMPLETE GLOBAL ROUTINE
            # #check if a player can still discard or not
            self.B.Set_canDiscard(
                self.hand, self.setConfig["cardExchangePointsLimit"])
            # #DEALER MOVE
            self.dealerPlayer = Get_Next_Player(
                self.dealerPlayer, len(list(self.hand.keys()))
            )
            self.Move_Dealer_Chip()
            self.Update_Player_Circle()
            Logger.info(
                "new dealer pos is player: " + str(self.dealerPlayer)
            )  # + 'pos: ' +  str(self.dealerPos[int(self.dealerPlayer) - 1][0]) + ', ' + str(self.dealerPos[int(self.dealerPlayer) - 1][1]))
            # #SHOW WINNER
            tmpText = " wins_the showdown"
            self.Fun_Text(
                self.B.Strip_Player(self.hand[winner]["name"]) + tmpText,
                winner,
                "yellow",
                2.5,
            )
            newPlayer = copy(self.dealerPlayer)

            def Now_Small_Cards(a, w):
                def done_animation(anim, widget):
                    Logger.info("done_animation fired")
                    self.ids["activeCardImage"].color = [0, 0, 0, 0]
                    sdl = self.ids["showDownLabel"]
                    c = self.ids["card0"]
                    self.ids["activeCardImage"].pos = sdl.pos[0] + (sdl.width / 2) - (
                        c.width / 2
                    ), sdl.pos[1] + (sdl.height / 2) - (c.height / 2)
                    # #RESET IF GAME IS OVER
                    self.Remove_dCards()
                    if check_winner() is False:
                        Logger.info(
                            "---------------Resetting game with current player "
                            + str(self.currentPlayer)
                            + "----------------"
                        )
                        self.Reset_Game({"nextTurn": True})
                    else:
                        self.Reset_Game({"nextTurn": False})

                for playerNum in self.hand:
                    for index in range(0, self.setConfig["handCount"]):
                        smallCard = self.ids[
                            "p" + str(playerNum) + "c" + str(index) + "Image"
                        ]
                        anim = Animation(
                            x=self.xpos_center,
                            y=0 - smallCard.height * 10,
                            t="in_out_quart",
                        )
                        # Logger.info( str(len(self.hand)) + str(len(self.hand[playerNum]['posindex'])) + str(playerNum) + str(index) )
                        if (
                                playerNum == len(self.hand)
                                and index == len(self.hand[playerNum]["posindex"]) - 1
                        ):
                            anim.bind(on_complete=done_animation)
                        anim.start(smallCard)

            yOffset = self.ids["card0"].size[1] * 2
            duration = 1
            if Configed_Bool("General", "fastPlay") is True:
                duration = 0.5
            for index in range(0, self.setConfig["handCount"]):
                card = self.ids["card" + str(index)]
                doneAnim = Animation(
                    x=int(self.xpos_center), y=0 - yOffset, d=duration)
                doneAnim.start(card)
            acAnim = Animation(x=int(self.xpos_center),
                               y=0 - yOffset, d=duration)
            acAnim.bind(on_complete=Now_Small_Cards)
            acAnim.start(self.ids["activeCardImage"])
            return False
        elif self.gameState["controlPlayer"] is None:  # #If poker round
            # #Update the current player and
            # #set roundNumber to 0 if Poker Rounds are done with
            if (
                    self.gameState["roundNumber"] >= self.setConfig["pokerRoundCount"]
                    and self.currentPlayer == self.dealerPlayer
            ):
                Logger.info(
                    "Poker rounds completed for this cycle - setting control player to "
                    + str(self.B.winner)
                )
                self.gameState["roundNumber"] = 0
                self.gameState["controlPlayer"] = copy(self.B.winner)
                if self.currentPlayer != self.gameState["controlPlayer"]:
                    newPlayer = copy(copy(self.B.winner))
            else:
                newPlayer = Get_Next_Player(self.currentPlayer, len(self.hand))
            Logger.info("player now = " + str(self.currentPlayer))

            # #Update current players (poker) roundCount
            self.hand[self.currentPlayer]["roundCount"] = self.gameState["roundNumber"]

            # #Figure if we need to roll onto the next round
            counter = 0
            for pNum in self.hand:
                if self.hand[pNum]["roundCount"] == self.gameState["roundNumber"]:
                    counter += 1
            if self.gameState["controlPlayer"] is None and counter == len(self.hand):
                self.gameState["roundNumber"] += 1
                Logger.info(
                    "roundNumber (poker) incremented to "
                    + str(self.gameState["roundNumber"])
                )
                for pNum in self.discardNumber:
                    self.discardNumber[pNum] = []

            # #show tutorial is needed
            if (
                    self.hand[self.currentPlayer]["cpu"] is False
                    and Configed_Bool("General", "tutorial") is True
                    and self.gameState["roundNumber"] > 1
                    and self.gameState["roundNumber"] < self.setConfig["pokerRoundCount"]
            ):
                num = copy(self.gameState["roundNumber"])
                if num == 4:
                    num = 3
                self.Show_Tutorial(**{"tutor": "poker" + str(num)})

            # #Now data has been updated, check Poker Scores and set start showdown by flagging a control player if needed
            if (
                    self.gameState["roundNumber"] == self.setConfig["pokerRoundCount"]
                    and self.dealerPlayer == self.currentPlayer
            ):
                if Configed_Bool("General", "tutorial") is True:
                    self.Show_Tutorial(**{"tutor": "poker4"})
                result = self.B.Score_Hand(
                    self.hand,
                    self.setConfig["straightFlushValue"],
                    Get_Config_Bool(self.setConfig["fourOfaKindReset"]),
                    self.stats,
                )
                self.Fun_Text(result, self.B.winner, "yellow", 1.5)
        else:
            # #Showdown round
            # #has someone stolen control?
            # #has the showdown round gone full circle
            if showdownRoundCompleteFlag is not None and showdownRoundCompleteFlag > 0:
                # #If someone else took control during the showdown round
                if self.gameState["tmpControlPlayer"] is not None:
                    Logger.info(
                        "control has switched from "
                        + str(self.gameState["controlPlayer"])
                        + " to "
                        + str(self.gameState["tmpControlPlayer"])
                    )
                    self.gameState["controlPlayer"] = copy(
                        self.gameState["tmpControlPlayer"]
                    )
                if self.gameState["activeCard"] is not None:
                    self.ids["activeCardImage"].color = [1, 1, 1, 0.5]
                self.gameState["activeCard"] = None

            if (
                    self.gameState["chicago"] > 0
                    and showdownRoundCompleteFlag is not None
                    and showdownRoundCompleteFlag > 0
            ):
                newPlayer = copy(self.gameState["chicago"])
                Logger.info("newPlayer assigned to chicago player")
            elif (
                    self.gameState["tmpControlPlayer"] is not None
                    and showdownRoundCompleteFlag is not None
                    and showdownRoundCompleteFlag > 0
            ):
                newPlayer = copy(self.gameState["tmpControlPlayer"])
                Logger.info("newPlayer assigned to tmpControlPlayer")
            else:
                newPlayer = Get_Next_Player(self.currentPlayer, len(self.hand))
                Logger.info("newPlayer assigned to Get_Next_Player")

            if self.gameState["chicago"] == -1:
                Logger.info("chicacgo decision round has started")
                self.gameState[
                    "chicago"
                ] = -2  # #set to denote decision round has started

        if check_winner() is True:
            self.Reset_Game({"nextTurn": False})
            return False

        # #Update the circle to reflect new info
        self.Update_Info(None)

        if showdownCompleteFlag is True:
            self.Update_Info(None)
            return False
        else:
            self.Anim_Cards_End_Turn(faceUp, newPlayer)
        self.Update_Info(None)
        return True

    def Remove_dCards(self):
        infoFloat = self.ids["infoFloat"]
        xPos = infoFloat.width + self.width
        yPos = infoFloat.height + self.height
        for playerNum in self.hand:
            for index in self.hand[playerNum]["posindex"]:
                dCard = self.ids[
                    "p" + str(playerNum) + "c" + str(index) + "DiscardImage"
                ]
                dCard.source = self.cardSmallBackImagePath
                animDiscard = Animation(x=xPos, y=yPos, t="in_out_quad")
                animDiscard.start(dCard)

    def Anim_Cards_End_Turn(self, faceUp, newPlayer):
        # #discover last card to leave the screen
        Logger.info(
            "Anim_Cards_End_Turn Fired, newPlayer = "
            + str(newPlayer)
            + ", current player is "
            + str(self.currentPlayer)
        )
        layout = self.ids["infoFloat"]
        lastScatter = None
        tmpList = []
        for scatterID in self.hand[self.currentPlayer]["posindex"]:
            if self.hand[self.currentPlayer]["cardid"][scatterID] == "DONE":
                continue
            tmpList.append(scatterID)
            lastScatter = scatterID
        Logger.info("lastScatter = " + str(lastScatter) +
                    ", tmpList = " + str(tmpList))

        # copy the currentPlayer so when we return after changig it, we continue with original value
        cPlayer = copy(self.currentPlayer)

        def nextTurn(a, w):
            Logger.info("Anim_Cards_End_Turn completed")
            if newPlayer is not None and self.currentPlayer != newPlayer:
                self.currentPlayer = newPlayer
            else:
                self.B.Next_Play(self)

        # #if cPlayers hand is all DONE then just proceed to the next turn
        if not tmpList:
            Logger.info("Current Player " + str(cPlayer) +
                        " has all DONE cards")
            nextTurn(None, None)
            return False

        # #create anim for sending the small cards back on screen
        def return_smallcards(a, w):
            Logger.info(
                "return_smallcards fired wth w.sID = "
                + str(w.sID)
                + " and lastScatter = "
                + str(lastScatter)
            )
            # now card is off screen - blank the card
            self.Blank_Card(w.sID)
            duration = 1
            if Configed_Bool("General", "fastPlay") is True:
                duration = 0.5
            animSmallCard = Animation(
                x=self.smallCardPos[cPlayer - 1][w.sID][0],
                y=self.smallCardPos[cPlayer - 1][w.sID][1],
                d=duration,
                t="in_out_quad",
            )
            if int(w.sID) == int(lastScatter):
                animSmallCard.bind(on_complete=nextTurn)
            animSmallCard.start(
                self.ids["p" + str(cPlayer) + "c" + str(w.sID) + "Image"]
            )

        def no_newplayer(a, w):
            Logger.info("no_newplayer fired")
            self.Move_All_Home(False)
            if (
                    self.hand[cPlayer]["cpu"] is False
                    and self.gameState["controlPlayer"] is not None
                    and self.gameState["chicago"] < 0
            ):
                self.Display_Chicago_Buttons()

        def _popToTop(dCard):
            Widget_ToTop(layout, dCard)
            Widget_ToTop(layout, self.ids["p" + str(cPlayer) + "nameLabel"])

        # #Create anim for current players cards downwards and off screen
        dCard = None
        for index, scatterID in enumerate(self.hand[cPlayer]["posindex"]):
            card = self.ids["card" + str(scatterID)]
            card.sID = scatterID
            y = 0 - self.ids["card0"].size[1] * 2
            if faceUp[0] is not None and scatterID == faceUp[0]:
                dStackPos = len(self.hand[cPlayer]["showDownDiscards"]) - 1
                animDiscard = Animation(
                    x=self.discardCardPos[cPlayer - 1][dStackPos][0],
                    y=self.discardCardPos[cPlayer - 1][dStackPos][1],
                    t="in_out_quad",
                )
                # small dis card :)
                dCard = self.ids[
                    "p" + str(cPlayer) + "c" + str(dStackPos) + "DiscardImage"
                ]
                _popToTop(dCard)
                # set the correct card picture and move into view
                dCard.source = self.cardFilePath + "/" + faceUp[1]
                animDiscard.start(dCard)
            if self.hand[cPlayer]["cardid"][scatterID] == "DONE":
                card.pos = int(self.xpos_center), y
                continue
            if self.hand[cPlayer]["cpu"] is True and cPlayer != newPlayer:
                return_smallcards(None, card)
            elif self.hand[cPlayer]["cpu"] is False:
                anim = Animation(x=int(self.xpos_center), y=0, d=0.2)
                if newPlayer != cPlayer:
                    anim = anim + \
                        Animation(x=int(self.xpos_center), y=y, d=0.3)
                    anim.bind(on_complete=return_smallcards)
                elif (
                        index
                        == len(self.hand[cPlayer]["cardid"])
                        - self.hand[cPlayer]["cardid"].count("DONE")
                        - 1
                ):
                    anim.bind(on_complete=no_newplayer)
                anim.start(card)
        # #Ensure dCards are displayed correctly along the z axis
        if Get_Config_Bool(self.setConfig["viewDiscards"]) is True:
            for index in range(0, len(self.hand[cPlayer]["posindex"])):
                _popToTop(
                    self.ids["p" + str(cPlayer) + "c" +
                             str(index) + "DiscardImage"]
                )
        elif dCard is not None:
            _popToTop(dCard)
        # #ensure Next Turn fires if CPU player has just stolen control
        if self.hand[cPlayer]["cpu"] is True and newPlayer == cPlayer:
            Logger.info("calling nextTurn again because CPU took control")
            nextTurn(None, None)
