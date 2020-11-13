import queue


HELP_MESSAGE = """--------**Rolbert**--------

Rollbert is a PnP bot that can manage attributes and uses them to make the roll process more easy. The goal of this bot ist to have minimal input requirements regarding the dicerolls.
It is currently in development and is therefore subject to change in the future. The basic features are, however, mostly fleshed out.
Restrictions are that names cant contain whitespaces. This is necessary to ensure a simple and easy to type syntax when dicerolling. If you must - you can use '_' and '-' symbols to save multiple words.

**Command list**
prefix:                                     display the current prefix for this server
/prefix <string>                            set the prefix for this server
/register <string>                          register a new character for your user
/delete <string>                            delete a character with given name from your user
/selected                                   displays the selected character name
/select <string>                            selects a character
/chars                                      list all your characters
/char <string> -optional-                   show the attributes from your selected or given character
/update <string1> <int1> <string2> <int2>   create or update a attribute. Multiple attributes can be created simultaneously
/update attribute(dep1,dep2,dep3) <int>     creates an attribute with dependencies. Can be used in a normal update call
/remove <string>                            removes an attribute from your selected character
/roll <roll string>                         rolls dice. supported operations are
                                            +,-,*, ()
                                            to throw a b sided dice a times use <a>w<b>
/rd <string>                                rolls the dice in DSA ruleset for an attribute that has dependencies for selected char
/rd <attr1> <attr2> <attr3> <attr4>         rolls attr4 for stats attr1-3 in DSA ruleset for selected char

/help                                       displays this message


"""


terminate = False

MAX_ATTRIBUTE_COUNT = 100
MAX_CHAR_COUNT = 10

send_queue = queue.Queue() 
bot_receive_queue = queue.Queue()
stats = ["mu","kl","in","ch","ff","ge", "ko", "kk"]

prefix = '/'

def send_bot_receive_queue(msg):
    bot_receive_queue.put((msg))

def send_message(channel, content):
    send_queue.put((channel, content))

