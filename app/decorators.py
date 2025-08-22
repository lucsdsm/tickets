from functools import wraps
from flask import abort, render_template, flash
from flask_login import current_user

def admin_required(f):
    """
    Restringe o acesso a uma rota apenas a usuários administradores.

    Verifica se o usuário atual está autenticado e se a sua propriedade `is_admin`
    é verdadeira. Se não for, interrompe o pedido e retorna um erro 403 (Proibido).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # verifica se o usuário está logado
        if not current_user.is_authenticated:
            flash('Acesso negado.', 'danger')
            return render_template('index.html', user=current_user) 
        
        # verifica se o usuário é um administrador
        if not current_user.is_admin:
            flash('Acesso negado.', 'danger')
            return render_template('index.html', user=current_user) 
        
        # se todas as verificações passarem, executa a rota original
        return f(*args, **kwargs)
    return decorated_function