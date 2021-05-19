
from guizero import App, Text, PushButton, Box
import dbHandler as db
import time
import readChip
import configReader
import RPi.GPIO as GPIO

#counts all entries of a query an generates pages
def countPages(aList,aPages):
	#Due to pass by reference from lists there has to be added a list for every
	#entry.
	tmp = []
	splitCounter= 0
	listCounter=0
	for entry in aList:
		if splitCounter > 8:
			for i in tmp:
				aPages[listCounter].append(i)
			splitCounter=0
			tmp.clear()
			aPages.append([])
			listCounter +=1
		tmp.append(entry)
		splitCounter+=1
		
	for entry in tmp:
		aPages[listCounter].append(entry)
		
#format Strings to look good 
def drinkFormatter(drink):
	#convert price(float) into a string and count the chars. If there are
	#less than 4 it means, that the price is 0.4 and missing a 0 at the end
	tmp = 0
	#convert float to string
	preis = f"{drink[3]}"
	
	#iterate over the chars and count them
	for char in preis:
		tmp += 1
	#if they are less than 4 add a 0
	if tmp < 4:
		preis = preis + "0"
	#combine name and price as label for the button
	tmp = f"{drink[2]}\n{preis}€"
	return tmp

def userFormatter(user):
	tmp = ""
	name = user[0]
	fName = user[1]
	tmp = f"{name} {fName}"
	return tmp
	
def scanRFID():
	global scanActive
	global endTime
	global RFID
	global masterBox
	global currentView
	global messageActive
	
	if messageActive:
		if time.time() > endTime:
			messageActive = False
			endTime = 0
			backToPreviousView()
			
	if scanActive:
		if time.time()< endTime:
			print("Scanning")
			RFID = readChip.scan()
			if len(RFID)> 1:
				print("Stop scanning")
				scanActive = False
				if currentView=="Main":
					global selectedDrink
					query= db.buyDrink(RFID,selectedDrink[0],selectedDrink[3])
					RFID = "0"
					selectedDrink = 0
					showMessage(query)
					
				elif currentView=="UserDetails":
					global selectedUser
					query=db.setRFID(RFID,selectedUser[3])
					RFID = "0"
					selectedUser = 0
					#update local db-copy
					clearLocalDB()
					updateLocalDB()
					showMessage(query)
					
		else:
			print("Stop scanning")
			scanActive = False
			if currentView=="Main":
				masterBox.destroy()
				generateMain(1)
				selectedDrink = 0
				
			elif currentView=="UserDetails":
				currentView = "Admin"
				generateUsers(1)
				selectedUser = 0

def showMessage(query):
	global masterBox
	global endTime
	global messageActive
	messageActive = True
	masterBox.destroy()
	masterBox = Box(app,width="fill",height="fill",border=True)
	if query == None:
		generateHeader("Erfolg!",None)
		infoBox = Box(masterBox,width=screenX/2,height=screenY/2,align="top")
		if currentView=="Main":
			info = Text(infoBox,align="top",text="Der Kauf des Getränks war erfolgreich!")
		elif currentView=="UserDetails":
			info = Text(infoBox,align="top",text="Das Einscannen der neuen RFID war erfolgreich!")
		endTime = time.time() + 2

	else: 
		generateHeader("Fehler!",None)
		infoBox = Box(masterBox,width=screenX/2,height=screenY/2,align="top")
		if currentView=="Main":
			info = Text(infoBox,align="top",text="Fehler bei der Transaktion. Fehlercode:")
			info2 = Text(infoBox,align="top",text=f"query")
		elif currentView=="UserDetails":
			info = Text(infoBox,align="top",text="Fehler beim Schreiben der neuen RFID. Fehlercode:")
			info2 = Text(infoBox,align="top",text=f"query")
		endTime = time.time() + 2
		
def abortScan():
	#by setting the endTime to the actual time the loop comes to a natural
	#end, sets all the switches back an turns to the previous view
	print("Aborting...")
	global endTime
	endTime = time.time()

