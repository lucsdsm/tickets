from flask_socketio import emit, join_room
from flask_login import current_user
from app import socketio, db
from models import TicketMessage

@socketio.on('join')
def handle_join(data):
    """Usuário entra em uma sala do ticket"""
    ticket_id = data['ticket_id']
    join_room(ticket_id)  # cada ticket tem sua sala

@socketio.on('send_message')
def handle_send_message(data):
    """Quando um usuário envia uma mensagem"""
    ticket_id = data['ticket_id']
    message = data['message']

    # salvar no banco
    new_message = TicketMessage(
        ticket_id=ticket_id,
        message=message,
        author_id=current_user.id
    )
    db.session.add(new_message)
    db.session.commit()

    # enviar a todos na mesma sala
    emit('new_message', {
        'author': current_user.first_name,
        'message': message,
        'created_at': new_message.created_at.isoformat()
    }, room=ticket_id)
