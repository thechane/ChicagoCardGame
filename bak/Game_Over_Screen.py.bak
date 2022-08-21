from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from kivy.core.audio import SoundLoader
from kivy.app import App
from kivy.clock import Clock
from brains.Particle import Particle
from os import remove
from os.path import isfile
import _pickle as cPickle

class Game_Over_Screen(Screen):

    def __init__(self, **kwargs):                               ##Override Screen's constructor
        Logger.info('Game_Over_Screen init Fired')
        super(Game_Over_Screen, self).__init__(**kwargs)        ##but also run parent class constructor (__init__)
        self.win_sound = SoundLoader.load('./sounds/applause.wav')

    def Configed_Bool(self,section,key):
        #config = ConfigParser()
        #config.read('./chicago.ini')
        try:
            if int(App.get_running_app().config.getdefault(section,key,True)) == 1:
                return True
            #if int(config.get(section,key)) == 1:
            #    return True
        except:
            pass
        return False

    def Game_OverScreen_Load(self):
        gameData = None
        if isfile(App.get_running_app().user_data_dir + '/game.dat') is True:
            Logger.info('Loading in game.dat')
            try:
                f = open(App.get_running_app().user_data_dir + '/game.dat')
                gameData = cPickle.load(f)
                f.close()
                self.parent.New_Game(gameData)
            except Exception as e:
                Logger.info('GAMEDATA FILE ERROR: ' + str(e))
        try:
            remove(App.get_running_app().user_data_dir + '/game.dat')
        except:
            Logger.error('Unable to delete game.dat')

        if self.manager.has_screen('gameScreen'):
            self.manager.remove_widget(self.manager.get_screen('gameScreen'))
        fullScreen = self.ids['gameOverFullScreen']

        pb = self.ids['closePrettyButton']
        if self.Configed_Bool("General", "effects") is True:
            with Particle(size_hint_x= fullScreen.width , width = fullScreen.width / 2) as Pa:
                def stopEffect(dt):
                    Pa.unshow(self.ids['gameOverFullScreen'])
                fullScreen.add_widget(Pa)
                Pa.show(id = 'royal',
                        x = pb.pos[0] + pb.width * 0.5,
                        y = pb.pos[1] + pb.height * 0.5,
                        layout = self.ids['gameOverFullScreen'])
                Clock.schedule_once(stopEffect, 4)
        if self.Configed_Bool("General", "sound") is True:
            self.win_sound.play()

        if gameData is None:
            self.ids['prettyHeading'].text = "GAME OVER"
        else:
            gameStats = gameData['stats']
            self.ids['prettyHeading'].text = gameStats['player'][gameStats['winner']]['name'] + " wins"
            def statInfo(pNum):
                s = "[b][color=FF00FF]" + str(gameStats['player'][pNum]['name']) + "[/color][/b]\n"
                s += "Score was " + str(gameStats['player'][pNum]['score']) + "\n"
                s += "Chicagos won     - " + str(gameStats['player'][pNum]['chicagoWins']) + "\n"
                s += "Chicagos lost    - " + str(gameStats['player'][pNum]['chicagoLosses']) + "\n"
                s += "Showdowns won    - " + str(gameStats['player'][pNum]['showdownWins']) + "\n"
                s += "Poker round wins - " + str(gameStats['player'][pNum]['pokerWins']) + "\n"
                try:
                    s += "Best poker hand   - " + str(gameStats['player'][pNum]['highestPokerHandText']) + "\n"
                except:
                    s += "Best poker hand   - no scoring poker hands\n"
                return s
            Logger.info(str(gameStats))
            iString = "[size=20sp][b][color=0000FF] The Winner in " + str(gameStats['plays']) + " rounds[/color][/b]\n\n"
            iString += statInfo(gameStats['winner']) + "\n\n"
            iString += "[size=20sp][b][color=0000FF] The Losers[/color][/b]\n\n"
            for pNum in xrange(1,len(gameStats['player']) + 1):
                if gameStats['player'][pNum]['name'] is not None and pNum != gameStats['winner']:
                    iString += statInfo(pNum) + "\n"
            self.ids['prettyLabel'].text = iString

