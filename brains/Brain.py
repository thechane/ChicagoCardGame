import collections
from copy import copy
from random import randint

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.logger import Logger  # , LoggerHistory

from brains.Common import Widget_ToTop, Configed_Bool


class Brain(object):
    def __init__(self, **kwargs):
        self.cardCount = kwargs.get("cardCount", 5)
        # suit, value
        try:
            self.winner = kwargs.get("winner")
        except:
            pass
        self.suitWatch = (None, None)
        self.playerCantPlaySuit = (
            [],
            [],
            [],
            [],  # ['hearts','hearts','spades'], ['diamonds']
        )

    def Strip_Player(self, name):
        newName = name[0:11]
        newName = newName.rstrip()
        return newName.replace(" ", "_")

    def ID_Card(self, cardID):
        # Logger.info('IDing card ' + str(cardID))
        tmp = cardID.split(".")
        tmp = tmp[0].split("_of_")
        return (int(tmp[0]), tmp[1])

    def ID_Hand(self, handStrings):
        splitHand = {"diamonds": [], "hearts": [], "spades": [], "clubs": []}
        LineUp = []
        # Suit Value order spades, hearts, diamonds, clubs
        highCard = (0, 0)
        for cardname in handStrings:
            cardID = self.ID_Card(cardname)
            suitVal = 0
            if cardID[1] == "diamonds":
                suitVal = 2
                splitHand["diamonds"].append(cardID[0])
            elif cardID[1] == "hearts":
                suitVal = 3
                splitHand["hearts"].append(cardID[0])
            elif cardID[1] == "spades":
                suitVal = 4
                splitHand["spades"].append(cardID[0])
            elif cardID[1] == "clubs":
                suitVal = 1
                splitHand["clubs"].append(cardID[0])
            LineUp.append(cardID[0])
            if cardID[0] > highCard[0]:
                highCard = (cardID[0], suitVal)
        LineUp = sorted(LineUp)
        # ? of a kind
        # DEBUGGING:  [(4, 3), (12, 1)]
        # ['4_of_spades.png', '12_of_hearts.png', '4_of_diamonds.png', '13_of_diamonds.png', '4_of_clubs.png']
        ofakind = collections.Counter(LineUp)
        self.ofAKindResult = ofakind.most_common(2)
        try:
            # tuple, ('value of most duplicated card', integer amount)
            Logger.info("DEBUGGING: " + str(self.ofAKindResult))
        except IndexError:
            # No pairs, 3 or 4 of a kinds
            pass
        # Straight? Flush
        isStraight = False
        if list(range(LineUp[0], LineUp[0] + self.cardCount)) == LineUp:
            isStraight = True

        isFlush = False
        for suit in splitHand:
            if len(splitHand[suit]) == self.cardCount:
                isFlush = True
                break
        if isFlush is True and isStraight is True:
            if LineUp[-1] == 14:
                return ("ROYAL_FLUSH", 9000 + highCard[0], highCard, splitHand)
            else:
                return ("STRAIGHT_FLUSH", 8000 + highCard[0], highCard, splitHand)
        if self.ofAKindResult[0][1] == 4:
            return ("4_OF_A_KIND", 7000 + self.ofAKindResult[0][0], highCard, splitHand)
        elif self.ofAKindResult[0][1] == 3 and self.ofAKindResult[1][1] == 2:
            return ("FULL_HOUSE", 6000 + self.ofAKindResult[0][0], highCard, splitHand)
        elif isFlush is True:
            return ("FLUSH", 5000 + highCard[0], highCard, splitHand)
        elif isStraight is True:
            return ("STRAIGHT", 4000 + highCard[0], highCard, splitHand)
        elif self.ofAKindResult[0][1] == 3:
            return ("3_OF_A_KIND", 3000 + self.ofAKindResult[0][0], highCard, splitHand)
        elif self.ofAKindResult[0][1] == 2 and self.ofAKindResult[1][1] == 2:
            higherPair = self.ofAKindResult[0][0]
            if self.ofAKindResult[1][0] > higherPair:
                higherPair = self.ofAKindResult[1][0]
            return ("2_PAIR", 2000 + higherPair, highCard, splitHand)
        elif self.ofAKindResult[0][1] == 2:
            return (
                "PAIR",
                1000 + self.ofAKindResult[0][0],
                highCard,
                splitHand,
            )  # 1000 + value of high card + card value of pair,value of suit
        else:
            return ("HIGH_CARD", highCard[0], highCard, splitHand)

    def Set_canDiscard(self, hand, cardExchangePointsLimit):
        for pNum in hand:
            if int(hand[pNum]["score"]) >= int(cardExchangePointsLimit):
                hand[pNum]["canDiscard"] = False
            else:
                hand[pNum]["canDiscard"] = True

    def Score_Hand(self, hand, straightFlushValue, fourKindToZero, stats):
        for playerNum in hand:
            # create tmp that removes DONE cards and readds those discarded during showdown
            tmp = [value for value in hand[playerNum]
                   ["cardid"] if value != "DONE"]
            tmp.extend(hand[playerNum]["showDownDiscards"])
            results = self.ID_Hand(tmp)
            hand[playerNum]["hand"] = results[0]
            hand[playerNum]["handScore"] = (
                results[1], results[2][0], results[2][1])
        # calculate the scores storing the top marks in bestScore
        bestScore = (0, 0, 0)
        for playerNum in hand:
            # Logger.info('Player ' + str(playerNum) + ' hand : ' + str(hand[playerNum]))
            if (
                    hand[playerNum]["handScore"][0] > bestScore[0]
                    or (
                    hand[playerNum]["handScore"][0] == bestScore[0]
                    and hand[playerNum]["handScore"][1] > bestScore[1]
                    )
                    or (
                    hand[playerNum]["handScore"][0] == bestScore[0]
                    and hand[playerNum]["handScore"][1] == bestScore[1]
                    and hand[playerNum]["handScore"][2] > bestScore[2]
                    )
            ):
                self.winner = playerNum
                bestScore = hand[playerNum]["handScore"]

        def ScoreIt(h):
            # Add to the winning players score
            s = 0
            if h == "PAIR":
                s = 1
            elif h == "2_PAIR":
                s = 2
            elif h == "3_OF_A_KIND":
                s = 3
            elif h == "STRAIGHT":
                s = 4
            elif h == "FLUSH":
                s = 5
            elif h == "FULL_HOUSE":
                s = 6
            elif h == "4_OF_A_KIND":
                s = 7
                if fourKindToZero is True:
                    for playerNum in hand:
                        if playerNum != self.winner:
                            hand[playerNum]["score"] = 0
            elif h == "STRAIGHT_FLUSH":
                s = int(straightFlushValue)
            elif h == "ROYAL_FLUSH":
                s = 52
            return s

        # Update points and stats
        points = ScoreIt(hand[self.winner]["hand"])
        hand[self.winner]["score"] += points
        winningHand = hand[self.winner]["hand"]
        stats["player"][self.winner]["pokerWins"] = +1

        # Craft fun text message and return it
        if winningHand == "HIGH_CARD" and bestScore[1] > 10 and bestScore[0] < 1000:
            if bestScore[1] == 14:
                winningHand = "Ace_High"
            elif bestScore[1] == 13:
                winningHand = "King_High"
            elif bestScore[1] == 12:
                winningHand = "Queen_High"
            elif bestScore[1] == 11:
                winningHand = "Jack_High"
        elif winningHand is "HIGH_CARD" and bestScore[0] < 1000:
            winningHand = str(bestScore[1]) + "_High"
        else:
            winningHand = str(winningHand)
        if points > stats["player"][self.winner]["highestPokerHand"]:
            stats["player"][self.winner]["highestPokerHand"] = points
            stats["player"][self.winner]["highestPokerHandText"] = winningHand
        return (
            self.Strip_Player(hand[self.winner]["name"]) +
            " wins_with " + winningHand
        )

    # return True if we should try to play Poker, or False if we want to prepare for Showdown
    def Poker_Change(self, hand, roundNo, roundTotal):
        Logger.info("Poker_Change FIRED")
        handID = self.ID_Hand(hand)
        if roundTotal > 2 and roundNo == 1:
            return (True, handID)
        elif roundNo == roundTotal:
            return (False, handID)
        if roundNo == roundTotal - 1 and handID[1] < 3000:
            return (False, handID)
        else:
            return (True, handID)

    def Poker_Discards(self, hand, posindex, handID):
        Logger.info("Poker_Discards FIRED")
        discards = []
        if handID[1] > 4000:  # Straight or better
            return []  # Do nothing
        elif handID[1] > 2000:  # 3 of a kind and 2 pair
            for scatterID in posindex:
                cardID = self.ID_Card(hand[scatterID])
                if (
                        (
                            handID[1] < 3000
                            and (  # two pair
                                self.ofAKindResult[0][0] == cardID[0]
                                or self.ofAKindResult[1][0] == cardID[0]
                            )
                        )
                        # 3 of a kind
                        or (self.ofAKindResult[0][0] == cardID[0])
                        or cardID[0] > 12  # king or higher
                ):
                    continue
                discards.append(scatterID)
        elif handID[1] > 1000:  # 1 pair, separated out for adding in intelligence later
            for scatterID in posindex:
                cardID = self.ID_Card(hand[scatterID])
                if (self.ofAKindResult[0][0] == cardID[0]) or (cardID[0] > 12):
                    continue
                discards.append(scatterID)
        else:
            for scatterID in posindex:
                cardID = self.ID_Card(hand[scatterID])
                if cardID[0] > 12:
                    continue
                discards.append(scatterID)
        return discards

    def Showdown_Discards(self, hand, posindex):
        Logger.info("Showdown_Discards FIRED")
        discards = []
        for scatterID in posindex:
            cardID = self.ID_Card(hand[scatterID])
            if cardID[0] > 11:
                continue
            discards.append(scatterID)
        return discards

    def Chicago_Question(self, configData, handData, playerNum):
        handID = self.ID_Hand(handData[playerNum]["cardid"])
        Logger.info("Chicago_Question FIRED on handID " + str(handID))
        splitHand = handID[3]
        if configData["pokerAfterShowdownScoring"] is True and handID[1] > 4000:
            # do not call Chicago if we have a good hand and are scoring the poker hand after the showdown (Chicago cancels this scoring)
            return False
        # Now check we have a decent amount of aces
        aceCount = 0
        kingCount = 0
        queenCount = 0
        for suit in splitHand:
            aceCount = aceCount + splitHand[suit].count(14)
            kingCount = kingCount + splitHand[suit].count(13)
            queenCount = queenCount + splitHand[suit].count(12)
        Logger.info("aceCount = " + str(aceCount))
        highestCardValue = handID[2][0]
        for suit in splitHand:
            # Consider have many of the same suit
            Logger.info(
                "... risk = "
                + str(handData[playerNum]["risk"])
                + ", considering the "
                + str(len(splitHand[suit]))
                + " "
                + str(splitHand[suit])
            )
            if (
                    (len(handData) < 4 and len(
                        splitHand[suit]) >= 4 and aceCount >= 2)
                    or (len(handData) == 2 and len(splitHand[suit]) >= 4 and aceCount >= 2)
                    or (len(handData) == 2 and aceCount > 2)
                    or (
                    len(handData) == 2
                    and aceCount == 2
                    and (kingCount > 1 or queenCount > 1)
                    )
            ):
                return True
            if (
                    (len(handData) == 2 and len(
                        splitHand[suit]) >= 3 and aceCount >= 2)
                    or (
                        len(handData) == 4
                        and len(splitHand[suit]) >= 4
                        and max(splitHand[suit]) > 10
                    )
                    or (  # 4 players, 4 or more cards of same suit and one of those cards > 10
                        len(handData) == 4 and len(
                            splitHand[suit]) >= 3 and aceCount >= 2
                    )
                    or (len(handData) < 4 and aceCount > 2)
                    or (
                        len(handData) < 4
                        and aceCount >= 2
                        and (kingCount >= 2 or queenCount >= 2)
                    )
            ) and randint(0, 9) < handData[playerNum][
                "risk"
            ]:  # players have risk factor set between 0 and 9.
                return True
        if highestCardValue < 11:
            return False
        if (handID[1] > 1000 and handID[1] < 3000) and (  # pair or 2 pair
                self.ofAKindResult[0][0] > 11 or self.ofAKindResult[1][0] > 11
        ):
            # If pair is high and we have at least one more highish card
            for cardName in handData[playerNum]["cardid"]:
                cardID = self.ID_Card(cardName)
                if (
                        cardID[0] > 13
                        and cardID[0] != self.ofAKindResult[0][0]
                        and len(handData) < 4
                        and randint(0, 9) < handData[playerNum]["risk"]
                ):
                    return True
        if (
                (handID[1] > 3000 and handID[1] < 4000)
                # 3 of a kind  ##4 of a kind
                or (handID[1] > 7000 and handID[1] < 8000)
        ) and (
                (len(handData) == 2 and self.ofAKindResult[0][0] > 12)
                or (len(handData) == 3 and self.ofAKindResult[0][0] > 13)
                or (self.ofAKindResult[0][0] == 14)
        ):
            # if we have 3 or 4 of a kind with Aces, or >= King with a two player game, or >= Queen with 3 player game
            return True
        # todo, consider finishing on a 2 and deliberate chicago fails when we can't exchange
        return False

    def Showdown_Turn_Self_Chicago(self, hand):
        Logger.info("BRAINS:Showdown_Turn_Self_Chicago fired")
        if len(hand) == 5:
            # if this is the first round of a Chicago call, reset the self.suitWatch
            # suit, value
            self.suitWatch = (None, None)
        # index,value,suit
        highCard = (None, 0, None)
        # index,value
        suitMatch = (None, None)
        for index, cardname in enumerate(hand):
            if cardname == "DONE":
                continue
            cardID = self.ID_Card(cardname)
            if self.suitWatch[0] is not None and cardID[1] == self.suitWatch[0]:
                # if last chicago showdown round was successful we can reuse suit which is proved safe
                # todo, consider if we have a 2 to finish with
                if suitMatch[1] is not None and cardID[0] > suitMatch[1]:
                    suitMatch = (index, cardID[0])
                elif suitMatch[1] is None:
                    suitMatch = (index, cardID[0])
            if cardID[0] > highCard[1]:
                # otherwise we use our highest valued card
                highCard = (index, cardID[0], cardID[1])
        # if we can match the last suit played and we are close in value
        if suitMatch[0] is not None and suitMatch[1] >= int(self.suitWatch[1] * 0.75):
            return suitMatch[0]
        else:
            self.suitWatch = (highCard[2], highCard[1])
            return highCard[0]

    def Return_Lowest_Card_With_Matching_Suit(self, hand, suit):
        Logger.info("BRAINS:Return_Lowest_Card_With_Matching_Suit fired")
        suitMatch = (None, None)  # (index,value)
        for index, cardname in enumerate(hand):
            if cardname != "DONE":
                cardID = self.ID_Card(cardname)  # (value,suit)
                Logger.info("??????>" + str(cardname))
                if (cardID[1] == suit and suitMatch[0] is None) or (
                        cardID[1] == suit and cardID[0] < suitMatch[1]
                ):
                    suitMatch = (index, cardID[0])
                    Logger.info("------>" + str(suitMatch))
        Logger.info("=======>" + str(suitMatch))
        return suitMatch

    def Does_Player_Have_Matching_Suit(self, hand, suit):
        for cardname in hand:
            if cardname == "DONE":
                continue
            cardID = self.ID_Card(cardname)  # (value,suit)
            if cardID[1] == suit:
                return True
        return False

    def Showdown_Turn_Other_Chicago(self, hand, activeCard, pNum):
        Logger.info("BRAINS: fired Showdown_Turn_Other_Chicago " + str(hand))
        # hand is ['cardid'], activecard is scatterID,value,suit
        # first try to take control
        for index, cardname in enumerate(hand):
            if cardname == "DONE":
                continue
            cardID = self.ID_Card(cardname)
            if cardID[1] == activeCard[2] and cardID[0] > activeCard[1]:
                return index
        # if we can't, then discard lowest card of same suit
        lowcard = self.Return_Lowest_Card_With_Matching_Suit(
            hand, activeCard[2])
        if lowcard[0] is not None:
            return lowcard[0]
        # if we still can't, pick the lowest card
        # todo - more intel here - keep one of each suit for example
        Logger.info("player " + str(pNum) +
                    " can not play suit " + activeCard[2])
        self.playerCantPlaySuit[pNum - 1].append(activeCard[2])
        lowcard = (None, 15)
        for index, cardname in enumerate(hand):
            if cardname == "DONE":
                continue
            cardID = self.ID_Card(cardname)
            if cardID[0] < lowcard[1]:
                lowcard = (index, cardID[0])
        return lowcard[0]

    def Showdown_Turn_No_Chicago(self, hand, activeCard, inControl, pNum):
        Logger.info(
            "BRAINS: fired Showdown_Turn_No_Chicago for player "
            + str(pNum)
            + " with hand "
            + str(hand)
        )
        # hand is ['cardid'], activecard is scatterID,value,suit, inControl is True or False
        # index,value,suit
        lowWinningCardMatchingSuit = (None, 15, None)
        highCard = (None, 0, None)
        lowCard = (None, 15, None)
        lowcardSuited = (None, None)
        doneCounter = 0
        for index, cardname in enumerate(hand):
            Logger.info(str(index) + ":" + str(cardname))
            if cardname == "DONE":
                doneCounter = doneCounter + 1
                continue
            cardID = self.ID_Card(cardname)
            if (
                    (activeCard is None or cardID[1] == activeCard[2])
                    and (activeCard is None or cardID[0] > activeCard[1])
                    and cardID[0]
                    < lowWinningCardMatchingSuit[
                        1
                    ]  # we want to use the lowest card to break control
            ):
                lowWinningCardMatchingSuit = (index, cardID[0], cardID[1])
            if cardID[0] > highCard[1]:
                highCard = (index, cardID[0], cardID[1])
            if cardID[0] < lowCard[1]:
                lowCard = (index, cardID[0], cardID[1])
        if inControl is True or activeCard is None:
            Logger.info("player is in control")
            if (doneCounter == 0 and lowCard[0] < 7) or (
                    doneCounter == 1 and lowCard[0] < 5
            ):
                # ditching low card at early stages of showdown probably best
                return lowCard[0]
            else:
                return highCard[0]
        else:
            Logger.info("player is NOT in control")
            # (index,value)
            lowcardSuited = self.Return_Lowest_Card_With_Matching_Suit(
                hand, activeCard[2]
            )
            if (
                    doneCounter == 0
                    and lowcardSuited[0] is not None
                    and lowcardSuited[1] < 5
            ):
                Logger.info("loose crappy withOUT taking control")
                # we could take control but do not as showdown has just begun and we have crappy card to loose
                return lowcardSuited[0]
            elif lowWinningCardMatchingSuit[0] is not None:
                Logger.info("loose crappy and take control")
                # take control with crappiest card possible if we can
                return lowWinningCardMatchingSuit[0]
        # At this point we know that we can not take control, drop crappiest card of same suit
        if lowcardSuited[0] is not None:
            Logger.info("can NOT take control, loose crappy matching suit")
            return lowcardSuited[0]
        # If we can't keep suit then find crappiest card and drop
        # todo consider keeping if many of same suit
        Logger.info("can NOT take control, loose crappy NO matching suit")
        self.playerCantPlaySuit[pNum - 1].append(activeCard[2])
        return lowCard[0]

    def Choose_Effect(self, text):
        if "2_PAIR" in text:
            return "niceone"
        elif "3_OF_A_KIND" in text:
            return "niceone"
        elif "STRAIGHT" in text:
            return "niceone"
        elif "FLUSH" in text:
            return "royal"
        elif "FULL_HOUSE" in text:
            return "royal"
        elif "4_OF_A_KIND" in text:
            return "royal"
        elif "STRAIGHT_FLUSH" in text:
            return "royal"
        elif "ROYAL_FLUSH" in text:
            return "royal"
        elif "showdown" in text:
            return "sun"
        # elif 'RANDOM_PICK' in text:
        #    pick = ['twopair', 'threekind', 'straight', 'flush', 'fullhouse', 'royal', 'straightflush']
        #    tmp = random.choice(pick)
        #    print tmp
        #    return tmp
        else:
            return None

    def Human_Next_Turn(self, gsInst):
        Logger.info("Human_Next_Turn fired")
        duration = 1
        if Configed_Bool("General", "fastPlay") is True:
            duration = 0.3
        tmpList = []

        def now_big_card(a, w):
            tmpTuple = tmpList.pop()
            # Logger.info('now_big_card fired')
            # Logger.info('firing now_big_card for -- ' + str(gsInst.xpos_home[tmpTuple[0]]))
            card = gsInst.ids["card" + str(tmpTuple[1])]
            anim = Animation(
                x=gsInst.xpos_home[tmpTuple[0]], y=0, d=duration, t="in_out_quad"
            )
            gsInst.Blank_Card(tmpTuple[1])
            # if nothing in tmpList and therefore last card
            if not tmpList:

                def finshUp(an, wi):
                    # Check if we have entered showdown and need to ask players if they wish to Chicago
                    if (
                            gsInst.gameState["controlPlayer"] is not None
                            and gsInst.gameState["chicago"] < 0
                    ):
                        gsInst.Display_Chicago_Buttons()
                    elif (
                            gsInst.gameState["chicago"] != -2
                            and gsInst.gameState["controlPlayer"] is None
                    ):
                        gsInst.ids["endTurnButton"].disabled = False
                        gsInst.ids["yesChicagoButton"].disabled = False
                        gsInst.ids["noChicagoButton"].disabled = False
                    # This ensures if we are in the middle of discarding in a poker round we'll show non discards as face up
                    # which allows the player to continue discarding before a double tap confirm
                    if gsInst.gameState["discardFlag"] is True:
                        for sID in gsInst.hand[gsInst.currentPlayer]["posindex"]:
                            if sID not in gsInst.discardNumber[gsInst.currentPlayer]:
                                gsInst.ids["card" + str(sID) + "Image"].source = (
                                    gsInst.cardFilePath
                                    + "/"
                                    + gsInst.hand[gsInst.currentPlayer]["cardid"][sID]
                                )
                    # if the gameScreen is not current (menu button pushed) force on_leave to fire again so cards
                    # are animated off screen. Prevent cards disappears and then reappearing when gameScreen is made current again.
                    if gsInst.manager.current != "gameScreen":
                        gsInst.on_leave()

                anim.bind(on_complete=finshUp)
            anim.start(card)

        # Move small cards off screen
        def moveSmallCardsOffScreen(dt):
            # Logger.info('moveSmallCardsOffScreen Fired')
            Clock.unschedule(moveSmallCardsOffScreen, all=True)
            if gsInst.manager is None:
                # Game has ended, do nothing
                return True
            elif (
                    gsInst.holdIt is False
                    and gsInst.dealingCards is False
                    and gsInst.init is False
            ):
                Logger.info("holdIt has been released, proceeding")
                # if all cards are done and there is an active card, we can enable the end turn button
                if all(
                        item == "DONE"
                        for item in gsInst.hand[gsInst.currentPlayer]["cardid"]
                ):
                    gsInst.ids["endTurnButton"].disabled = False
                else:
                    for toXhomeIndex, scatterID in enumerate(
                            gsInst.hand[gsInst.currentPlayer]["posindex"]
                    ):
                        if (
                                gsInst.hand[gsInst.currentPlayer]["cardid"][scatterID]
                                == "DONE"
                        ):
                            continue
                        tmpList.append((toXhomeIndex, scatterID))
                        smallCard = gsInst.ids[
                            "p"
                            + str(gsInst.currentPlayer)
                            + "c"
                            + str(scatterID)
                            + "Image"
                        ]
                        anim = Animation(
                            x=gsInst.xpos_center,
                            y=0 - smallCard.height * 10,
                            d=duration,
                            t="in_out_quart",
                        )
                        anim.bind(on_complete=now_big_card)
                        anim.start(smallCard)
            else:
                Logger.info(
                    "waiting on self holdit, init and dealingSmallCards to release"
                )
                Clock.schedule_once(moveSmallCardsOffScreen, 0.5)

        moveSmallCardsOffScreen(None)
        gsInst.Refocus_Cards()
        return True

    def Next_Play(self, gsInst):
        # todo - readd save game below
        cPlayer = copy(gsInst.currentPlayer)
        gsInst.Save_Game()

        def _Next_Play():
            Logger.info(
                "---------- _Next_Play fired for player "
                + str(cPlayer)
                + " ---------------, chicago gameState = "
                + str(gsInst.gameState["chicago"])
            )
            Logger.info("controlPlayer = " +
                        str(gsInst.gameState["controlPlayer"]))
            if gsInst.hand[cPlayer]["cpu"] is False:
                return self.Human_Next_Turn(gsInst)

            # Showdown CPU Play
            def Play_Card(scatterID):
                Logger.info("Play_Card fired with : " + str(scatterID))
                duration = 1.2
                if Configed_Bool("General", "fastPlay") is True:
                    duration = 0.5

                def smallcardGone(a, w):
                    def setTmpActiveCard(a, w):
                        cID = self.ID_Card(
                            gsInst.hand[cPlayer]["cardid"][scatterID])
                        gsInst.gameState["tmpActiveCard"] = (
                            scatterID, cID[0], cID[1])
                        Logger.info("ending from setTmpActiveCard")
                        gsInst.End_Turn()

                    # turn card face up
                    card = gsInst.ids["card" + str(scatterID)]
                    cImage = gsInst.ids["card" + str(scatterID) + "Image"]
                    cImage.source = (
                        gsInst.cardFilePath
                        + "/"
                        + gsInst.hand[cPlayer]["cardid"][scatterID]
                    )
                    box = gsInst.ids["showDownLabel"]
                    anim = Animation(
                        x=box.pos[0]
                        + (box.width / 2)
                        - (gsInst.ids["card0"].width / 2),
                        y=box.pos[1]
                        + (box.height / 2)
                        - (gsInst.ids["card0"].height / 2),
                        d=duration,
                        t="out_quint",
                    )
                    anim.bind(on_complete=setTmpActiveCard)
                    anim.start(card)

                anim = Animation(
                    x=int(gsInst.xpos_center),
                    y=0 - gsInst.ids["card0"].size[1] * 2,
                    d=duration,
                    t="in_out_quad",
                )
                anim.bind(on_complete=smallcardGone)
                sc = gsInst.ids["p" + str(cPlayer) +
                                "c" + str(scatterID) + "Image"]
                Widget_ToTop(gsInst.ids["infoFloat"], sc)
                anim.start(sc)
                return True

            if gsInst.gameState["controlPlayer"] is None:
                Logger.info("Poker CPU play fired")
                # POKER PLAY
                handID = []

                def Poker_Change_With_handID():
                    hID = self.Poker_Change(
                        gsInst.hand[cPlayer]["cardid"],
                        gsInst.gameState["roundNumber"],
                        gsInst.setConfig["pokerRoundCount"],
                    )
                    # http://stackoverflow.com/questions/8447947/is-it-possible-to-modify-variable-in-python-that-is-in-outer-but-not-global-sc
                    handID.append(hID[1])
                    return hID[0]

                # get dicarded cards
                discardList = None
                if gsInst.hand[cPlayer]["canDiscard"] is False:
                    # Powerless - end turn
                    discardList = []
                elif Poker_Change_With_handID() is True:
                    Logger.info("handID = " + str(handID))
                    # Let's try to get a good poker hand
                    discardList = self.Poker_Discards(
                        gsInst.hand[cPlayer]["cardid"],
                        gsInst.hand[cPlayer]["posindex"],
                        handID[0],
                    )
                else:
                    # Let's try to position ourselves for the showdown / posible chicago call
                    discardList = self.Showdown_Discards(
                        gsInst.hand[cPlayer]["cardid"], gsInst.hand[cPlayer]["posindex"]
                    )
                Logger.info("CPU discarding" + str(discardList))
                if not discardList:  # If no discards
                    Logger.info("ending from not discardList")
                    gsInst.End_Turn()
                    return False
                # deal in new cards
                Pos = gsInst.Position_Small_Card_Offscreen(
                    gsInst.ids["p1c1Image"]
                )  # offscreen position same for all (dealer dependant)

                def anim_callback(a, w):
                    gsInst.gameState["discardFlag"] = True
                    Logger.info("ending from not anim_callback")
                    gsInst.End_Turn()

                for counter, scatterID in enumerate(discardList):
                    gsInst.discardNumber[cPlayer].append(scatterID)
                    gsInst.Deal_Cards(
                        cPlayer, gsInst.hand[cPlayer]["cardid"][scatterID]
                    )
                    scW = gsInst.ids[
                        "p" + str(cPlayer) + "c" + str(scatterID) + "Image"
                    ]
                    duration = 1
                    if Configed_Bool("General", "fastPlay") is True:
                        duration = 0.5
                    anim = Animation(x=Pos[0], y=Pos[1],
                                     d=duration, t="in_out_quad")
                    anim = anim + Animation(
                        x=gsInst.smallCardPos[cPlayer - 1][scatterID][0],
                        y=gsInst.smallCardPos[cPlayer - 1][scatterID][1],
                        d=0.5,
                        t="in_out_quad",
                    )
                    # print str(counter) + ' ' + str(len(discardList))
                    if counter == len(discardList) - 1:
                        if (
                                Configed_Bool("General", "sound") is True
                                and gsInst.init is False
                        ):
                            def dealSound(dt):
                                gsInst.drop_sound.play()

                            Clock.schedule_once(dealSound, duration)
                        anim.bind(on_complete=anim_callback)
                    anim.start(scW)
                return True
            elif (
                    gsInst.gameState["controlPlayer"] is not None
                    and gsInst.gameState["activeCard"] is not None
                    and all(item == "DONE" for item in gsInst.hand[cPlayer]["cardid"])
            ):
                Logger.critical(
                    "Player num = "
                    + str(cPlayer)
                    + ". This should never happen, we are continuing a game where the CPU has played but not completed end_turn yet."
                )
                return None
            elif (
                    gsInst.gameState["controlPlayer"] is not None
                    and gsInst.gameState["chicago"] < 0
            ):
                Logger.info("CPU Chicago Q fired")
                # shall we call Chicago?
                if (
                        self.Chicago_Question(
                            gsInst.setConfig, gsInst.hand, cPlayer)
                        is True
                ):
                    Logger.info("CPU will play Chicago")
                    gsInst.Call_Chicago()
                    gsInst.Fun_Text(
                        self.Strip_Player(gsInst.hand[cPlayer]["name"])
                        + " calls Chicago",
                        None,
                        "yellow",
                        1.5,
                    )
                    Logger.info(
                        "CPU_Play requested from CPU_Play itself (CPU Chicago Q fired)"
                    )
                    self.Next_Play(gsInst)
                else:
                    Logger.info("CPU will NOT play Chicago")
                    gsInst.Skip_Chicago()
                    return True
            elif gsInst.gameState["chicago"] == cPlayer:
                Logger.info("CPU Chicago CPU play fired")
                # Showdown and we have called Chicago
                Play_Card(
                    self.Showdown_Turn_Self_Chicago(
                        gsInst.hand[cPlayer]["cardid"])
                )
            elif gsInst.gameState["chicago"] > 0:
                Logger.info("OTHER Chicago CPU play fired")
                # Showdown and player gsInst.gameState['chicago'] has called Chicago
                scatterID = self.Showdown_Turn_Other_Chicago(
                    gsInst.hand[cPlayer]["cardid"],
                    gsInst.gameState["activeCard"],
                    cPlayer,
                )
                return Play_Card(scatterID)
            elif gsInst.gameState["chicago"] == 0:
                Logger.info("Showdown without Chicago CPU play fired")
                # Showdown with no Chicago
                inControl = False
                if cPlayer == gsInst.gameState["controlPlayer"]:
                    inControl = True
                scatterID = self.Showdown_Turn_No_Chicago(
                    gsInst.hand[cPlayer]["cardid"],
                    gsInst.gameState["activeCard"],
                    inControl,
                    cPlayer,
                )
                return Play_Card(scatterID)

        ###################################################################################################################
        def CPUwait(dt):
            Clock.unschedule(CPUwait, all=True)
            returnValue = None
            if (
                    gsInst.holdIt is False
                    and gsInst.init is False
                    and gsInst.dealingCards is False
            ):
                returnValue = _Next_Play()
            else:
                Logger.info("... CPU pause for player " + str(cPlayer))
                Clock.schedule_once(CPUwait, 1)
            if returnValue is not None:
                return returnValue

        gsInst.ids["endTurnButton"].disabled = True
        gsInst.ids["yesChicagoButton"].disabled = True
        gsInst.ids["noChicagoButton"].disabled = True
        CPUwait(None)
