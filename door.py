import hashlib
from time import sleep
from gpiozero import LED
from db import db_query, db_query_match
from nfc_reader import nfc_setup, nfc_loop


print("\n")


# hash the username
def hash_username(cleartext_usrname):
    hashed_usrname = hashlib.sha256(cleartext_usrname.encode()).hexdigest()
    return hashed_usrname


# get passwd and save as a global string(hashed)
def get_passwd(cleartext_passwd):
    global hashed_passwo
    hashed_passwd = hashlib.sha256(cleartext_passwd.encode()).hexdigest()
    return hashed_passwd


# function to open the door. in testing, just prints
def open_sesame():
    usrname_led.on()
    passwd_led.on()
    print("Door has been opened")
    return

def close_sesame():
    print("Door has been closed")
    usrname_led.off()
    passwd_led.off()
    return


# flashes both LEDs
def flash_both_led(time):
    for num in range(time):
        print(f"Locked out for {time - num} more seconds")
        usrname_led.on()
        passwd_led.on()
        sleep(0.5)
        usrname_led.off()
        passwd_led.off()
        sleep(0.5)


# TODO figure out how to add color to this logic
def change_led(category, action):
    if category == usrname_led:
        if action == 1:
            usrname_led.on()
        if action == 0:
            usrname_led.off()
    if category == passwd_led:
        if action == 1:
            passwd_led.on()
        if action == 0:
            passwd_led.off()


# main program runs from here
if __name__ == "__main__":

    # initial variables setup
    fuckups = 0
    hashed_usrname = ""
    hashed_passwd = ""
    usrname_check = False
    passwd_check = False
    match_check = False
    usrname_led = LED(12)
    passwd_led = LED(5)
    change_led(usrname_led, 0)
    change_led(passwd_led, 0)

    # running program in a loop

    nfc_setup()
    while True:

        # usrname check loop
        while not usrname_check:
            result = nfc_loop()
            if result:
                hashed_usrname = hash_username(result)
            else: 
                continue

            # admin override using magic hash_data
            if hashed_usrname == "7485f7f14090849ddbece011de103c40eadcdc0031885dc29f899f3c5a727428":
                change_led(usrname_led, 1)
                fuckups = 0
                usrname_check = True

            # compare usrname to creds.db
            if db_query(hashed_usrname, "queried_usrname"):
                change_led(usrname_led, 1)
                fuckups = 0
                usrname_check = True

            # incorrect input
            else:
                fuckups += 1
                print(f"Incorrect user, try again.You have {3 - fuckups} attempts left")
                flash_both_led(1)
                usrname_check = False

            # timeout after 3 incorrect input
            if fuckups > 2:
                print("Too many incorrect attempts, pls wait 30s and try again")
                flash_both_led(30)
                sleep(30)
                fuckups = 0

        # passwrd check loop
        while not passwd_check:
            get_passwd(input("Please enter your passwd\n"))

            # admin override using magic hash_data
            if hashed_passwd == "936867247aef14d232e539bd3f08b2c6bc47afe56a774ede3488d66006cbeb95":
                change_led(passwd_led, 1)
                passwd_check = True

            # compare usrname to creds.db
            if db_query(hashed_passwd, "queried_passwd"):
                change_led(passwd_led, 1)
                passwd_check = True

            # incorrect input
            else:
                fuckups += 1
                print(f"Incorrect passwd, try again.You have {3 - fuckups} attempts left")
                flash_both_led(1)
                passwd_check = False
                usrname_check = False

            # timeout after 3 incorrect input
            if fuckups > 2:
                print("Too many incorrect attempts, pls wait 30s and try again")
                flash_both_led(5)
                fuckups = 0
                usrname_check = False

            # check that usrname and passwd match
            if db_query_match(hashed_usrname, hashed_passwd):
                match_check = True
            else:
                print("Username and password do not match")
                passwd_check = False
                fuckups += 1

        # opens the door. TODO Need to write protective logic around this function
        if usrname_check and passwd_check and match_check:
            open_sesame()
            sleep(5)
            close_sesame()
            usrname_check = False
            passwd_check = False
            match_check = False
            fuckups = 0
