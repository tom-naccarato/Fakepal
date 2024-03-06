class InsufficientBalanceException(Exception):
    def __init__(self, message="Insufficient balance to complete the transaction"):
        self.message = message
        super().__init__(self.message)