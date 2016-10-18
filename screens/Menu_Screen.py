from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from kivy.app import App
from kivy.utils import platform
from kivy.metrics import Metrics
from os import remove
from os.path import isfile
import webbrowser
import cPickle

class Menu_Screen(Screen):

    screen = {
        'orientation':  None,
        'size':         None
    }

    def __init__(self, **kwargs):                       ##Override Screen's constructor
        Logger.info('Menu_Screen init Fired')
        super(Menu_Screen, self).__init__(**kwargs)     ##but also run parent class constructor (__init__)

    def Screen_Size_Calcs(self):
        if (
                (self.width <= self.height + self.width * 0.2) and
                (self.width >= self.height - self.width * 0.2)
            ):
            ##~ square
            Logger.info('Square')
            self.screen['orientation'] = 'square'
            if self.width < 230:
                self.screen['orientation'] = 'small'
            else:
                self.screen['orientation'] = 'large'
        elif self.width > self.height:
            ##Landscape
            ##repos info and showdown drop
            Logger.info('Landscape')
            self.screen['orientation'] = 'landscape'
            if self.width < 165:
                self.screen['orientation'] = 'small'
            else:
                self.screen['orientation'] = 'large'
        elif self.height > self.width:
            ##portrait
            Logger.info('Portrait')
            self.screen['orientation'] = 'portrait'
            if self.width < 165:
                self.screen['orientation'] = 'small'
            else:
                self.screen['orientation'] = 'large'

    def on_size(self,screen,size):
        Logger.info('on_size fired, ' + str(screen) + ',' + str(size) + ',' + str(self.width) + ',' + str(self.height) )
        self.Screen_Size_Calcs()

    def on_enter(self):
        Logger.info('on_load fired, ')
        if platform != 'android':
            try:
                self.ids['menuScroller'].remove_widget(self.ids['shopButton'])
            except:
                pass

    def Goto_Link(self, instance, url):
        webbrowser.open(url)

    def Hide_About(self):
        self.ids['aboutLO'].clear_widgets()
        self.ids['aboutLO2'].clear_widgets()
        self.ids['aboutButton'].disabled = False

    def Show_About(self):
        Logger.info("DPI rounded : " + str(Metrics.dpi_rounded))
        self.ids['aboutButton'].disabled = True
        self.ids['aboutLO'].add_widget(self.ids['aboutLabelPadding'])
        self.ids['aboutLO2'].add_widget(self.ids['closeAboutButtonPadding'])
        self.ids['aboutLO'].add_widget(self.ids['scrollViewID'])
        ##Still not sure how this works without the following line but it does??
        #self.ids['scrollViewID'].add_widget(self.ids['aboutLabel'])
        #self.ids['aboutLO'].add_widget(self.ids['aboutLabel'])
        self.ids['aboutLO2'].add_widget(self.ids['closeAboutButton'])
        self.ids['aboutLO'].add_widget(self.ids['aboutLabelPadding2'])
        self.ids['aboutLO2'].add_widget(self.ids['closeAboutButtonPadding2'])
        with open ("./tutorial/about.markup", "r") as myfile:
            data=myfile.read()
        data = data.replace('TITLESIZE', str("14sp"))
        data = data.replace('NORMALSIZE', str("14sp"))
        data = data.replace('VERSION', str(App.get_running_app().version))
        self.ids['aboutLabel'].text = data
        self.ids['aboutLabel'].bind(on_ref_press=self.Goto_Link)


    def MenuScreen_Checks(self):
        ##Fix for weak reffed widgets`
        self.refs = [
                self.ids['aboutLabelPadding'].__self__,
                self.ids['closeAboutButtonPadding'].__self__,
                self.ids['aboutLabel'].__self__,
                self.ids['closeAboutButton'].__self__,
                self.ids['aboutLabelPadding2'].__self__,
                self.ids['closeAboutButtonPadding2'].__self__,
                self.ids['scrollViewID'].__self__
            ]
        self.Hide_About()
        Logger.info('screens = ' + str(self.manager.screen_names))
        if isfile(App.get_running_app().user_data_dir + '/game.dat') is True or self.manager.has_screen('gameScreen') is True:
            self.ids['returnToGameButton'].disabled = False
        if self.width < self.height:
            self.AYStext = 'Are you sure?\nThis will destroy\nthe current game.'
        else:
            self.AYStext = 'Are you sure?\nThis will destroy the current game.'

    def Return_to_Game(self):
        if self.parent.has_screen('gameScreen') is True:
            self.manager.current = 'gameScreen'
        elif isfile(App.get_running_app().user_data_dir + '/game.dat') is True:
            Logger.info('Loading in game.dat')
            try:
                f = open(App.get_running_app().user_data_dir + '/game.dat')
                gameData = cPickle.load(f)
                f.close()
                App.get_running_app().New_Game(gameData)
            except Exception,e:
                Logger.info('GAMEDATA FILE ERROR: ' + str(e))
                try:
                    remove(App.get_running_app().user_data_dir + '/game.dat')
                    self.ids['t2lab'].text = 'Game Data file was corrupt - deleted'
                except:
                    self.ids['t2lab'].text = 'Unable to continue from previous game - sorry'
        else:
            self.ids['t2lab'].text = 'No Game Running'

    def Are_You_Sure(self):
        ##Create yes know dialog
        Logger.info('Are_You_Sure FIRED')
        menuScroller = self.ids['menuScroller']
        box = BoxLayout(orientation = 'horizontal', size_hint_x = None, size = (menuScroller.width, menuScroller.height))

        def done_aAnim(anim,widget):
            menuScroller.add_widget(box)
            bAnim = Animation(x = 0 - self.width + box.width, y = 0, d = 0.2)
            bAnim.start(menuScroller)

        def done_cAnimYes(anim,widget):
            menuScroller.remove_widget(box)
            def done_dAnim(anim,widget):
                App.get_running_app().New_Game(None)
                return True
            dAnim = Animation(x = 0, y = 0, d = 0.2)
            dAnim.bind(on_complete=done_dAnim)
            dAnim.start(menuScroller)
            return True

        def done_cAnimNo(anim,widget):
            menuScroller.remove_widget(box)
            dAnim = Animation(x = 0, y = 0, d = 0.2)
            dAnim.start(menuScroller)
            return True

        aAmin = Animation(x = 0 - self.width, y = 0, d = 0.3)
        aAmin.bind(on_complete=done_aAnim)
        cAmin = Animation(x = 0 - self.width, y = 0, d = 0.3)

        def yes_callback(instance):
            cAmin.bind(on_complete=done_cAnimYes)
            cAmin.start(menuScroller)
            return True
        def no_callback(instance):
            cAmin.bind(on_complete=done_cAnimNo)
            cAmin.start(menuScroller)
            return True
        yBut = Button(text='Yes', font_size = menuScroller.height * 0.3, size_hint_x = 0.25)
        nBut = Button(text='No', font_size = menuScroller.height * 0.3, size_hint_x = 0.25)
        yBut.bind(on_press=yes_callback)
        nBut.bind(on_press=no_callback)
        lab = Label(text = self.AYStext,
                    italic = True,
                    font_size = menuScroller.height * 0.25,
                    size_hint_x = 1)
        box.add_widget(yBut)
        box.add_widget(nBut)
        box.add_widget(lab)
        if self.parent.has_screen('gameScreen') is True or isfile(App.get_running_app().user_data_dir + '/game.dat') is True:
            aAmin.start(menuScroller)
        else:
            App.get_running_app().New_Game(None)