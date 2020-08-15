=================================================================================
HOW TO RUN:
=================================================================================
1. Add your voice commands in the Commands.txt file (more instructions within that file)
2. (Optional) Edit the Settings.cfg file with notepad
3. Double-click on VoiceHotkey.exe
=================================================================================





=========================================================================================
HOW TO MAKE YOUR OWN COMMMANDS
=========================================================================================

Each line is made up of an Action Type, an Arguement, and (optionally) a Modifier
Putting a bunch of lines makes a command

----------------------------------------------------------------------------------------
The Action type dictates how the line should be interpreted, and the Arguement is what actually gets carried out.
		- "Said" makes the computer listens for the specified text, and runs the rest of the lines in the command when it hears it.
		- "Say" makes the computer speak
		- "Run" will run whichever program you specify.
		- "Type" will type the text that you specify
		- "Press" will press the specified keys on your keyboard
		- "Sleep" will pause the program for a specified number of seconds

----------------------------------------------------------------------------------------
 <var> stands for variable. It will hold all the words you say between the defined words 
		(Try the "My number" example, and it will make much more sense)
		
----------------------------------------------------------------------------------------
There are also modifiers you can put at the end of some actions. They come after " --"
		Works with the "Said" Action Type:
			"--contains" 	- If what you said contains the specified phrase, the rest of the command runs
			"--startsWith"	- If what you said starts with the specified phrase, the rest of the command runs
			"--regex"		- If what you said is a regex match with the specified phrase, the rest of the command runs (see https://docs.python.org/3/library/re.html) 
		Works with the "say" Action Type:
			"--mute"		-Prints the specified text to the console, but doesn't actually say it out loud
		Works with the "run" Action Type:
			"--batch"		-Runs the arguement as a batch command rather than a program that needs to be opened.

----------------------------------------------------------------------------------------
Anything starting with a "#" is a comment. The program will ignore these.
	
========================================================================================
