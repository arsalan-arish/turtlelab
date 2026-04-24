""" This holds all exceptions used inside the application """

class TabRefusedToClose(Exception):
    """ rmTab was called to remove and delete a tab, but it sent a refusal signal (this exception) """
    
