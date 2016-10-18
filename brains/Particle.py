from kivyparticle import ParticleSystem
from kivy.uix.widget import Widget
from kivy.clock import Clock
#from kivy.logger import Logger

class Particle(Widget):

    def __init__(self, **kwargs):
        super(Particle, self).__init__(**kwargs)
#        self._show(self.sun)
#    def on_touch_down(self, touch):
#        self.current.emitter_x = float(touch.x)
#        self.current.emitter_y = float(touch.y)
#    def on_touch_move(self, touch):
#        self.current.emitter_x = float(touch.x)
#        self.current.emitter_y = float(touch.y)

    def show(self, **kwargs):
        if self.current:
            self.remove_widget(self.current)
            self.current.stop(True)
        self.current = self.effect[kwargs.get('id')]

        try:
            self.current.emitter_x = float(kwargs.get('x'))
        except:
            self.current.emitter_x = 100
        try:
            self.current.emitter_y = float(kwargs.get('y'))
        except:
            self.current.emitter_y = 100

        layout = kwargs.get('layout')
        layout.add_widget(self.current)
        self.current.start()

    def unshow(self, layout):
        self.current.emitter_x = -1000
        self.current.emitter_y = -1000
        def done(dt):
            self.current.stop()
            layout.remove_widget(self.current)
        Clock.schedule_once(done, 3)

    def __enter__(self):
        self.effect = {
            'sun': ParticleSystem('./effects/sun.pex'),
            'royal': ParticleSystem('./effects/royal.pex'),
            'niceone': ParticleSystem('./effects/twopair.pex'),
            #'drugs': ParticleSystem('./effects/drugs.pex'),
            #'jellyfish': ParticleSystem('./effects/jellyfish.pex'),
            #'fire': ParticleSystem('./effects/fire.pex'),
            #'twopair': ParticleSystem('./effects/twopair.pex'),
            #'threekind': ParticleSystem('./effects/threekind.pex'),
            #'flush': ParticleSystem('./effects/flush.pex'),
            #'fullhouse': ParticleSystem('./effects/fullhouse.pex'),
            #'royal': ParticleSystem('./effects/royal.pex'),
            #'straight': ParticleSystem('./effects/straight.pex'),
            #'straightflush': ParticleSystem('./effects/straightflush.pex')
        }
        self.current = None
        return self

    def __exit__(self, typ, val, tb):
        def cleanUp(dt):
            self.effect = None
            self.current = None
        Clock.schedule_once(cleanUp, 20)

