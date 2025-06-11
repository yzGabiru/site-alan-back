from app import app, db, Premio, Resgate
with app.app_context():
    db.drop_all()
    db.create_all()
    # prêmios iniciais
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