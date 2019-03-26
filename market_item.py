class MarketItem:

    def __init__(self, value, message):
        self.value = value
        self.id = message.id
        self.message = message

    def downvote(self, amount=100):
        self.value -= amount
