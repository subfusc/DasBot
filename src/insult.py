import os
import string
from random import randint

insult_list = [line for line in open('insult_db.txt')]

def save_insult(insult):
    
    insult = string.join(insult)
    
    if insult in insult_list:
        return
        
    os.system('echo ' + insult + ' >> insult_db.txt')

def insult(recipient):
    return recipient + ', ' + insult_list[randint(0, len(insult_list)-1)]


if __name__ == "__main__":
    il = [line.strip() for line in open('insult_db.txt')]
    save_insult(['fuck', 'you'], il)
    save_insult(['suck', 'my', 'balls'], il)
    save_insult(['eat', 'shit'], il)
  
    print insult('berlusconi', il)
    print insult('berlusconi', il)
    print insult('berlusconi', il)
    print insult('berlusconi', il)
    print insult('berlusconi', il)
  