#whenever the user clicks a drink, he will be ask to scan the RFID chip and
#the drink will be bought
def drinkTransaction(tmpDrink):
	global masterBox
	global scanActive 
	global endTime
	global selectedDrink
	selectedDrink = tmpDrink
	#the Idea here is, that the scan-Function is automatically called every 100ms but if the Bool scanActive is False nothing happens
	masterBox.destroy()
	masterBox = Box(app,width="fill",height="fill",border=True)
	generateHeader("Scanne nach Chip...",None)
	buyTxt= Text(masterBox,width="fill",height="fill",align="top",text=f"Auswahl: {drinkFormatter(tmpDrink)}\nBitte Chip auflegen...")
	abortButton = PushButton(masterBox,width="fill",height="fill",align="top",command=abortScan,text="Abbrechen")
	abortButton.tk.config(font=("Verdana",dynamicTextSize))
	buyTxt.tk.config(font=("Verdana",dynamicTextSize))
	scanActive = True
	endTime = time.time()+10
	
#dummy command - will open window for Admin Panel
def generateAdmin():
	global currentView
	currentView = "Admin"
	showNumPad(None)

#If you are in a Menue you can go back with this command
def backToPreviousView():
	global currentView
	global masterBox
	if currentView == "User":
		masterBox.destroy()
		generateMain(1)
	elif currentView == "UserDetails":
		currentView = "Admin"
		generateUsers(1)
	elif currentView == "Admin":
		masterBox.destroy()
		generateMain(1)
	elif currentView == "Main":
		masterBox.destroy()
		generateMain(1)
		
#select user and show details and options
def selectUser(user):
	global masterBox
	global currentView
	currentView = "UserDetails"
	masterBox.destroy()
	masterBox = Box(app,width="fill",height="fill",border=True)
	uName = userFormatter(user)
	uRFID = user[2]
	generateHeader(uName,user)
	limit = int(user[4])
	
	limitText = ""
	if limit > 0:
		limitText = f"Benachrichtigen bei {limit}€"
	else:
		limitText = "Derzeit keine\nBenachrichtigungen eingerichtet."
	
	
	#Display Name and CHIP-ID on the left
	infoBox = Box(masterBox, width=screenX/2,height=screenY,align="left",border=True)
	userTxt = Text(infoBox,width="fill",height="2",align="top",text=f"User: {uName}")
	idTxt = Text(infoBox,width="fill",height="2",align="top",text=f"ChipID: {uRFID}")
	limitTxt = Text(infoBox,width="fill",height="2",align="top",text=f"{limitText}")

	userTxt.tk.config(font=("Verdana",dynamicTextSize))
	idTxt.tk.config(font=("Verdana",dynamicTextSize))
	limitTxt.tk.config(font=("Verdana",dynamicTextSize))
	
	#Display available Options on the right
	optionsBox = Box(masterBox, width=screenX/2,height=screenY,align="right",border=True)
	limitButton = PushButton(optionsBox,args=[user], width="fill", height="fill",align="top", command=registerRFID,text="Chip registrieren")
	#noChipButton = PushButton(optionsBox, width="fill", height="fill",align="top", command=noChip,text="Buchung ohne Chip")
	
	limitButton.tk.config(font=("Verdana",dynamicTextSize))

def registerRFID(usr):
	global masterBox
	global scanActive 
	global endTime
	global selectedUser
	uName = userFormatter(usr)
	masterBox.destroy()
	masterBox = Box(app,width="fill",height="fill",border=True)
	generateHeader(uName,usr)
	infoBox = Box(masterBox,width=screenX/2,height=screenY/2,align="top",border=True)
	infoText = Text(infoBox,align="top",text="Bitte neuen Chip an den Lesebereich halten...")
	abortButton = PushButton(masterBox,width="fill",height="fill",align="top",command=abortScan,text="Abbrechen")
	
	abortButton.tk.config(font=("Verdana",dynamicTextSize))
	infoText.tk.config(font=("Verdana",dynamicTextSize))
	scanActive = True
	endTime = time.time()+10
	selectedUser = usr
	
