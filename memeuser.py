class MemeUser:

    def __init__(self, id, balance):
        self.balance = balance
        self.ID = id
        self.investments = []
        self.default_invest = 100
        self.bankrupt_count = 0

    def add_investment(self, id, cur_value, marketItem, amount=None):
        """
        Create an investment object or add value to an existing one
        :param id: The ID of the post to invest in
        :param cur_value: The current value of the post
        :param marketItem: The post object
        :param amount: The amount to invest in the post
        :return: The success of the action (boolean)
        """
        from investment import Investment

        if amount is None:
            amount = self.default_invest

        # Check if the user has enough to invest
        if self.balance <= 0:
            return None
        elif self.balance < amount:
            amount = self.balance

        self.balance -= amount
        investmnt = Investment(amount, int(id), cur_value + amount, marketItem)
        self.investments.append(investmnt)

        marketItem.value += amount
        # return True if an investment was successfully added
        return True

    def sell_all(self):
        income = 0
        for i in self.investments:
            income += self.sell(i.id)
        return income

    def bankrupt(self, new_bal):
        self.bankrupt_count += 1
        self.investments = []
        self.balance = new_bal

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

    def get_investment_display(self):
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
