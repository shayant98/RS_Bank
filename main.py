from flask import Flask,render_template,request,redirect,url_for,session
from flask_mysqldb import MySQL
import datetime
import os



app = Flask(__name__)
mysql = MySQL()
# MySQL configurations
app.config['MYSQL_HOST	'] = 'localhost'
app.config['MYSQL_PORT'] = 8888
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD	'] = 'root'
app.config['MYSQL_DB'] = 'bank'
mysql.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/validate', methods=['POST'])
def validate():
    username = str(request.form['username'])
    password = str(request.form['password'])

    try:
        cursor = mysql.connect.cursor()
        cursor.execute("SELECT * FROM users WHERE username ='" + username + "' AND password = '" + password + "'")
        user = cursor.fetchone()
        session['id'] = user[0]
        session['level'] = user[3]
        if user[3] == 1:
            return redirect(url_for('home'))
        elif user[3] == 2:
            return redirect(url_for('home2'))
        else:
            return "nope"
    except Exception as e:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('id', None)
   return redirect(url_for('index'))

@app.route('/home', methods=["GET", "POST"])
def home():
    if 'id' in session:
        if session['level'] == 1:
            return render_template('home.html',username=session['id'])
        else:
            return 'geen access'
    else:
        return 'nope'


@app.route('/countcoins', methods=["GET", "POST"])
def countcoins():

        _1cent = request.form['_01cent']
        _5cent = request.form['_05cent']
        _10cent = request.form['_10cent']
        _25cent = request.form['_025cent']
        _100cent = request.form['_100cent']
        _250cent = request.form['_250cent']

        tot1 = round(int(_1cent) * 0.01, 2);
        tot5 = round(int(_5cent) * 0.05, 2);
        tot10 = round(int(_10cent) * 0.10, 2);
        tot25 = round(int(_25cent) * 0.25, 2);
        tot100 = round(int(_100cent) * 1, 2);
        tot250 = round(int(_250cent) * 2.5, 2);

        tot = tot1 + tot5 + tot10 + tot25 + tot100 + tot250
        tot = str(round(tot, 2))

        try:
            ses_id = str(session['id'])
            cursor = mysql.connect.cursor()
            today = datetime.datetime.now().date()
            date = str(today)
            cursor.execute(
                "SELECT COUNT(*) from coin where date='" + date + "' AND user_id='" + ses_id + "'")
            result = cursor.fetchone()
            number_of_rows = result[0]

            if number_of_rows == 0:
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO coin (user_id, 1cent, 5cent, 10cent, 25cent, 100cent, 250cent,total, date)" 
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)",
                            (ses_id, _1cent, _5cent, _10cent, _25cent, _100cent,_250cent,tot, date))
                mysql.connection.commit()
                return render_template('home.html', tot1=tot1,tot5=tot5,tot10=tot10,tot25=tot25,
                                       tot100=tot100,tot250=tot250,tot=tot)
            else:
                cur = mysql.connection.cursor()
                cur.execute("""
                   UPDATE coin
                   SET 1cent=1cent+%s, 5cent=5cent+%s, 10cent=10cent+%s, 25cent=25cent+%s, 100cent=100cent+%s, 
                   250cent=250cent+%s,total=total+%s
                   WHERE user_id=%s AND date=%s""",
                            (_1cent, _5cent, _10cent, _25cent, _100cent, _250cent, tot, ses_id, date))
                mysql.connection.commit()
                return render_template('home.html',tot1=tot1,tot5=tot5,tot10=tot10,tot25=tot25,
                                       tot100=tot100,tot250=tot250,tot=tot)
        except Exception as e:
            return redirect('home')