def numpadKeyPress(inp,inpList,usr,txtField):
	global currentView
	global numTextInput#splitdrinks into pages
	
	#clear the whole list
	if inp == "C":
		inpList.clear()
	#delete last input
	elif inp == "D":
		if len(inpList)>0:
			inpList.pop(-1)
	#if ok is pressed, safe values and close window
	elif inp == "OK":
		numPadOK(inpList,usr)
		return
	#if abort is pressed, do not save value and close window
	elif inp == "AB":		
		numPadAbort(usr)
		return
	else:
	#if a digit is pressed, append it to the list
		inpList.append(inp)
	tmp = ""
	#combine all numbers from the list to a string
	for entry in inpList:
		tmp += entry
	#save the input in a global variable
	numTextInput = tmp
	#if we are in the Admin panel, hide digits
	if currentView == "Admin":
		txtField.clear()
		tmpL= len(tmp)
		tmp = ""
		if tmpL>=1:
			tmp+="*"
			
		for i in range(1,tmpL):
			tmp+= "*"
		txtField.append(tmp)
	#if not, show digits
	else:		
		txtField.clear()
		txtField.append(tmp)
	
def numPadOK(inpList,usr):
	global numTextInput
	global currentView
	global users
	global userPages
	global currentPage
	#concatenate Input to a string
	tmp = ""
	for entry in inpList:
		tmp += entry
	numTextInput = tmp
	print(numTextInput)
	
	if currentView == "Admin":
		if config["appAdmin"] == tmp:
			generateUsers(1)
		else:
			print("Falsches Adminpasswort")
			numPadAbort(None)
	
def numPadAbort(usr):
	global currentView
	global masterBox
	if currentView == "Admin":
		masterBox.destroy()
		generateMain(1)
	
def showNumPad(usr):
	global masterBox
	global numTextInput
	masterBox.destroy()
	masterBox = Box(app,width="fill",height="fill",border=True)
	
	digitBoxW = screenX/2
	digitBoxH = (screenY/3)*2
	digitInput = []
	
	digitBox = Box(masterBox,width=digitBoxW ,height=digitBoxH,border=True)
	#calculate digit-button width and height
	digitX = digitBoxW/3
	digitY = digitBoxH/4
	#generate buttons for digits, delete, accept and cancel
	#add digits 1-9
	overBox = Box(digitBox, width=digitBoxW,height= digitY,align="top",border=True)
	
	#add a TextField das shows the input
	displayText= Text(overBox,width="fill", height="fill",align="top",text="")	
	
	overBox = Box(digitBox, width=digitBoxW,height= digitY,align="top",border=True)
	for i in range (1,10):
		tmpBox = Box(overBox, width=digitX,height= digitY,align="left",border=True)
		tmpButton=PushButton(tmpBox,args=[f"{i}",digitInput,usr,displayText], width="fill", height="fill",align="top", command=numpadKeyPress,text=f"{i}")
		#adapt FontSize
		tmpButton.tk.config(font=("Verdana",dynamicTextSize))
		if i%3 ==0:
			overBox = Box(digitBox, width=digitBoxW,height= digitY,align="top",border=True)
	#add clear, zero and delete
	#clear
	tmpBox= Box(overBox, width=digitX, height=digitY,align="left",border=True)
	tmpButton=PushButton(tmpBox,args=["C",digitInput,usr,displayText],width="fill", height="fill",align="top", command=numpadKeyPress,text="C")
	tmpButton.tk.config(font=("Verdana",dynamicTextSize))
	#Zero	
	tmpBox = Box(overBox, width=digitX, height=digitY,align="left",border=True)
	tmpButton=PushButton(tmpBox,args=["0",digitInput,usr,displayText], width="fill", height="fill",align="top", command=numpadKeyPress,text="0")
	tmpButton.tk.config(font=("Verdana",dynamicTextSize))
	#Delete
	tmpBox = Box(overBox, width=digitX, height= digitY,align="left",border=True)
	tmpButton=PushButton(tmpBox, args=["D",digitInput,usr,displayText],width="fill", height="fill",align="top", command=numpadKeyPress,text="<-")
	tmpButton.tk.config(font=("Verdana",dynamicTextSize))
	#add accept and cancel
	overBox = Box(digitBox, width=digitBoxW,height= digitY,align="top",border=True)
	tmpBox = Box(overBox, width=digitBoxW, height=digitY,align="left",border=True)
	tmpButton=PushButton(tmpBox, args=["OK",digitInput,usr,displayText],width="fill", height="fill",align="top", command=numpadKeyPress,text="OK")
	tmpButton.tk.config(font=("Verdana",dynamicTextSize))
	tmpBox = Box(overBox, width=digitBoxW,height= digitY,align="left",border=True)
	tmpButton=PushButton(tmpBox,args=["AB",digitInput,usr,displayText], width="fill", height="fill",align="top", command=numpadKeyPress,text="Abbrechen")
	tmpButton.tk.config(font=("Verdana",dynamicTextSize))
	
