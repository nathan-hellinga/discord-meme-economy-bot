class Investment:

    def __init__(self, value, marketID, current_value, marketItem):
        """
        Constructor
        :param value: the initial value invested
        :param marketID: the id
        :param current_value: the value the post is at at the time of investing
        :param marketItem: The market object
        """
        self.value = value
        self.id = marketID
        self.original_value = current_value
        self.marketItem = marketItem

    def get_value(self):
        return round((self.value / self.original_value) * self.marketItem.value * 100) / 100


    def cash_out(self):
        self.marketItem.downvote(self.get_value())
