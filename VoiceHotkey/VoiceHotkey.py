import speech_recognition as sr
import keyboard, time, pyttsx3, os, re, configparser, pkg_resources.py2_warn, pyttsx3.drivers, pyttsx3.drivers.sapi5

#Function for pressing and releasing a set of keys. Delay is required by some programs like OBS.
def pressAndRelease(hotkey, timer = 0.2):
        keyboard.send(hotkey, True, False)
        time.sleep(timer)
        keyboard.send(hotkey, False, True)
        
def updateSettings():
    config = configparser.RawConfigParser()
    try:
        config.read('Settings.cfg')

        Bot_Volume = config.getfloat('Bot_Voice', 'Bot_Volume')
        Bot_Talking_Speed = config.getint('Bot_Voice', 'Bot_Talking_Speed')
        Silence_Buffer = config.getfloat('Your_Voice', 'Silence_Buffer')

        print("Successfully imported config")
    except:
        print("Failed to import Settings.cfg. Default values loaded.")
        Bot_Volume = 1.0
        Bot_Talking_Speed = 150
        Silence_Buffer = 0.3

    Talker.volume = float(Bot_Volume)
    Talker.rate = Bot_Talking_Speed
    sr.Recognizer.non_speaking_duration = Silence_Buffer
    sr.Recognizer.pause_threshold = Silence_Buffer

#Parse Commands from Commands.txt
def updateHotkeys():
    i = 0
    hotkeys = []
    try:
        with open ('commands.txt', 'rt') as theFile:
            thisHotkey = Hotkey()
            for theLine in theFile:
                lineText = theLine.replace('\n', '').replace('\r', '').replace(' || ', '||').replace(" --", "--")
                actionType = ""
                action = ""

                #Use blank lines to separate different hotkeys
                if re.fullmatch("\s*", lineText) or lineText == "end of file - do not delete":
                    if thisHotkey.isValid():
                        hotkeys.append(thisHotkey)
                    thisHotkey = Hotkey()
                elif re.search("\s*\#", lineText) == None: 
                    isolatedEvents = lineText.split('||')
                    for i in isolatedEvents:
                        arguements = i.split("--")
                        mainAction = arguements[0]
                        arguements.remove(arguements[0])
                        if len(arguements) == 0:
                            arguements = ["Placeholder6748"]
                        for a in range(len(arguements)):
                            arguements[a] = arguements[a].lower()
                    
                        #Split the command (ex. say) from the message (ex. Hello World)
                        actionType = ""
                        action = ""
                        for j in range(0, mainAction.find(",")):
                            actionType += mainAction[j]
                        for j in range(mainAction.find(',') + 2, len(mainAction)):
                            action += mainAction[j]

                        TheAction = Action(actionType.lower(), action, arguements)
                        thisHotkey.appendAction(TheAction)
    except:
        print("CRITICAL ERROR - Failed to load Commands.txt from local directory")
        print("Please verify that Commands.txt is present, otherwise this program will do nothing.")
        os.startfile("")

    globalVars.hotkeys = hotkeys
    printHotkeys(0)

def printHotkeys(print_actions=1):
    print("Here is a list of your Hotkeys:\n")
    print("====================================================================")
    for i in globalVars.hotkeys:
        i.print(print_actions)
        print("====================================================================")

class Talker:
    engine = pyttsx3.init()

    def say(words):
        print(words)
        if Talker.engine.getProperty('volume') != 0:
            Talker.engine.say(words)
            Talker.engine.runAndWait()

class globalVars:
    hotkeys = []
    UserVariable = ""

