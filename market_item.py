class MarketItem:

    def __init__(self, value, message):
        self.value = value
        self.id = message.id
        self.message = message

    def downvote(self, amount=100):
        self.value -= amount
        if self.value < 0:
            self.value = 0

    def remove_downvote(self, amount=100):
        self.value += amount
