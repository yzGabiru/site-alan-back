from app import app, db, Premio

with app.app_context():
    # cria todas as tabelas que não existirem
    db.create_all()

    # popula os prêmios apenas se ainda não tiver nenhum
    if Premio.query.count() == 0:
        prêmios = [
            Premio(nome='Cesta Básica',   custo=80),
            Premio(nome='Desconto R$10',  custo=50),
            Premio(nome='Produto Grátis', custo=120),
        ]
        db.session.add_all(prêmios)
        db.session.commit()
        print("Prêmios iniciais inseridos.")
    else:
        print("Prêmios já existem no banco.")

    print("Tabelas criadas com sucesso.")