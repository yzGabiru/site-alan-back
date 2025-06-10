from app import app, db, Premio
with app.app_context():
    db.create_all()
    if Premio.query.count()==0:
        db.session.add_all([
            Premio(nome='Cesta Básica', custo=80),
            Premio(nome='Desconto R$10', custo=50),
            Premio(nome='Produto Grátis', custo=120),
        ])
        db.session.commit()
    print("Tabelas criadas e prêmios inseridos.")