class Action:
    def __init__(self, actionType, action, arguements):
        self.actionType = actionType
        self.actionString = action
        self.arguements = arguements
                
    def print(self):
        print(self.actionType.upper() + ": " + self.actionString, end="")
        for arg in self.arguements: 
            if arg != "placeholder6748":
                print(" --" + arg, end="")
        print("") #Newline
    
    def run(self):
        for arguement in self.arguements:
            actionString2= self.actionString.replace("<var>", globalVars.UserVariable)

            if self.actionType == "say":
                if arguement == "mute":
                    print(actionString2)
                else:
                    Talker.say(actionString2)

            elif self.actionType == "run":
                try:
                    if arguement == "batch":
                        os.system(actionString2)
                    else:
                        os.startfile(actionString2)
                except:
                    Talker.say("ERROR")
                    print("The path you input, \"" + actionString2 + "\" could not be found. \nPlease ensure you copied the path correctly.") 

            elif self.actionType == "press":
                pressAndRelease(actionString2)

            elif self.actionType == "type":
                keyboard.write(actionString2)

            elif self.actionType == "sleep":
                time.sleep(float(actionString2))
            elif self.actionType == "set_volume":
                number = actionString2.replace("ten", "10").replace("nine", "9").replace("eight", "8").replace("seven", "7").replace("six", "6").replace("five", "5").replace("four", "4").replace("three", "3").replace("two", "2").replace("one", "1").replace("zero", "0").replace("mute", "0")
                try:
                    Talker.engine.setProperty("volume", float(number)/100)
                except:
                    print("Invalid number: " + actionString2)
            elif self.actionType == "update_hotkeys":
                updateHotkeys()
            else:
                print("ERROR: " + self.actionType + " not recognized")
          
class Hotkey:
    def __init__(self):
        self.triggers = []
        self.actions = []
        self.layer = -1

    def print(self, print_actions=1):
        for i in self.triggers:
            i.print()
        if print_actions:
            for i in self.actions:
                i.print()
    def performActions(self):
        for i in self.actions:
            i.run()

    def appendAction(self, action):
        if action.actionType == "said":
            self.triggers.append(action)
        else:
            self.actions.append(action)    

    def isValid(self):
        return len(self.triggers)!=0

    def wasTriggered(self, wordsSaidRaw):
        wordsSaid = wordsSaidRaw.lower()
        condition = False
        for trigger in self.triggers:
            for arguement in trigger.arguements:
                if arguement == "contains":
                    condition = (trigger.actionString.lower() in wordsSaid)
                elif arguement == "startswith":
                    condition = wordsSaid.startswith(trigger.actionString.lower())
                elif arguement == "regex":
                    condition = re.fullmatch(trigger.actionString, wordsSaid)
                elif arguement == "placeholder6748":
                    condition = wordsSaid == trigger.actionString.lower()
                else:
                    print("INVALID ARGUEMENT: --" + arguement)
                if trigger.actionString.find("<var>") != -1:
                    condition = self.__varEvaluator(trigger.actionString.lower(), wordsSaid)
                if condition:
                    return True
        return False

    def __varEvaluator(self, actionString, wordsSaid):
        phrase = actionString.lower()
        splitPhrase = phrase.split("<var>")
        varInWord = wordsSaid
        for i in splitPhrase:
            varInWord = varInWord.replace(str(i), "")
            if not i in wordsSaid:
                return False
                            
        globalVars.UserVariable = varInWord
        return True



#Setup


updateSettings()

print("Calibrating for ambient Noise...")
r = sr.Recognizer()
#with sr.Microphone() as source:
    #r.adjust_for_ambient_noise(source, 1)
r.energy_threshold = 250  
print("[DEBUG] Energy Threshold: " + str(r.energy_threshold))
r.dynamic_energy_threshold = False
print("")
updateHotkeys()

#Main Execution Loop
while 1:

    with sr.Microphone() as source:
        print("\nAwaiting a command")
        try:
            audio = r.listen(source)               
            try:
                said = r.recognize_google(audio)
                #See if what was said matches any hotkeys, and perform their respective functions
                valid = 0

                for hotkey in globalVars.hotkeys:
                    if hotkey.wasTriggered(said):
                        hotkey.performActions()
                        valid = 1
                
                if not valid:
                    #Talker.say("Not recognized")
                    print("The computer heard:\t " + said + "\nThat doesn't match up with any command.")
      
            #Deal with irritating errors
            except sr.UnknownValueError:
                print("Didn't detect any words")
            except sr.RequestError as e:
                print("CHECK INTERNET CONNECTION: \n Could not request results from Google Speech Recognition service; {0}".format(e))
        except sr.WaitTimeoutError:
            print("timeout")

