import _pickle as cPickle
from os.path import isfile

from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.switch import Switch
from kivy.utils import platform


class BuyButton(Button):
    sku = StringProperty(None)
    name = StringProperty(None)
    id = StringProperty(None)

    def __init__(self, sku, **kwargs):
        self.sku = sku
        self.name = sku.split(".")[-1]
        Logger.info("adding custom widget " + self.name + "_buyButton")
        self.id = self.name + "_buyButton"
        kwargs.setdefault("text", "...thinking")
        super(BuyButton, self).__init__(**kwargs)
        App.get_running_app().billing.bind(consumed=self.checkPurchase)
        self.money_sound = SoundLoader.load("./sounds/money.wav")

    def on_press(self, *args):
        if (
                App.get_running_app().billing.isConsumable(self.sku)
                and self.sku in App.get_running_app().billing.consumed
                and App.get_running_app().billing.consumed[self.sku]
        ):
            # No consuming items at this time
            App.get_running_app().billing.consume(self.sku)
        else:
            App.get_running_app().billing.purchase(self.sku)
        if int(App.get_running_app().config.getdefault("General", "sound", True)) == 1:
            self.money_sound.play()

    def _on_purchase(self, checkFlag):
        widgetDict = {}
        for widget in self.parent.walk():
            # Logger.info("{} -> {}".format(widget, widget.id))
            if (widget.id is not None) and (
                    "flaggedcards" in widget.id or "noads" in widget.id
            ):
                widgetDict[widget.id] = widget
        # Logger.info('---->' + str(widgetDict))
        if checkFlag is True:
            widgetDict[self.name + "_switch"].disabled = False
        else:
            widgetDict[self.name + "_switch"].active = False
            widgetDict[self.name + "_switch"].disabled = True

    def checkPurchase(self, *args):
        if (
                self.sku in App.get_running_app().billing.consumed
                and App.get_running_app().billing.consumed[self.sku]
        ):
            if not App.get_running_app().billing.isConsumable(self.sku):
                if self.text[-6:] != "active":
                    self.text = self.text + " active"
                self.disabled = True
                self._on_purchase(True)
            else:
                # This is not used at the moment
                self.text = "Consumed %s" % self.name
                self.disabled = False
        else:
            self.disabled = False


class ToggleButton(Switch):
    name = StringProperty(None)

    def __init__(self, name, **kwargs):
        self.name = name
        kwargs.setdefault("id", name)
        super(ToggleButton, self).__init__(**kwargs)
        self.deactive_sound = SoundLoader.load("./sounds/ticktock.wav")
        self.active_sound = SoundLoader.load("./sounds/tocktick.wav")
        self.bind(active=self.active_callback)

    def active_callback(self, *args):
        if self.active is True:
            if (
                    int(App.get_running_app().config.getdefault(
                        "General", "sound", True))
                    == 1
            ):
                self.active_sound.play()
            if self.name != "noads_switch":
                for widget in self.parent.walk():
                    # print("{} -> {}".format(widget, widget.id))
                    if (widget.id is not None) and (
                            "flaggedcards" in widget.id and self.name != widget.id
                    ):
                        widget.active = False
        elif (
                int(App.get_running_app().config.getdefault(
                    "General", "sound", True)) == 1
        ):
            self.deactive_sound.play()


class Shop_Screen(Screen):
    def __init__(self, **kwargs):  # Override Screen's constructor
        Logger.info("Shop_Screen init Fired")
        super(Shop_Screen, self).__init__(
            **kwargs
        )  # but also run parent class constructor (__init__)
        innerShopGL = self.ids["innerShopGL"]
        if platform == "android":
            for fullsku in App.get_running_app().billing.skus:
                name = fullsku.split(".")[-1]
                innerShopGL.add_widget(
                    BuyButton(
                        sku=fullsku,
                        size_hint_x=0.8,
                        text=name.split("_")[0] + " flag cards",
                    )
                )
                innerShopGL.add_widget(Label(size_hint_x=0.1))
                innerShopGL.add_widget(
                    ToggleButton(name=name + "_switch",
                                 disabled=True, size_hint_x=0.2)
                )

    def on_enter(self):
        #         popup = Popup(title='Beta Test Warning',
        #                       content=Label(text="Please note, these are live transactions\nand so you will be charged. "),
        #                       size_hint=(0.5,0.5))
        #         popup.open()
        self.Load_Shop()
        for widget in self.walk():
            if widget.id is not None and "_buyButton" in widget.id:
                widget.checkPurchase()
            if (
                    widget.id is not None
                    and "flaggedcards_buyButton" in widget.id
                    and widget.text[-6:] != "active"
            ):
                tmp = widget.id.split("_")[0]
                widget.prettytext = tmp + " card design"
                widget.text = widget.prettytext
            elif (
                    widget.id is not None
                    and "noads_buyButton" in widget.id
                    and widget.text[-6:] != "active"
            ):
                widget.prettytext = "No more ads"
                widget.text = widget.prettytext
            try:
                if widget.id is not None and widget.id[-7:] == "_switch":
                    widget.active = self.shopData[widget.id]
            except:
                if widget.id is not None and widget.id[-7:] == "_switch":
                    widget.active = False

    def on_leave(self):
        tmpCard = None
        for widget in self.walk():
            # print("{} -> {}".format(widget, widget.id))
            if (
                    widget.id is not None
                    and "flaggedcards_switch" in widget.id
                    and widget.active is True
            ):
                flagname = widget.id.split("_")[0]
                Logger.info("set card backs to " + flagname)
                tmpCard = flagname
                break
        App.get_running_app().root.shopCard = tmpCard
        self.Save_Shop()

    def Load_Shop(self):
        if isfile(App.get_running_app().user_data_dir + "/shop.dat") is True:
            Logger.info("Loading in shop.dat")
            try:
                f = open(App.get_running_app().user_data_dir + "/shop.dat")
                self.shopData = cPickle.load(f)
                f.close()
            except Exception as e:
                Logger.info("SHOPDATA LOAD FILE ERROR: " + str(e))

    def Save_Shop(self):
        Logger.info("Save_Shop Fired")
        data = {}
        for widget in self.walk():
            if widget.id is None or widget.id[-7:] != "_switch":
                continue
            data[widget.id] = False
            tmp = widget.id.split("_")
            tmp.pop()
            fullsku = "net.roadtrip2001.kivychicago." + "_".join(tmp)
            Logger.info("Saving SKU switch active data for " + fullsku)
            if widget.disabled is False:
                if (
                        fullsku in App.get_running_app().billing.consumed
                        and App.get_running_app().billing.consumed[fullsku]
                        and widget.active is True
                ):
                    Logger.info("Show data --> " + widget.id + " is True")
                    data[widget.id] = True
                else:
                    Logger.info("Show data --> " + widget.id + " is False")
                    data[widget.id] = False
        try:
            f = open(App.get_running_app().user_data_dir + "/shop.dat", "w")
            cPickle.dump(data, f)
            f.close()
        except:
            Logger.error("Save_Shop Failed")

    def Activate(self, sku):
        pass

    def Deactivate(self, sku):
        pass
