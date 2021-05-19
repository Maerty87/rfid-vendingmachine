# rfid-vendingmachine

The idea behind this project is to make a device with a touch-screen from which users can choose goods to buy (i.E. Drinks), identify themselves with their RFID-Chip thus finishing the transaction.
Usernames with RFIDs, product names and prices and all transactions are all stored in a database which the software retrieves at start.

This code is subdivided in different "Modules" (python-files) for better reuasability and simplicity.
The file where it all comes together is the "MainWindow.py". 

IMPORTANT!
For this Software to work properly you'll need an RFID Reader MFRC522 connected to your RPi.
Furthermore a you need a database with the data.
Please note that the SQL-Queries in the dbHandler.py need to be changed in order to work with your database-tables.

Additional info:
No commercial purpose of this software is intended. It is a practical test for my skills and it helps my collegue to be a little bit more efficient. 

Thanks to Freenove for the MFRC522.py file! No changes were made to this file as it is just what we need :)
I got the RFID module and most of the information for this project from the Freenove RFID Starter Kit. 
(The Code from Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License (CC BY-NC-SA 3.0))
