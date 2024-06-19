class Revolutions:
    def __init__(self):
        self.revs = 0

    def get_revolutions(self, child_pipe):
        # doe dingen
        child_pipe.send(self.revs)
        pass

