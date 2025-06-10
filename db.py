from app import app, db, Premio

with app.app_context():
    # DESTRÓI todas as tabelas
    db.drop_all()
    # CRIA novamente as tabelas já com o campo pontos
    db.create_all()

    # Popula prêmios iniciais (se quiser)
    if Premio.query.count() == 0:
        prêmios = [
            Premio(nome='Cesta Básica',   custo=80),
            Premio(nome='Desconto R$10',  custo=50),
            Premio(nome='Produto Grátis', custo=120),
        ]
        db.session.add_all(prêmios)
        db.session.commit()
        print("Prêmios iniciais inseridos.")

    print("Tabelas criadas com sucesso.")