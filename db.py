from app import app, db  # importa o app e o db do seu arquivo principal (app.py)

with app.app_context():
    db.create_all()
    print("Tabelas criadas com sucesso.")
