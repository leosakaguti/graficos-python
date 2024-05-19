from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Vetor(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   nome_vetor = db.Column(db.String(100), unique=True)
   valores = db.relationship('ItemVetor', backref='vetor')

   def __init__(self, id=None, nome_vetor=None):
       self.id = id
       self.nome_vetor = nome_vetor

   def __repr__(self):
       return f'<Vetor {self.nome_vetor!r}>'

class ItemVetor(db.Model):
   id_numero = db.Column(db.Integer, primary_key = True)
   valor = db.Column(db.Integer, primary_key = False)
   seq_valor = db.Column(db.Integer, primary_key = False)
   id_vetor = db.Column(db.Integer, db.ForeignKey('vetor.id'))

   def __init__(self, id_vetor=None, id_numero=None, valor=None, seq_valor=None):
       self.id_numero = id_numero
       self.valor = valor
       self.seq_valor = seq_valor
       self.id_vetor = id_vetor

   def __repr__(self):
       return f'<Numero do Vetor {self.valor!r}>'