from kivy.app import App
from kivy.logger import Logger
import webbrowser

def Widget_ToTop(layout, widget):
    layout.remove_widget(widget)
    layout.add_widget(widget)
    return True

def Get_Next_Player(player, numOfPlayers):
    if player == numOfPlayers:
        return 1
    else:
        return player + 1

def Get_Config_Bool(cID):
    try:
        if int(cID) == 1:
            return True
    except:
        return False
    return False

def Configed_Bool(section, key):
    try:
        if int(App.get_running_app().config.getdefault(section,key,True)) == 1:
            return True
    except:
        pass
    return False

def Goto_Link(instance, url):
    webbrowser.open(url)

def Debug_Mem(children):
    #from screen - Debug_Mem(self.ids[l].children)
    #Logger.Info(str(self.hp.heap()))
    tmp = ('infoFloat', 'topBoxLayout','mainFloat')
    for l in tmp:
        debugMem =  {
                        'Image':        0,
                        'Label':        0,
                        'Scatter':      0,
                        'Other':        0
                    }
        for child in children:
            if 'Image' in str(child):
                debugMem['Image'] += 1
            elif 'Label' in str(child):
                debugMem['Label'] += 1
            elif 'Scatter' in str(child):
                debugMem['Scatter'] += 1
            else:
                debugMem['Other'] += 1
        Logger.info("mem stats for " + l + ':')
        Logger.info(str(debugMem))