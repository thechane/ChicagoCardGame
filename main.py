import io
from builtins import int
from os import listdir, remove, environ, rename
from os.path import isfile
import _pickle as cPickle
from traceback import format_exc, print_exc

import kivy
from kivy.uix.settings import SettingsWithTabbedPanel
kivy.require('2.1.0')

from screens.Game_Screen import Game_Screen
from screens.Menu_Screen import Menu_Screen
from screens.Shop_Screen import Shop_Screen
from screens.Game_Over_Screen import Game_Over_Screen

from kivy.app import App
from kivy.logger import Logger, LoggerHistory
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.image import Image as CoreImage
from kivy.utils import platform
from kivy.properties import StringProperty, ObjectProperty

from plyer import email

__version__ = "2.0"
paidApp = True
try:
    if environ['FREE'] == "0":
        paidApp = True
except Exception as e:
    Logger.info('Unable to query ENV var FREE: ' + str(e))

# if platform == 'android':
#     ##Billing
#     from jnius import autoclass
#     import oiabilling
#     ##Advertising
#     PythonActivity = autoclass("org.renpy.android.PythonActivity")
#     AdBuddiz = autoclass("com.purplebrain.adbuddiz.sdk.AdBuddiz")
# elif platform == 'ios' and paidApp is False:
#     from pyobjus import autoclass
#     from pyobjus.dylib_manager import load_framework, INCLUDE,  make_dylib, load_dylib
#     load_framework(INCLUDE.StoreKit)
#     load_framework(INCLUDE.AVFoundation)
#     load_framework(INCLUDE.SystemConfiguration)
#     load_framework("./frameworks/AdSupport.framework")
#     load_framework("./frameworks/AdBuddiz.framework")
#     Ad = autoclass("AdBuddiz")
#     Logger.info("\n\nview class methods:\n" + str(dir(Ad)))
#     Logger.info("\n\nview instance methods:\n" + str(dir(Ad.alloc())))

class CustomLayout(FloatLayout):
    pass

class ChicagoApp(App):
    billing = ObjectProperty(None)
    version = __version__

    def __init__(self, **kwargs):
        Logger.info('ChicagoApp init FIRED')
        super(ChicagoApp, self).__init__(**kwargs)
        ##fix for old file locations
        if platform == 'android':
            if isfile(App.get_running_app().user_data_dir + '/game.dat') is False and isfile('./game.dat') is True:
                rename('./game.dat', App.get_running_app().user_data_dir + '/game.dat')
            if isfile(App.get_running_app().user_data_dir + '/shop.dat') is False and isfile('./shop.dat') is True:
                rename('./shop.dat', App.get_running_app().user_data_dir + '/shop.dat')
        ##Cache all the card images
        for path in ('./images/PNG-cards-1.3', './images/back'):
            for f in listdir(path):
                if isfile(path + '/' + f) and f[-4:] == '.png':
                    data = io.BytesIO(open(path + '/' + f, "rb").read())
                    CoreImage(data, ext="png", filename = path + '/' + f)
        ##and the reset
        for f in ('cardborder.png', 'greenTable.jpg', 'simpleTable.jpg'):
            data = io.BytesIO(open('./images/' + f, "rb").read())
            CoreImage(data, ext=f[-3:], filename='./images/' + f)
        # if platform == "android":
        #     ##set up AdBuddiz
        #     AdBuddiz.setPublisherKey("_ANDROIDADKEY_")
        #     #AdBuddiz.setTestModeActive() # todo - Comment this line before releasing!
        #     AdBuddiz.cacheAds(PythonActivity.mActivity)
        # elif platform == 'ios' and paidApp is False:
        #     #import <AdBuddiz/AdBuddiz.h>
        #     Ad.setPublisherKey_("_IOSADDKEY_")
        #     Ad.cacheAds()
        #     Ad.setTestModeActive()
        #     pass

    def build(self):
        Logger.info('build FIRED')
        ##Build the shop screen and set up billing
        # if platform == 'android':
        #     global billing
        #     self.billing = billing = oiabilling.Billing(["net.roadtrip2001.kivychicago.noads",
        #                                                  "net.roadtrip2001.kivychicago.sweden_flaggedcards",
        #                                                  "net.roadtrip2001.kivychicago.usa_flaggedcards",
        #                                                  "net.roadtrip2001.kivychicago.uk_flaggedcards"],
        #                                                 'net.roadtrip2001.kivychicago.Config')
        #     #self.billing.setConsumable("fr.alborini.openiab4kivy.gas")
        #     ##Add all the screens
        #     if (self.billing.consumed.has_key("net.roadtrip2001.kivychicago.noads") and
        #         self.billing.consumed["net.roadtrip2001.kivychicago.noads"]):
        #         self.noAds = True
        #     else:
        #         self.noAds = False
        # elif platform == "ios" and paidApp is True:
        #     self.noAds = True   # THIS WILL CHANGE
        # else:
        self.noAds = True
        sm = ScreenManager()
        sm.add_widget(Menu_Screen(name='menuScreen'))
        sm.add_widget(Shop_Screen(name='shopScreen'))
        sm.add_widget(Game_Over_Screen(name='gameOverScreen'))
        self.settings_cls = SettingsWithTabbedPanel
        self.use_kivy_settings = False
        ##shop data section
        sm.shopCard = None
        shopData = None
        if platform == 'android':
            if isfile(App.get_running_app().user_data_dir + '/shop.dat') is True:
                Logger.info('Reading in in shop.dat')
                try:
                    f = open(App.get_running_app().user_data_dir + '/shop.dat')
                    shopData = cPickle.load(f)
                    f.close()
                except Exception as e:
                    Logger.info('SHOPDATA LOAD FILE ERROR (file will be removed): ' + str(e))
                    remove(App.get_running_app().user_data_dir + '/shop.dat')
            if shopData is not None:
                for skuSwitchID in shopData:
                    if 'flaggedcards' in skuSwitchID and shopData[skuSwitchID] is True:
                        flagname = skuSwitchID.split('.')[-1]
                        flagname = flagname.split('_')[0]
                        sm.shopCard = flagname
                        break

        return sm

    def on_start(self):
        Logger.info('on_start FIRED')
        #self.show_ads()
        pass

    # def show_ads(self, *args):
    #     if self.noAds is False:
    #         if platform == "android":
    #             AdBuddiz.showAd(PythonActivity.mActivity)
    #         elif platform == "ios":
    #             Ad.showAd()
    #         else:
    #             pass
