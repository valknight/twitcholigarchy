from enum import Enum
import json
import datetime
from data import store


class PollTypes(Enum):
    POLL = "POLL"
    POINT_REDEEM = "POINT_REDEEM"
    PREDICTION = "PREDICTION"


class Poll:
    def __init__(self, name: str, blueteam: str, pinkTeam: str, doRefund: bool = True, pollType: PollTypes = PollTypes.PREDICTION) -> None:
        self.name = name
        self.expiration = 30
        self.blueteamName = blueteam
        self.blueteamVotes = 0
        self.pinkTeamName = pinkTeam
        self.pinkTeamVotes = 0
        self.doRefund = doRefund
        self.isOpen = True
        self.type = pollType
        self.closedAt = None
        self.write()

    def __dict__(self) -> dict:
        return {
            'name': self.name,
            'blueteam': {
                'name': self.blueteamName,
                'votes': self.blueteamVotes
            },
            'pinkTeam': {
                'name': self.pinkTeamName,
                'votes': self.pinkTeamVotes
            },
            'doRefund': self.doRefund,
            'isOpen': self.isOpen,
            'closedAt': self.closedAt,
            'type': str(self.type)
        }

    def write(self) -> bool:
        return store.set('poll', json.dumps(self.__dict__()))

    def setVotesPoll(self, choices: list) -> bool:
        for i in choices:
            if i['title'] == self.blueteamName:
                self.blueteamVotes = i['votes']
            if i['title'] == self.pinkTeamName:
                self.pinkTeamVotes = i['votes']
        self.write()
        return True

    def setVotesPrediction(self, outcomes: list) -> bool:
        for i in outcomes:
            if i['title'] == self.blueteamName:
                self.blueteamVotes = i['channel_points']
            if i['title'] == self.pinkTeamName:
                self.pinkTeamVotes = i['channel_points']
        self.write()
        return True

    def close(self) -> bool:
        ogCloseStatus = self.isOpen
        self.isOpen = False
        self.closedAt = datetime.datetime.utcnow().timestamp()
        self.write()
        return ogCloseStatus

    def canRefund(self) -> bool:
        # Cannot refund if not closed
        return self.isOpen and self.doRefund
