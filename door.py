import hashlib
import sqlalchemy as db
from time import sleep 
#from gpiozero import LED
print("\n")

# get usrname and save as a global string(hashed)
def get_usrname(cleartext_usrname):
    global hashed_usrname 
    hashed_usrname = hashlib.sha256(cleartext_usrname.encode()).hexdigest()
    print(hashed_usrname)

# get passwd and save as a global string(hashed)
def get_passwd(cleartext_passwd):
    global hashed_passwd
    hashed_passwd = hashlib.sha256(cleartext_passwd.encode()).hexdigest()
    print(hashed_passwd)

# insert new member (still in testing)
def insert(hashed_usrname, hashed_passwd):
    query = db.insert(Users).values(usrname=hashed_usrname, passwd=hashed_passwd)
    result = conn.execute(query)
    if result.is_insert:
        print(f"inserted")
    else:
        print("not inserted.")
        return

# check if the usrname is in the db
def query_creds(hash, type):
    output = conn.execute(f"SELECT * FROM members WHERE {type}= {hash}")
    print(output.fetchall())

# function to open the door. in testing, just prints 
def open_door():
    print("the door is OPEN\n")
    print("sleep 15 seconds")
    # usrname_led.off()
    # passwd_led.off()

# whole loop is 1s
def flash_led(time):
    for num in range(time):
        print("flashing LED " + str(time) + " times, pulse "+ str(num))
        # usrname_led.on()
        # passwd_led.on()
        # sleep(0.5)
        # usrname_led.off()
        # passwd_led.off()
        # sleep(0.5)

# main program runs from hhere
if __name__ == "__main__":
    
    # initial variables setup
    fuckups = 0
    hashed_usrname= ""
    hashed_passwd = ""
    
    # LED types 
    # usrname_led = LED(17)
    # passwd_led = LED(21)
    
    # db setup
    engine = db.create_engine("sqlite:///creds.db")
    conn = engine.connect()
    metadata = db.MetaData()
    # tables setup
    Users = db.Table('members', metadata,
                db.Column('usrname', db.CHAR(64),primary_key=True),
                db.Column('passwd', db.CHAR(64), nullable=False),
              )
    metadata.create_all(engine)

    # running program in a loop
    while True:
        get_usrname(input("Please enter your usrname\n"))

        # admin override using magic hash
        if hashed_usrname  == "936867247aef14d232e539bd3f08b2c6bc47afe56a774ede3488d66006cbeb95":
            open_door()

        # compare usrname to creds.db TODO
        if hashed_usrname == "correct":
            print("turn LED on")
            # usrname_led.on()

        else:
            print("Incorrect user, try again")
            fuckups += 1
            flash_led(1)

        # compare passwd to creds.db TODO
            get_passwd(input("What is your passwrd?\n"))


        if hashed_passwd == "correct": 
            # passwd_led.on()
            open_door()

        if fuckups == 3:
            print("Too many incorrect attempts, pls wait 30s and try again")
            flash_led(30) 
            sleep(30)
        else:
           print("Incorrect user, try again")
           fuckups += 1
           flash_led(1)
            
        insert(hashed_usrname, hashed_passwd)
