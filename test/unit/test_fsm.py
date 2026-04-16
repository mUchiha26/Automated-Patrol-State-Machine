import unittest
from automated_patrol_state_machine.fsm.state_machine import StateMachine

class FakeNode:
    def get_logger(self):
        class L:
            def info(self, msg):
                print(msg)
        return L()

class TestFSM(unittest.TestCase):

    def test_initial_state(self):
        node = FakeNode()
        fsm = StateMachine(node)

        self.assertEqual(fsm.current_state.name, "PATROL")

if __name__ == "__main__":
    unittest.main()