def generateButtons(aList,rPage):
	#first box for buttons
	global containerX
	global containerY
	global masterBox
	global currentView
	box = Box(masterBox, width="fill",height=containerY,border=True)
	rowCounter = 0
	buttonCounter = 0
	for entry in aList[rPage]:
		if rowCounter > 2:
			box = Box(masterBox, width="fill", height=containerY,border=True)
			rowCounter = 0
		
		if rowCounter == 0:
			containerBox = Box(box,width=containerX, height=containerY,align="left",border=True)
			if currentView=="User" or currentView=="Admin":
				aButton = PushButton(containerBox, args=[entry],width="fill", height="fill",align="left", command=selectUser,text=userFormatter(entry))
			elif currentView=="Main":
				aButton = PushButton(containerBox, args=[entry],width="fill", height="fill",align="left", command=drinkTransaction,text=drinkFormatter(entry))
		
		if rowCounter == 1:
			containerBox = Box(box,width=containerX, height=containerY,align="left",border=True)
			if currentView=="User" or currentView=="Admin":
				aButton = PushButton(containerBox, args=[entry],width="fill", height="fill",align="left", command=selectUser,text=userFormatter(entry))
			elif currentView=="Main":
				aButton = PushButton(containerBox, args=[entry],width="fill", height="fill",align="left", command=drinkTransaction,text=drinkFormatter(entry))
		
		if rowCounter == 2:
			containerBox = Box(box,width=containerX, height=containerY,align="left",border=True)
			if currentView=="User" or currentView=="Admin":
				aButton = PushButton(containerBox, args=[entry],width="fill", height="fill",align="right", command=selectUser,text=userFormatter(entry))
			elif currentView=="Main":
				aButton = PushButton(containerBox, args=[entry],width="fill", height="fill",align="right", command=drinkTransaction,text=drinkFormatter(entry))
		
			
		aButton.tk.config(font=("Verdana",dynamicTextSize))
		rowCounter += 1
		buttonCounter += 1

	if buttonCounter < 8:
		remainders = 8 - buttonCounter
		for i in range(buttonCounter+1,10):
			if rowCounter > 2:
				box = Box(masterBox, width="fill", height=containerY,border=True)
				rowCounter = 0
				
			if rowCounter == 0:
				containerBox = Box(box,width=containerX, height=containerY,align="left",border=True)
				emptyButton = PushButton(containerBox, width="fill", height="fill",align="left", text="")
			if rowCounter == 1:
				containerBox = Box(box,width=containerX, height=containerY,align="left",border=True)
				emptyButton = PushButton(containerBox,width="fill", height="fill",align="left",text="")
			if rowCounter == 2:
				containerBox = Box(box,width=containerX, height=containerY,align="left",border=True)
				emptyButton = PushButton(containerBox,width="fill", height="fill",align="right", text="")
			emptyButton.enabled = False
			emptyButton.tk.config(font=("Verdana",dynamicTextSize))
			rowCounter += 1
			buttonCounter += 1


		
def generateHeader(txt,usr):
	global masterBox
	global currentView 
	global message
	message = txt
	
	#Setup of the options bar on Top of the screen
	headerBox = Box(masterBox, width=screenX,height=headerBarY,border=True)
	settingsButton = PushButton(headerBox,width="5",height="2",align="right",command=generateAdmin,text="Admin")
	infoOutput = Text(headerBox,width="fill",height="2",align="right",text=f"{message}")
	if currentView=="Main":
		return
		#Currently there is no need for the Users to access the User Window
		#UserButton= PushButton(headerBox, width="5",height="2",align="left",command=generateUsers,text="Benutzer")
	elif currentView=="User" or currentView=="UserDetails":
		UserButton= PushButton(headerBox,width="5",height="2",align="left",command=backToPreviousView,text="Zurück")
	elif currentView == "Admin":
		UserButton= PushButton(headerBox,width="5",height="2",align="left",command=backToPreviousView,text="Zurück")
		
