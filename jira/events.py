class Event:
    name = None
    topic = "Users"

    def __init__(self, data):
        self.data = data
        # key is used as message key
        self.key = str(self.get_key())

    def get_key(self):
        return self.data["id"]

    def __str__(self):
        return f"{self.name}: {self.data}"


class UserCreated(Event):
    name = "UserCreated"


class UserUpdated(Event):
    name = "UserUpdated"


class UserDeleted(Event):
    name = "UserDeleted"


class TicketCreated(Event):
    topic = "Tickets"
    name = "TicketCreated"


class TicketUpdated(Event):
    name = "TicketUpdated"


class TicketDeleted(Event):
    name = "TicketDeleted"


class JiraTicketCreated(Event):
    name = "JiraTicketCreated"


class JiraTicketUpdated(Event):
    name = "JiraTicketUpdated"


class JiraTicketDeleted(Event):
    name = "JiraTicketDeleted"


class JiraTicketCommentCreated(Event):
    name = "JiraTicketCommentCreated"
