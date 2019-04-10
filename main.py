import discord
import argparse

from market_item import MarketItem
from memeuser import MemeUser

parser = argparse.ArgumentParser(description='Discord bot to facilitate investing in posts.')
# required arguments
parser.add_argument('-t', '--token', help='your discord bot token', required=True)
parser.add_argument('-c', '--channel', help='the channel ID designated for investing', required=True)
# optional arguments
parser.add_argument('--init_balance', help='the balance that users start at initially', required=False, default=200)
parser.add_argument('--init_post', help='the balance that posts start at. Higher makes returns lower', required=False, default=1000)
parser.add_argument('-d', '--dev', help='enables some developer commands', required=False, default=False, action='store_true')

args = parser.parse_args()

TOKEN = args.token
channelID = args.channel

client = discord.Client()

# global values
userlist = []
initbalance = int(args.init_balance)
init_post_balance = int(args.init_post)
activeMarkets = []
memechannel = None

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------------')

    # Load some required information and cache in memory
    global memechannel
    global userlist
    memechannel = client.get_channel(channelID)
    print("Meme channel detected")
    potentialUsers = memechannel.server.members
    for m in potentialUsers:
        if m != client.user and await memeUserExists(m.id) is False:
            nu = MemeUser(m.id, initbalance)
            userlist.append(nu)
    print("{} users detected and processed".format(len(userlist)))
    print("User starting balance: ${}".format(initbalance))
    if args.dev is True:
        print("Starting Bot in DEVELOPER MODE")
    print("------------")

@client.event
async def on_member_join(member):
    nu = MemeUser(member.id, initbalance)
    userlist.append(nu)
    print("New User added and given ${} in starting money".format(initbalance))


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # If the message is a DM it will check these conditions
    if message.server is None:
        print(message.content)

        if message.content.lower().startswith('!help'):             # show the user the available commands
            await getHelp(message)
        elif message.content.lower().startswith('!balance'):        # show the user only their current balance
            await checkBalance(message)
        elif message.content.lower().startswith('!portfolio'):      # show the user what investments they have
            await showInvestments(message)
        elif message.content.lower().startswith('!default_investment'):
            await change_default_investment(message)
        elif message.content.lower().startswith('!sell'):
            await sell(message)
        elif message.content.lower().startswith('!my_id'):
            await client.send_message(message.channel, message.author.id)
        elif message.content.lower().startswith("!bankrupt"):
            await declare_bankruptcy(message)
        elif message.content.lower().startswith("!subtract"):
            await subtract(message)
    else:  # The message is NOT a DM it will count it for investing if it is in the correct channel
        # We add the up and downvote reactions and add the post to a list for counting
        if message.channel.id == channelID:
            await client.add_reaction(message, '👍')
            await client.add_reaction(message, '👎')

            mi = MarketItem(init_post_balance, message)
            activeMarkets.append(mi)


# This function is called when a reaction is added to a message
# Only applies to messages sent AFTER the bot joined the server
@client.event
async def on_reaction_add(reaction, user):
    # Ignore reactions in other channels and reactions made by the bot
    if reaction.message.channel.id != channelID or user == client.user:
        return

    if reaction.emoji == '👍':
        await createInvestment(reaction.message, user.id)
        # await client.send_message(reaction.message.channel, "invested, you have 👍")
    elif reaction.emoji == '👎':
        mi = await getMarketItem(reaction.message.id)
        mi.downvote()

async def subtract(message):
    if args.dev is True:
        user = await getUser(message.author.id)
        m = message.content.split(' ')
        user.balance -= int(m[1])



async def getHelp(message):
    msg = 'Hello {0.author.mention}, here are some things you can ask me: \n' \
          '\t`!help` - Displays this help dialog.\n' \
          '\t`!balance` - Get information about your current balance.\n' \
          '\t`!portfolio` - Get information about your current investment portfolio.\n' \
          '\t`!default_investment %INTEGER%` - Change your default investment value for new investments.\n' \
          '\t`!sell %INVESTMENT ID%` - Sell your investment for its current value.\n' \
          '\t`!sell all` - Sell all outstanding investments for their current value.\n' \
          '\t`!bankrupt` - Usable only when close to $0 to help you get back on your feet. Don\'t just say it, declare it. \n' \
          '**Instructions:**\n' \
          'To invest in memes simply react to them with 👍\n' \
          'When investing with 👍, you will always invest what your `default_investment` is set to.'.format(message)
    await client.send_message(message.channel, msg)


async def change_default_investment(message):
    m = message.content.split(' ')
    if len(m) != 2:
        await client.send_message(message.channel,
                                  "Please ensure there is only a single number argument after the command.")
        return None

    new_val = int(m[1])
    user = await getUser(message.author.id)
    user.default_invest = new_val
    await client.send_message(message.channel,
                              "Default Investment Value changed to `${}`".format(new_val))


async def checkBalance(message):
    userID = message.author.id
    for u in userlist:
        if u.ID == userID:
            msg = "Here is your balance information:\n" \
                  "`Balance: ${}`\n" \
                  "`Total Investments Outstanding: ${}`\n" \
                  "`Default investment amount: ${}`".format(u.balance, u.get_outstanding(), u.default_invest)
            await client.send_message(message.channel, msg)
            return


async def createInvestment(message, uid):
    mi = await getMarketItem(message.id)
    user = await getUser(uid)
    if user == None:
        print("User does not exist")
        print("this should probably not happen?")
        return
    else:
        ret = user.addInvestment(message.id, mi.value, mi)
        if ret is None:
            print("Investment not added, user insufficient funds")



async def showInvestments(message):
    uid = message.author.id
    user = await getUser(uid)
    msg = user.getInvestmentDisplay()
    if msg != None:
        await client.send_message(message.channel, msg)
    else:
        await client.send_message(message.channel, "You currently have `0` investments.")
    await client.send_message(message.channel, "You have declared bankruptcy {} times.".format(user.bankrupt_count))


async def sell(message):
    m = message.content.split(' ')
    user = await getUser(message.author.id)

    if len(m) != 2:
        await client.send_message(message.channel,
                                  "Please ensure there is only a single number argument after the command.")
        return None
    elif m[1] == 'all':
        income = user.sell_all()
    else:
        income = user.sell(int(m[1]))

    if income is None:
        await client.send_message(message.channel, "You do not have any investments with that ID.")
    else:
        await client.send_message(message.channel, "Income from sale: `${}`".format(income))

async def declare_bankruptcy(message):
    user = await getUser(message.author.id)
    # if the user has no outstanding investments and has less then a quarter of the starting value
    if user.get_outstanding() == 0 and user.balance < initbalance / 4:
        user.bankrupt(initbalance / 4)
        await client.send_message(message.channel, "You have sucessfully declared bankruptcy. You have been granted "
                                                   "an initial balance of ${}.".format(initbalance / 4))
    elif user.get_outstanding() != 0:
        await client.send_message(message.channel, "You cannot declare bankruptcy unless you have 0 investments.")
    else:
        await client.send_message(message.channel, "You have too much money to declare bankruptcy.")



async def memeUserExists(checkID):
    for u in userlist:
        if u.ID == checkID:
            return True
    return False


# TODO order userlist and use a better search method like quicksearch im just lazy. fine for small servers
async def getUser(uid):
    for u in userlist:
        if u.ID == uid:
            return u
    return None  # this shouldn't happen


async def getMarketItem(mid):
    for m in activeMarkets:
        if m.id == mid:
            return m
    return None


client.run(TOKEN)