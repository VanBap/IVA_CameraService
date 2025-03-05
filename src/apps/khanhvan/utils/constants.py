
class MessageType:
    COMMAND = 1


class MessageAction:
    RESTART = 1
    DOWN = 2
    RESTART_LABEL = 'RESTART'
    DOWN_LABEL = 'DOWN'

    @staticmethod
    def get_action_label(action):
        if action == MessageAction.RESTART:
            return MessageAction.RESTART_LABEL
        elif action == MessageAction.DOWN:
            return MessageAction.DOWN_LABEL

        return None
