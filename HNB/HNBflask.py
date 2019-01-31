

from flask import Flask
import json;
import urllib.request;
from database import User11, Currency2
from flask_restplus import Api, Resource, fields
from peewee1 import Val
from peewee import fn
import smtplib

app = Flask(__name__)
api = Api(app)

a_user = api.model('User', {'id' : fields.Integer, 'name' : fields.String, 'password' : fields.String, 'mail' : fields.String, 'alarmThreshold' : fields.Integer})
#a_currency = api.model('User', {'Valuta' : fields.String(), 'vrijednost_valute' : fields.String(), 'datum' : fields.String()})
a_users_currencies = api.model('Currency', {'id' : fields.Integer(), 'valuta' : fields.String()})

data = []
url = 'http://api.hnb.hr/tecajn/v1'
json_object = urllib.request.urlopen(url)

data = json.load(json_object)


#za slanje maila
email = ''


for i in range(14):
    Val(Valuta=data[i]["Valuta"], Srednji=data[i]["Srednji za devize"], Datum=data[i]["Datum primjene"]).save()


users = []

@api.route('/home')
class TodaysCurrencyList(Resource):
    def get(self):

        todays_value = Val.select(Val.Valuta, Val.Srednji, Val.Datum).where(Val.Datum == (Val.select(fn.MAX(Val.Datum)))).distinct()


        output = []

        for v in todays_value:

            user_data = {}
            user_data['Valuta'] = v.Valuta
            user_data['Srednji'] = v.Srednji
            user_data['Datum'] = v.Datum
            output.append(user_data)

        print(output)

        return {'todays_currencies_list' : output}, 200

#kreiranje prifla
@api.route('/home/createProfil')
class CreateUser(Resource):

    @api.marshal_with(a_user)
    def get(self):
        return users, 200

    @api.expect(a_user)
    def post(self):
        new_user = api.payload
        users.append(new_user)

        User11.insert(id=new_user['id'], Name=new_user['name'], Password=new_user['password'], Mail=new_user['mail'], AlarmThreshold=new_user['alarmThreshold']).execute()

        return {'result' : 'User added'}, 201

#prikaz svih usera
@api.route('/home/users')
class GetAllUsers(Resource):

    @api.marshal_with(a_user)
    def get(self):

        output = []

        for us in User11:
            user_data = {}
            user_data['id'] = us.id
            user_data['name'] = us.Name
            user_data['password'] = us.Password
            user_data['mail'] = us.Mail
            user_data['alarmThreshold'] = us.AlarmThreshold
            output.append(user_data)

        return output, 200

#prikaz usera prema id
@api.route('/home/user/<id>')
class GetOneUser(Resource):

    @api.marshal_with(a_user)
    def get(self, id):
        temp = User11.select().where(User11.id == id).first()
        user_data = {}
        user_data['id'] = temp.id
        user_data['name'] = temp.Name
        user_data['password'] = temp.Password
        user_data['mail'] = temp.Mail
        user_data['alarmThreshold'] = temp.AlarmThreshold

        return user_data, 200

#prikaz valuta za pojedinog usera
@api.route('/home/user/<id>/users_currencies')
class GetUsersCurrencies(Resource):

    def get(self, id):
        output = []

        temp = Currency2.select(Currency2.currency).where(Currency2.id == id)

        curr = []
        for i in temp:
            curr = Val.select(Val.Valuta, Val.Srednji, Val.Datum).where(Val.Valuta == i.currency).distinct()
            for c in curr:
                user_data = {}
                user_data['Valuta'] = c.Valuta
                user_data['vrijednost_valute'] = c.Srednji
                user_data['datum'] = c.Datum
                output.append(user_data)

        for v in curr:
            print('{} {} {}'.format(v.Valuta, v.Srednji, v.Datum))

        print(output)
        return output, 200

    @api.expect(a_users_currencies)
    def post(self, id):
        users = []
        new_user = api.payload
        users.append(new_user)

        Currency2.insert(id=id, currency=new_user['valuta']).execute()

        return {'currency': 'Currencies added'}, 201

#slanje maila
@api.route('/home/user/<id>/mail')
class SendMail(Resource):
    message = []

    def get(self, id):
        todaysValue1 = []
        msg = []

        temp = Currency2.select(Currency2.currency).where(Currency2.id == id)
        alarm = User11.select(Currency2.AlarmThreshold).where(Currency2.id == id)

        curr = []
        for i in temp:
            todays_value = Val.select(Val.Valuta, Val.Srednji).where((Val.Valuta == i.currency) & (Val.Datum == (Val.select(fn.MAX(Val.Datum))))).distinct()
            yesterdays_value = Val.select(Val.Valuta, Val.Srednji).where((Val.Valuta == i.currency) & (Val.Datum == (Val.select(fn.MAX(Val.Datum))).where(Val.Datum < (Val.select(fn.MAX(Val.Datum)))))).distinct()
            for c in todays_value:
                todays_value1 = float(c.Srednji.replace(",", "."))
                curr = c.Valuta
            for c1 in yesterdays_value:
                yesterdays_value1 = float(c1.Srednji.replace(",", "."))
                change = todays_value1 / yesterdays_value1
                m = User11.select(User11.Mail).where(User11.id == id)
                for i in m:
                    email = i.Mail
                if(change < alarm and change > alarm):
                    msg.append(str(curr) + " se promjenila za " + alarm)
                else:
                    msg.append(str(curr) + "se nije promjenila.")

            message = msg

            server = smtplib.SMTP('smtp.gmail.com:587')

            server.ehlo()

            server.starttls()

            server.login("johndoe420420420042@gmail.com", "H123456789H")

            server.sendmail("johndoe420420420042@gmail.com", str(email), str(message))

            server.quit()

        return {'mail' : 'mail sent'}, 200



#updatanje userove šifre
@api.route('/home/user/<id>/<password>')
class UpdatePassword(Resource):

    def put(self, id, password):

        User11.update(Password = int(password)).where(User11.id == id).execute()

        return {'password' : 'Password updated'}, 405


#updatanje korisnikovih valuta
@api.route('/home/user/<id>/delete/<delete_currency>')
class UpdateCurrencies(Resource):

    def delete(self, id, delete_currency):

        #Currency2.update(currency=new_currency).where(Currency2.id == id).execute()

        Currency2.delete().where((Currency2.currency == delete_currency) & (Currency2.id == id)).execute()

        return {'currency': 'Currenciy deleted'}, 405



if __name__ == '__main__':
    app.run(debug=True)
