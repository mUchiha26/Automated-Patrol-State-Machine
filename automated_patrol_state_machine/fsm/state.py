# Base class for all states
# Every state must follow this structure

class State:
    def __init__(self, name):
        self.name = name

    def enter(self, context):
        """Called when state starts"""
        pass

    def execute(self, context):
        """Main logic of the state"""
        pass

    def exit(self, context):
        """Called when leaving state"""
        pass
