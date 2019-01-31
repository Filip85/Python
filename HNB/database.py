from peewee import SqliteDatabase, Model, CharField, DateField, IntegerField

db1=SqliteDatabase('currency2.db')

class User11(Model):
    id = IntegerField(unique=True)
    Name = CharField()
    Password = CharField()
    Mail = CharField()
    AlarmThreshold = IntegerField()

    class Meta:
        database = db1

class Currency2(Model):
    id = IntegerField()
    currency = CharField()

    class Meta:
        database = db1

db1.connect()


#db1.create_tables([Currency2])
