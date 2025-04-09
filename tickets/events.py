class Event:
    name = None
    topic = "Tickets"

    def __init__(self, data):
        self.data = data
        # key is used as message key
        self.key = data["id"]

    def __str__(self):
        return f"{self.name}: {self.data}"
    


class TicketCreated(Event):
    name = "TicketCreated"


class TicketAssigned(Event):
    name = "TicketAssigned"


class TicketClosed(Event):
    name = "TicketClosed"


class FollowUpCreated(Event):
    name = "TicketFollowUpCreated"

    def __init__(self, data):
        super().__init__(data)
        self.key = str(data["ticket"])


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