def generateNavigation(currPage, maxPage):
	global masterBox
	#Setup of the navigationBar on bottom of the screen
	navigationBox = Box(masterBox, width=screenX,height=headerBarY,border=True)
	nextPage = PushButton(navigationBox,args=[masterBox],width="5",height="2",align="right",command=goToNextPage,text="->")
	pageOutput = Text(navigationBox,width="fill",height="2",align="right",text=f"Seite: {currPage}/{maxPage}")
	previousPage= PushButton(navigationBox,args=[masterBox],width="5",height="2",align="left",command=goToPreviousPage,text="<-")
	if maxPage < 2:
		nextPage.enabled = False
		previousPage.enabled = False
# open window for Admin User&functions
def generateUsers(page):
	global currentView
	global masterBox
	masterBox.destroy()
	
	#substract 1 from page to apply on list index
	realPage = page-1
	#box that contains all Items for easy remove and redraw
	masterBox = Box(app,width="fill",height="fill",border=True)

	#Setup of the options bar on Top of the screen
	generateHeader(currentView,None)

	#setup the buttons with the users
	generateButtons(userPages,realPage)

	generateNavigation(currentPage,maximalPageUsers)
	
#will go to next page
def goToNextPage(masterBox):
	global currentPage
	global currentView
	if currentView=="Main":
		maxPag = maximalPageDrinks
	else:
		maxPag = maximalPageUsers
	if currentPage+1 > maxPag:
		print("Nix is")
		return
	else:
		currentPage+=1
		if currentView == "Main":
			masterBox.destroy()
			generateMain(currentPage)
		elif currentView== "User":
			generateUsers(currentPage)
			
#will go to previous page
def goToPreviousPage(masterBox):
	global currentPage
	if currentPage-1 < 1:
		print("Nix is")
		return
	else:
		currentPage-=1
		if currentView == "Main":
			masterBox.destroy()
			generateMain(currentPage)
		elif currentView== "User":
			generateUsers(currentPage)
	
def generateMain(page):
	global currentView
	global masterBox
	currentView = "Main"
	#substract 1 from page to apply on list index
	realPage = page-1
	#box that contains all Items for easy remove and redraw
	
	masterBox = Box(app,width="fill",height="fill",border=True)

	#Setup of the options bar on Top of the screen
	generateHeader("Getränkeauswahl",None)

	generateButtons(drinkPages,realPage)

	generateNavigation(currentPage,maximalPageDrinks)

def deconstruct():
	print("deconstruct")
	GPIO.cleanup()
	db.terminateConnection()

#in cases where Users or Drinks are updated first the local cache has to be cleared...	
def clearLocalDB():
	global users
	global drinks
	global drinkPages
	global userPages
	
	drinks.clear()
	users.clear()
	drinkPages.clear()
	userPages.clear()
	
	drinks = []
	users = []
	drinkPages = [[]]
	userPages = [[]]
		
#... and then the local cache get's updated (refetch everything from the DB)
def updateLocalDB():
	global users
	global drinks
	global drinkPages
	global userPages

	drinks = db.fetchAllDrinks()
	users = db.fetchAllCustomers()

	#Count drinks and users and split them up in different pages
	countPages(drinks,drinkPages)
	countPages(users,userPages)

	
config = configReader.parseFile("app")

drinks = []
users = []
drinkPages = [[]]
userPages = [[]]
updateLocalDB()

#message for the headerBar
message = ""
numTextInput = ""
#variable to track current page
currentPage = 1
currentView = "Main"

#Variables for RFID Scan
RFID = "0"
scanActive = False
endTime = 0
selectedDrink = 0
selectedUser = 0
messageActive = False
#split drinks and users into pages
maximalPageDrinks = len(drinkPages)
maximalPageUsers = len(userPages)

screenX = 1024
screenY = 600

#Adjust text size to window resolution
dynamicTextSize = int(screenY/35)

#calculate size for containerBox for buttons
#width is 1/3 of the window width.
#height is 1/7 for the headerBar and 2/7 for each button
containerX = int(screenX/3)
containerY = int(screenY/8)*2
#calculate size for
headerBarY = int(screenY/8)

#instantiate app	
app = App(title=config["appName"], layout="auto",width=screenX, height=screenY)
app.when_closed = deconstruct

generateMain(1)

app.repeat(100,scanRFID)

GPIO.cleanup()
#load all and display app
app.display()
 
