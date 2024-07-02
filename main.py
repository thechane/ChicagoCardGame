import io
import kivy
from builtins import int
from os import listdir
from os.path import isfile
from kivy.uix.settings import SettingsWithTabbedPanel
from screens.Game_Screen import Game_Screen
from screens.Menu_Screen import Menu_Screen
from screens.Game_Over_Screen import Game_Over_Screen
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.core.image import Image as CoreImage
from kivy.properties import ObjectProperty

kivy.require('2.3.0')
__version__ = "2.0"


class CustomLayout(FloatLayout):
    pass


class ChicagoApp(App):
    billing = ObjectProperty(None)
    version = __version__

    def __init__(self, **kwargs):
        self.noAds = True
        Logger.info('ChicagoApp init FIRED')
        super(ChicagoApp, self).__init__(**kwargs)
        # Cache all the card images
        for path in ('./images/PNG-cards-1.3', './images/back'):
            for f in listdir(path):
                if isfile(path + '/' + f) and f.endswith('.png'):
                    data = io.BytesIO(open(path + '/' + f, "rb").read())
                    CoreImage(data, ext="png", filename = path + '/' + f)
        # and the reset
        for f in ('cardborder.png', 'greenTable.jpg', 'simpleTable.jpg'):
            data = io.BytesIO(open('./images/' + f, "rb").read())
            CoreImage(data, ext=f[-3:], filename='./images/' + f)

    def build(self):
        Logger.info('build FIRED')
        sm = ScreenManager()
        sm.add_widget(Menu_Screen(name='menuScreen'))
        sm.add_widget(Game_Over_Screen(name='gameOverScreen'))
        self.settings_cls = SettingsWithTabbedPanel
        self.use_kivy_settings = False
        return sm

    def on_start(self):
        Logger.info('on_start FIRED')

    # Pause mode - http://kivy.org/docs/api-kivy.app.html#pause-mode
    def on_pause(self):
        # Here you can save data if needed
        return True

    def on_resume(self):
        # Here you can check if any data needs replacing (usually nothing)
        pass

    def new_game(self, gamedata):
        Logger.info('new_game FIRED')

        config = ChicagoApp.get_running_app().config
        pcount = int( config.getdefault("Varients", "playerCount", "2")) + 1
        pinfo = {}
        for index in range(1, pcount):
            pinfo[index] = {
                'name': config.getdefault("Players", "PlayerCount" + str(index),
                                          'Player' + str(index)),
                'cpu': config.getdefault("Players", "p" + str(index) + "CPU", False)
            }
        gs = Game_Screen(
                name = 'gameScreen',
                playerCount = pcount,
                handCount = 5,
                players = pinfo,
                chicagoTwo = config.getdefault("Varients", "chicagoTwo", True),
                rounds = int( config.getdefault("Varients", "roundCount", "2") ),
                pokerRoundScoring = config.getdefault("Varients", "pokerRoundScoring", False),
                pokerAfterShowdownScoring = config.getdefault("Varients",
                                                              "pokerAfterShowdownScoring",
                                                              True),
                cardExchangePointsLimit = config.getdefault("Varients",
                                                            "cardExchangePointsLimit",
                                                            "46"),
                negativeScoring = config.getdefault("Varients", "negativeScoring", True),
                fourOfaKindReset = config.getdefault("Varients", "fourOfaKindReset", False),
                viewDiscards = config.getdefault("Varients", "viewDiscards", True),
                chicagoDestroy = config.getdefault("Varients", "chicagoDestroy", False),
                Player1 = "{:<6}".format(config.getdefault("Players", "Player1", False)),
                Player2 = "{:<6}".format(config.getdefault("Players", "Player2", False)),
                Player3 = "{:<6}".format(config.getdefault("Players", "Player3", False)),
                Player4 = "{:<6}".format(config.getdefault("Players", "Player4", False)),
                p1CPU = config.getdefault("Players", "p1CPU", False),
                p2CPU = config.getdefault("Players", "p2CPU", False),
                p3CPU = config.getdefault("Players", "p3CPU", False),
                p4CPU = config.getdefault("Players", "p4CPU", False),
                gameData = gamedata
            )
        if self.root.has_screen('gameScreen'):
            self.root.remove_widget(self.root.get_screen('gameScreen'))
        self.root.add_widget(gs)
        Logger.info('screens = ' + str(self.root.screen_names))
        self.root.transition = FadeTransition()
        self.root.current = 'gameScreen'

    def on_config_change(self, config, section, key, value):
        Logger.info('on_config_change FIRED')

    def build_config(self, config):
        Logger.info('build_config FIRED')
        config.setdefaults('General', {
            'sound': 1,
            'fastPlay': 1,
            'effects': 1,
            'simplefuntext': 0,
            'simplecardback': 0,
            'simplebackground': 0,
            'table': 1,
            'tutorial': 1
        })
        config.setdefaults('Varients', {
            'playerCount': 2,
            'roundCount': 3,
            'straightFlushValue': 10,
            'cardExchangePointsLimit': 46,
            'chicagoTwo': 1,
            'chicagoDestroy': 0,
            'pokerAfterShowdownScoring': 1,
            'negativeScoring': 1,
            'fourOfaKindReset': 0,
            'viewDiscards': 1
        })
        config.setdefaults('Players', {
            'Player1': "Julia",
            'p1CPU': 0,
            'Player2': "Marie",
            'p2CPU': 1,
            'Player3': "Bhav",
            'p3CPU': 1,
            'Player4': "Stu",
            'p4CPU': 1
        })

    def build_settings(self, settings):
        Logger.info('build_settings FIRED')
        with open("settings.json", "r") as settings_json:
            settings.add_json_panel('Settings', self.config, data=settings_json.read())


if __name__ == '__main__':
    ChicagoApp().run()