#                 popup = Popup(title='Advertise',
#                               content=Label(text='Here'),
#                               size_hint=(0.5,0.5))
#                 popup.open()

    ##Pause mode - http://kivy.org/docs/api-kivy.app.html#pause-mode
    def on_pause(self):
        # Here you can save data if needed
        return True

    def on_resume(self):
        # Here you can check if any data needs replacing (usually nothing)
        pass

    def New_Game(self,gameData):
        Logger.info('New_Game FIRED')

        config = ChicagoApp.get_running_app().config
        pCount = int( config.getdefault("Varients", "playerCount", "2") ) + 1
        pInfo = {}
        for index in range(1,pCount):
            #pInfo[index] = {'name': 'Player' + str(index), 'cpu': False}
            pInfo[index] = {'name': config.getdefault("Players", "PlayerCount" + str(index), "Player" + str(index)),
                            'cpu': config.getdefault("Players", "p" + str(index) + "CPU", False)
                            }
        gs = Game_Screen(
                name = 'gameScreen',
                playerCount = pCount,
                handCount = 5,
                players = pInfo,
                chicagoTwo = config.getdefault("Varients", "chicagoTwo", True),
                rounds = int( config.getdefault("Varients", "roundCount", "2") ),
                pokerRoundScoring = config.getdefault("Varients", "pokerRoundScoring", False),
                pokerAfterShowdownScoring = config.getdefault("Varients", "pokerAfterShowdownScoring", True),
                cardExchangePointsLimit = config.getdefault("Varients", "cardExchangePointsLimit", "46"),
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
                gameData = gameData
            )
        if self.root.has_screen('gameScreen'):
            self.root.remove_widget(self.root.get_screen('gameScreen'))
        self.root.add_widget(gs)
        Logger.info('screens = ' + str(self.root.screen_names))
        self.root.transition = FadeTransition()
        self.root.current = 'gameScreen'
        #self.sm.switch_to(s, transition = WipeTransition())

    def on_config_change(self, config, section, key, value):
        Logger.info('on_config_change FIRED')
        #print config, section, key, value

    def build_config(self, config):
        Logger.info('build_config FIRED')
#         config.add_section("General")
#         config.add_section("Varients")
#         config.add_section("Players")
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
    #todo - take out plyer for production?? Don't forget to remove from .spec files also
    try:
        ChicagoApp().run()
    except:
        print_exc()
#         if platform == 'android':
#             his = ''
#             for line in LoggerHistory.history:
#                 his = his + str(line) + "\n"
#             his = his + "\n\n\n" + str(format_exc()) + "\n\n----------------------------\n"
#             f = open(App.get_running_app().user_data_dir + '/game.dat', 'r')
#             his = his + str(f.read()) + "\n-----------------------\n"
#             f.close()
#             email.send(recipient = 'chicago@roadtrip2001.net',
#                        subject = 'DEBUG:CHICAGO:CRASH',
#                        text = his,
#                        create_chooser = False)
