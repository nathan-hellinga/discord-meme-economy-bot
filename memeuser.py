class MemeUser:

    def __init__(self, id, balance):
        self.balance = balance
        self.ID = id
        self.investments = []
        self.default_invest = 100



    def addInvestment(self, id, cur_value, marketItem, ammount=None):
        from investment import Investment

        if ammount is None:
            ammount = self.default_invest
        # Handle insufficient funds
        if self.balance <= 0:
            return None
        elif self.balance < ammount:
            ammount = self.balance

        self.balance -= ammount
        investmnt = Investment(ammount, int(id), cur_value + ammount, marketItem)
        self.investments.append(investmnt)

        marketItem.value += ammount
        # return True if an investment was successfully added
        return True


    def sell_all(self):
        income = 0
        for i in self.investments:
            income += self.sell(i.id)
        return income


    def sell(self, invst):
        # find the investment in the list by its ID
        for i in self.investments:
            if i.id == invst:
                invst = i
                break
            # if no investment is found with that ID
            return None
        # remove from investment list
        self.investments.remove(invst)
        # calculate earnings before cashing out
        income = invst.get_value()
        self.balance += income
        invst.cash_out()
        return income



    def set_defaults(self, invest):
        self.default_invest = invest

    def get_investment(self, iid):
        for i in self.investments:
            if i.id == iid:
                return i
        return None


    def getInvestmentDisplay(self):
        # compose lines
        result = []
        for i in self.investments:
            result.append("Post id: " + str(i.id))
            result.append("Initially invested: $" + str(i.value))
            val = i.get_value()  # current investment val calculated a share %
            result.append("current Value: $" + str(val))
            result.append("----------------------------------")

        # compose string
        output = ""
        for i in result:
            output += i
            output += '\n'

        # don't return an empty message
        if output != "":
            return output
        else:
            return None

    def get_outstanding(self):
        temp = 0
        for i in self.investments:
            temp += i.get_value()
        return temp
