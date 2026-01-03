from .models import Ticket

def is_ticket_open(ticket):
    return ticket.status == Ticket.Status.OPEN

def is_ticket_closed(ticket):
    return ticket.status == Ticket.Status.CLOSED

def is_ticket_pending(ticket):
    return ticket.status == Ticket.Status.PENDING
