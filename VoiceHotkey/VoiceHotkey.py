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
        globalVars.Noise_Threshold = config.getfloat('Your_Voice', 'Noise_Threshold')
        print("Successfully imported config")
    except:
        print("Failed to import Settings.cfg. Default values loaded.")
        Bot_Volume = 100
        Bot_Talking_Speed = 150
        Silence_Buffer = 0.3
        globalVars.Noise_Threshold = 300

    Talker.engine.setProperty("volume", float(Bot_Volume)/100)
    Talker.engine.setProperty("rate",  Bot_Talking_Speed)
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
                lineText = theLine.replace('\n', '').replace('\r', '').replace(' || ', '||').replace( ' && ', '&&').replace(" --", "--")
                actionType = ""
                action = ""

                #Use blank lines to separate different hotkeys
                if re.fullmatch("\s*", lineText) or lineText == "end of file - do not delete":
                    if thisHotkey.isValid():
                        hotkeys.append(thisHotkey)
                    thisHotkey = Hotkey()
                elif re.search("\s*\#", lineText) == None: 
                    isolatedEvents = []
                    if '&&' in lineText:
                        isolatedEvents = lineText.split('&&')
                        thisHotkey.setCompareMode(False)
                        print("Here")
                    elif '||' in lineText:
                        isolatedEvents = lineText.split('||')
                        thisHotkey.setCompareMode(True)
                    else:
                        isolatedEvents = [lineText]
                        #thisHotkey.setCompareMode(True)
                    
                    for i in isolatedEvents:
                        arguements = i.split("--")
                        mainAction = arguements[0]
                        arguements.remove(arguements[0])
                        if len(arguements) == 0:
                            arguements = [""]
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
    Noise_Threshold = 0

class Action:   #A single line.
    def __init__(self, actionType, arguement, modifiers):
        self.type = actionType      #The type of action ex. Say,
        self.arguement = arguement  #The "action string" ex. Yes, I do know Alexa.
        self.modifiers = modifiers  #A modifier ex. --mute
                
    def print(self):
        print(self.type.upper() + ": " + self.arguement, end="")
        for modifier in self.modifiers: 
            if modifier != "":
                print(" --" + modifier, end="")
        print("") #Newline
    
    def run(self):  #run the action #NOTE - This runs once for each arguement given multiple arguements
        for modifier in self.modifiers:
            arg= self.arguement.replace("<var>", globalVars.UserVariable)

            if self.type == "say":
                if modifier == "mute":
                    print(arg)
                else:
                    Talker.say(arg)
            elif self.type == "run":
                try:
                    if modifier == "batch":
                        os.system(arg)
                    else:
                        os.startfile(arg)
                except:
                    Talker.say("ERROR")
                    print("The path you input, \"" + arg + "\" could not be found. \nPlease ensure you copied the path correctly.") 
            elif self.type == "press":
                try:
                    pressAndRelease(arg, float(modifier))
                except:
                    if not modifier == "":
                        print("Invalid number: " + modifier + ". Please change the modifier in the config file to a number. /n Keys have been presed for 0.2 seconds.")
                    pressAndRelease(arg)

            elif self.type == "type":
                keyboard.write(arg)

            elif self.type == "sleep":
                time.sleep(float(arg))
            elif self.type == "set_volume":
                arg = arg.replace("ten", "10").replace("nine", "9").replace("eight", "8").replace("seven", "7").replace("six", "6").replace("five", "5").replace("four", "4").replace("three", "3").replace("two", "2").replace("one", "1").replace("zero", "0").replace("mute", "0")
                try:
                    Talker.engine.setProperty("volume", float(arg)/100)
                except:
                    print("Invalid number: " + arg)
            elif self.type == "update_hotkeys":
                updateHotkeys()
            else:
                print("ERROR: " + self.type + " not recognized")
          
class Hotkey:
    def __init__(self):
        self.triggers = []          #array of actions that trigger this hotkey (the full line, separated by OR's)
        self.compareMode = True     #1 is OR, 0 is AND
        self.actions = []           #array of actions that the hotkey is made up of (the full line)
        self.layer = -1             #Will be used for nesting (later)
    def setCompareMode(self, mode):
        self.compareMode = mode
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
        if action.type == "said":
            self.triggers.append(action)
        else:
            self.actions.append(action)    

    def isValid(self):
        return len(self.triggers)!=0

    def wasTriggered(self, wordsSaidRaw):   #currently only triggered by "said" lines
        wordsSaid = wordsSaidRaw.lower()
        condition = False
        for trigger in self.triggers:
            for modifier in trigger.modifiers:
                if modifier == "contains":
                    condition = (trigger.arguement.lower() in wordsSaid)
                elif modifier == "startswith":
                    condition = wordsSaid.startswith(trigger.arguement.lower())
                elif modifier == "regex":
                    condition = re.fullmatch(trigger.arguement, wordsSaid)
                elif modifier == "":
                    condition = wordsSaid == trigger.arguement.lower()
                else:
                    print("INVALID ARGUEMENT: --" + modifier)
                if trigger.arguement.find("<var>") != -1:
                    condition = self.__varEvaluator(trigger.arguement.lower(), wordsSaid)
                if self.compareMode and condition:  #OR mode, a condition is true
                    return True
                elif not self.compareMode and not condition: #AND mode, a condition is false
                   return False

        return not self.compareMode

    def __varEvaluator(self, actionString, wordsSaid): #splits what was said to see if the command was correct, then assigns a value to var.
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
r.energy_threshold = globalVars.Noise_Threshold  
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