@app.route('/clienten', methods=["GET", "POST"])
def clienten():```````````````````````````````````````````````````
    if 'id' in session:
        if session['level'] == 2:
            try:
                cursor = mysql.connect.cursor()
                cursor.execute("""SELECT clients.id, clients.name, clients.surname, accounts.acc_num, accounts.ammount
                               FROM clients
                               INNER JOIN accounts
                               ON clients.id = accounts.client_id
                               """)
                data = cursor.fetchall()
                return render_template('clienten.html', data=data)
            except Exception as e:
               return render_template('clienten.html', error = str(e))
        else:
            return 'geen access'
    else:
        return 'nope'

@app.route('/insertClient', methods=["GET", "POST"])
def insertclient():
    if request.method == 'POST':
        name = request.form['naam']
        surname = request.form['achternaam']
        accountnr = request.form['rekening']

        cursor = mysql.connect.cursor()
        cursor.execute("SELECT * FROM clients WHERE name ='" + name + "' AND surname ='" + surname + "'")
        account = cursor.fetchall()
        res_list = [x[0] for x in account]  # hoeveel rows er zijn
        if len(account) is 1:
            cur = mysql.connection.cursor()
            client_id = str(res_list).strip('[]')
            cursor.execute("SELECT COUNT(*) from accounts where client_id='" + client_id + "'")  # check als er 2 rekeningen bestaan
            result = cursor.fetchall()
            res_list = [x[0] for x in result]  # hoeveel rows er zijn
            if len(result) is 1:
                if str(res_list) == '[2]':
                    return redirect(url_for('clienten'))
                else:
                    cur.execute('''INSERT INTO accounts (client_id, acc_num) VALUES (%s, %s)''', (client_id, accountnr))
                    mysql.connection.commit()
                    return redirect(url_for('clienten'))
            else:
                cur.execute('''INSERT INTO accounts (client_id, acc_num) VALUES (%s, %s)''', (client_id, accountnr))
                mysql.connection.commit()
                return redirect(url_for('clienten'))
        #als de client niet voor komt
        elif len(account) is 0:
            cur = mysql.connection.cursor()
            cur.execute('''INSERT INTO clients (name, surname) VALUES (%s, %s)''', (name, surname))  #client opslaan in db
            mysql.connection.commit()
            client_id = cur.lastrowid  #client id pakken
            cur.execute('''INSERT INTO accounts (client_id, acc_num) VALUES (%s, %s)''', (client_id,accountnr))
            mysql.connection.commit()
            return redirect(url_for('clienten'))
    else:
        return render_template('clienten.html')


@app.route('/dagLog', methods=["GET", "POST"])
def daglog():
    if 'id' in session:
        if session['level'] == 2:
            try:
                today = datetime.datetime.now().date()
                date = str(today)
                cursor = mysql.connect.cursor()
                cursor2 = mysql.connect.cursor()
                cursor.execute("SELECT transactions.id, transactions.ammount, clients.name, clients.surname "
                               "FROM transactions INNER JOIN clients "
                               "ON transactions.client_id = clients.id "
                               "WHERE transactions.type = 0 + 1 AND transactions.date ='"+date+"'")
                cursor2.execute("SELECT transactions.id, transactions.ammount, clients.name, clients.surname "
                                "FROM transactions INNER JOIN clients "
                                "ON transactions.client_id = clients.id "
                                "WHERE transactions.type = '2' AND transactions.date ='"+date+"'")
                data = cursor.fetchall()
                data2 = cursor2.fetchall()
                return render_template('daglog.html', data=data,data2=data2)
            except Exception as e:
                return e
        else:
            return 'geen access'

    else:
        return 'nope'

@app.route('/home2', methods=["GET", "POST"])
def home2():
    if 'id' in session:
        if session['level'] == 2:
            try:
                today = datetime.datetime.now().date()
                date = str(today)
                cursor = mysql.connect.cursor()
                cursor.execute("SELECT coin.date, users.username, coin.1cent, coin.5cent, coin.10cent, coin.25cent, coin.100cent, coin.250cent, coin.total "
                               "FROM coin INNER JOIN users "
                               "ON coin.user_id = users.id "
                               "WHERE coin.date ='"+date+"'")

                data = cursor.fetchall()
                return render_template('home2.html', data=data)
            except Exception as e:
                return e
        else:
            return 'geen acces'
    else:
        return 'nope'

@app.route('/saldo', methods=["GET", "POST"])
def saldo():
    return render_template('saldo.html')


@app.route('/insertopname', methods=["GET", "POST"])
def insertopname():
    if 'id' in session:
        if session['level'] == 1:
            rekening = str(request.form['rekening'])
            bedrag = str(request.form['bedrag'])
            today = datetime.datetime.today()
            date = str(today)
            type = '2'

            try:

                cursor = mysql.connection.cursor()
                cursor.execute("SELECT COUNT(*) from accounts where acc_num='" + rekening + "'")
                result = cursor.fetchone()
                number_of_rows = result[0]
                if number_of_rows == 1:
                    cursor.execute("SELECT ammount,id,client_id FROM accounts WHERE acc_num ='" + rekening + "'")
                    data = cursor.fetchone()
                    calculation = data[0] - int(bedrag)

                    if calculation < 0:
                        return 'Nope'
                    else:
                        cur = mysql.connection.cursor()
                        cur.execute("""UPDATE accounts SET ammount=%s WHERE acc_num=%s""",
                                    (calculation, rekening))
                        mysql.connection.commit()
                        cur.execute('''INSERT INTO transactions (ammount, client_id, account_id, type, date) 
                           VALUES (%s, %s,%s,%s,%s)''',
                                    (bedrag, data[2], data[1], type, date))
                        mysql.connection.commit()
                        return render_template('saldo.html')
                else:
                    return 'rekening bestaat niet'
            except Exception as e:
                return e
        else:
            return 'geen acces'
    else:
        return 'nope'

@app.route('/insertstort', methods=["GET", "POST"])
def insertstort():
    if 'id' in session:
        if session['level'] == 1:
            rekening = str(request.form['rekening'])
            bedrag = str(request.form['bedrag'])
            today = datetime.datetime.today()
            date = str(today)
            type = '1'

            try:

                cursor = mysql.connection.cursor()
                cursor.execute("SELECT COUNT(*) from accounts where acc_num='" + rekening + "'")
                result = cursor.fetchone()
                number_of_rows = result[0]
                if number_of_rows == 1:
                    cursor.execute("SELECT ammount,id,client_id FROM accounts WHERE acc_num ='" + rekening + "'")
                    data = cursor.fetchone()
                    calculation = data[0] + int(bedrag)

                    if calculation < 0:
                        return 'Nope'
                    else:
                        cur = mysql.connection.cursor()
                        cur.execute("""UPDATE accounts SET ammount=%s WHERE acc_num=%s""",
                                    (calculation, rekening))
                        mysql.connection.commit()
                        cur.execute('''INSERT INTO transactions (ammount, client_id, account_id, type, date) 
                           VALUES (%s, %s,%s,%s,%s)''',
                                    (bedrag, data[2], data[1], type, date))
                        mysql.connection.commit()
                        return render_template('saldo.html')
                else:
                    return 'rekening bestaat niet'
            except Exception as e:
                return e
        else:
            return 'geen acces'
    else:
        return 'nope'

@app.route('/maandlog', methods=["GET", "POST"])
def maandlog():
    if 'id' in session:
        if session['level'] == 2:
            try:
                cursor = mysql.connection.cursor()
                cursor2 = mysql.connection.cursor()
                cursor.execute("""SELECT clients.name, clients.surname, accounts.acc_num, transactions.ammount, accounts.ammount, transactions.date
                 FROM transactions 
                INNER JOIN accounts ON transactions.account_id = accounts.id 
                INNER JOIN clients  ON transactions.client_id = clients.id
                WHERE transactions.type = 1 AND transactions.date BETWEEN (CURRENT_DATE() - INTERVAL 1 MONTH) AND CURRENT_DATE()
                ORDER BY transactions.date DESC """)
                cursor2.execute("""SELECT clients.name, clients.surname, accounts.acc_num, transactions.ammount, accounts.ammount, transactions.date
                         FROM transactions 
                        INNER JOIN accounts ON transactions.account_id = accounts.id 
                        INNER JOIN clients  ON transactions.client_id = clients.id
                        WHERE transactions.type = 2 AND transactions.date BETWEEN (CURRENT_DATE() - INTERVAL 1 MONTH) AND CURRENT_DATE()
                        ORDER BY transactions.date DESC """)
                data = cursor.fetchall()
                data2 = cursor2.fetchall()

                return render_template('maandlog.html', data = data, data2=data2)
            except Exception as e:
                return render_template('maandlog.html')
        else:
            return 'geen acces'
    else:
        return 'nope'

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True)
