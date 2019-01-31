from peewee import SqliteDatabase, Model, CharField, DateField, IntegerField


db = SqliteDatabase('currency1.db')

class Val(Model):
    Valuta = CharField()
    Srednji = CharField()
    Datum = DateField()

    class Meta:
        database = db

db.connect()

#db.create_tables([Val])