import click
from flask.cli import with_appcontext
from . import db
from .models import User
from .models import Sector
from .models import Subject

@click.command(name='create-admin')
@with_appcontext
def create_admin() -> None:
    """Cria um usuário admin com credenciais padrão."""
    
    # verifica se o admin já existe
    if User.query.filter_by(username='admin').first():
        print("Usuário 'admin' já existe.")
        return
        
    # cria o novo usuário admin
    admin_user = User(
        username='admin',
        first_name='Admin',
        last_name='Master',
        password_hash='admin',
        email='admin@tickets.com',
        admin=True
    )
    
    # define a senha usando o método set_password
    admin_user.set_password('admin')
    
    # salva o usuário no banco de dados
    db.session.add(admin_user)
    db.session.commit()
    
    print("usuário 'admin' criado com sucesso.")

@click.command(name='seed-subjects')
@with_appcontext
def seed_subjects() -> None:
    """Cria uma lista de subjects iniciais se eles não existirem."""
    
    # Lista de setores e os seus respetivos subjects
    initial_data = {
        "TI": [
            "Problemas com Login/Senha",
            "Computador Lento ou a Travar",
            "Pedido de Instalação de Software",
            "Problema com Impressora",
            "Falha de Rede ou Internet",
            "Criação de Email para Novo Colaborador"
        ],
        "Financeiro": [
            "Dúvida sobre Folha de Pagamento",
            "Pedido de Reembolso de Despesas",
            "Problema com Fatura de Fornecedor",
            "Acesso ao Sistema Financeiro",
            "Solicitação de Relatório de Custos"
        ],
        "Diretoria": [
            "Preparação de Relatório Estratégico",
            "Agendamento de Reunião Confidencial",
            "Problema com Equipamento de Videoconferência",
            "Pedido de Acesso a Dashboards de Gestão"
        ],
        "Compras": [
            "Criação de Novo Pedido de Compra",
            "Aprovação de Orçamento",
            "Cadastro de Novo Fornecedor",
            "Dúvida sobre Contrato com Fornecedor"
        ],
        "RH": [
            "Dúvida sobre Férias ou Ausências",
            "Alteração de Dados Cadastrais",
            "Pedido de Declaração de Vínculo",
            "Informações sobre Benefícios (Plano de Saúde, etc.)",
            "Questões sobre Ponto Eletrónico"
        ],
        "Marketing": [
            "Pedido de Criação de Arte Gráfica",
            "Aprovação de Conteúdo para Redes Sociais",
            "Problema de Acesso a Ferramentas de Marketing",
            "Relatório de Performance de Campanhas"
        ],
        "Jurídico": [
            "Análise de Contrato ou Documento Legal",
            "Dúvida sobre LGPD (Lei Geral de Proteção de Dados)",
            "Pedido de Documento Societário",
            "Consulta sobre Processo Jurídico"
        ],
        "Operações e Logística": [
            "Problema no Controlo de Stock",
            "Avaria em Equipamento de Armazém",
            "Rastreamento de Entrega de Mercadoria",
            "Pedido de Material de Expedição"
        ],
        "Vendas": [
            "Problema com o Sistema de CRM",
            "Pedido de Aprovação de Desconto para Cliente",
            "Atualização de Pipeline de Vendas",
            "Dúvida sobre Cálculo de Comissão"
        ],
        "Manutenção e Instalações": [
            "Abertura de Ordem de Serviço (Reparo)",
            "Pedido de Manutenção Preventiva (Ar Condicionado, etc.)",
            "Relato de Problema Predial (Infiltração, Elétrico)",
            "Solicitação de Reparo de Mobiliário"
        ]
    }
    
    print("A verificar e a criar dados iniciais...")
    
    # cria os setores
    for sector_name in initial_data.keys():
        if not Sector.query.filter_by(name=sector_name).first():
            new_sector = Sector(name=sector_name)
            db.session.add(new_sector)
            print(f'A criar setor: "{sector_name}"')
    # guarda os novos setores na base de dados antes de continuar
    db.session.commit()

    # criar os assuntos e os associa aos setores
    for sector_name, subject_names in initial_data.items():
        # encontra o setor que acabou de criar/verificar
        sector = Sector.query.filter_by(name=sector_name).first()
        if not sector:
            continue

        for subject_name in subject_names:
            # verifica se o assunto já existe
            subject = Subject.query.filter_by(name=subject_name).first()
            
            # se não existir, cria-o
            if not subject:
                subject = Subject(name=subject_name)
                db.session.add(subject)
                print(f'A criar assunto: "{subject_name}"')
            
            # associa o assunto ao setor, se a associação ainda não existir
            if sector not in subject.sectors:
                subject.sectors.append(sector)
                print(f'A ligar "{subject_name}" ao setor "{sector_name}"')

    # Guarda todas as novas criações e associações na base de dados
    db.session.commit()
    print("Povoamento da base de dados concluído com sucesso.")
