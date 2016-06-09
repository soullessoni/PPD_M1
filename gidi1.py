# -*- coding: utf-8 -*-
"""
"""

import psycopg2
from switch import Switch
import re
import sys
import pprint

from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

#File with disease's name
fmaladie_name = "maladies_bovines.txt"

adresseIPLocalhost = ['localhost', '127.0.0.1']

def connect():
    return psycopg2.connect("dbname='"+ session['db_name'] +
                            "' user='"+ session['user'] +
                            "' host='" + session['host'] +
                            "' password='" + session['password'] + "'")

def drop_index_local():
        conn = connect()
        cur1 = conn.cursor()
        cur2 = conn.cursor()
        cur1.execute(
            'SELECT table_name '
            'FROM INFORMATION_SCHEMA.TABLES '
            'WHERE table_name LIKE \'farm%\';'
        )
        tables = cur1.fetchall()
        #Please a good RegEx
        for table in tables:
            is_farm = re.compile('\\bfarm[0-9]+\\b', re.IGNORECASE)
            if (is_farm.match(table[0]) != None):
                print table[0]
            else:
                cur2.execute(
                    'drop table "' + table[0] + '";'
                    )
        conn.commit()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/db_disconnect')
def db_disconnect():
    session.clear()
    return redirect(url_for('home'))

@app.route('/db_connect/', methods=['GET', 'POST'])
def db_connect():
    if not session.get('connexion'):
        if request.method == 'POST':
            db_name = request.form['db_name']
            usr = request.form['usr']
            psw = request.form['psw']
            #Localhost is default
            if request.form['host'] == "":
                host = "localhost"
            else:
                host = request.form['host']

            try:
                conn = psycopg2.connect("dbname='"+db_name+"' user='"+usr+"' host='"+host+"' password='"+psw+"'")
                conn.close()

            except:
                return redirect(url_for('error'))

            #set session data
            session['db_name'] = db_name
            session['user'] = usr
            session['password'] = psw
            session['host'] = host
            session['connexion'] = True
            return redirect(url_for('home'))

    else:
        return redirect(url_for('db_action'))

    return render_template("db_connect.html")

@app.route('/db_action', methods=['GET', 'POST'])
def db_action():
    if session.get('connexion'):
        if request.method == 'POST':
            with Switch(request.form['action']) as case:
                if case("top_K"):
                    return redirect(url_for("top_k"))
                if case("threshold"):
                    return redirect(url_for("threshold"))
                if case("index_local"):
                    return redirect(url_for("index_local"))
                if case("index_global"):
                    return redirect(url_for("index_global"))
                if case("db_link"):
                    return redirect(url_for("db_link"))
                if case.default:
                    return redirect(url_for('error'))
        else:
            return render_template('home.html')
    else:
        return redirect(url_for('error'))

@app.route('/index/local')
def index_local():
    if session.get('connexion'):
        drop_index_local()
        conn = connect()
        cur1 = conn.cursor()
        cur2 = conn.cursor()

        print fmaladie_name
        with open(fmaladie_name) as f:
            maladies = (f.readlines())

        cur1.execute(
            'SELECT table_name '
            'FROM INFORMATION_SCHEMA.TABLES '
            'WHERE table_name LIKE \'farm%\';'
        )
        tables = cur1.fetchall()
        for table in tables:
            for maladie in maladies:
                cur2.execute(
                    'CREATE TABLE "' + table[0] + '_' + str(maladie).rstrip() + '" '
                    '(id INTEGER PRIMARY KEY, proba NUMERIC(10,8)); '
                    'INSERT INTO "' + table[0] + '_' + str(maladie).rstrip() + '" '
                    'SELECT id, proba '
                    'FROM "' + table[0] + '" '
                    'WHERE "maladie" '"= '" + (str(maladie).rstrip()) + "' "';'

                    'CREATE TABLE "test" (LIKE "' + table[0] + '_' + str(maladie).rstrip() + '"); '
                    'INSERT INTO "test" '
                    'SELECT * FROM "' + table[0] + '_' + str(maladie).rstrip() + '" ORDER BY proba DESC; '
                    'DROP TABLE "' + table[0] + '_' + str(maladie).rstrip() + '"; '
                    'ALTER TABLE "test" RENAME TO "' + table[0] + '_' + str(maladie).rstrip() + '";'
                )
        conn.commit()
        return render_template('index_local_confirm.html', active="index_local")
    else:
        return redirect(url_for('error'))

@app.route('/index_global', methods=['GET', 'POST'])
def index_global():
    if session.get('connexion'):
        if request.method == 'POST':
            conn = connect()
            cur1 = conn.cursor()
            cur2 = conn.cursor()
            cur3 = conn.cursor()
            cur4 = conn.cursor()
            cur1.execute(
                "DROP TABLE IF EXISTS index_global;"
                "CREATE TABLE index_global(adress CHAR(100), proba NUMERIC(10,8));"
            )
            sick = request.form['maladie']
            doOrNo = request.form['choice']
            print sick
            cur2.execute(
                #creation de table_path et la remplir
                'DROP TABLE IF EXISTS table_path;'
                'CREATE TABLE table_path(adress CHAR(100));'
                'insert into table_path (adress)'
                'SELECT table_name FROM INFORMATION_SCHEMA.TABLES WHERE table_name LIKE \'%_' + sick + '\';'
                """DROP TABLE IF EXISTS table_path_ip;
                    CREATE TABLE table_path_ip(adress CHAR(100));"""
            )

            print '++++++++++++++++++++++++++'
            cur2.execute(
                """SELECT adress FROM table_path"""
            )
            listeFarms = cur2.fetchall()
            for farm in listeFarms:
                print farm[0]
                ipName = session['host'] + '-' + farm[0]
                print ipName
                cur2.execute(
                    """
                    INSERT INTO table_path_ip(adress) VALUES('""" + ipName + """')"""
                )
            print '++++++++++++++++++++++++++'

            cur3.execute(
                #pour remplir la listeTablesSick en bas
                'SELECT adress FROM table_path;'
            )
            listeTablesSick = cur3.fetchall()
            print listeTablesSick
            for liste in listeTablesSick:
                print '-----------------------'
                print liste[0]
                cur3.execute(
                    #remplir l'index global
                    """INSERT INTO index_global(adress, proba)
                    SELECT table_path_ip.adress, """+ liste[0].rstrip() +""".proba FROM table_path_ip, """+ liste[0].rstrip() +""" LIMIT 1;
                    DELETE FROM table_path WHERE ctid IN (SELECT ctid FROM table_path LIMIT 1);
                    DELETE FROM table_path_ip WHERE ctid IN (SELECT ctid FROM table_path_ip LIMIT 1)"""
                )
            print 'en haut pas touche'
            test = 'toto3'
            cur4.execute(
                # mettre en ordre l'index global
                """CREATE TABLE test (LIKE index_global);
                    INSERT INTO test
                    SELECT * FROM index_global ORDER BY proba DESC;
                    DROP TABLE index_global;
                    ALTER TABLE test RENAME TO index_global;
                """
                #Suppression de table_path et table_path_ip
                """
                DROP TABLE IF EXISTS table_path;
                DROP TABLE IF EXISTS table_path_ip;
                """
            )
            print doOrNo + '==========================================='
            if (doOrNo == '1'):
                # dblinK
                cur4.execute(
                    """
                        SELECT dblink_connect('toto6', 'hostaddr=192.168.43.143 port=5432 dbname=PPD user=postgres password=root');
                        INSERT INTO index_global
                        SELECT * FROM dblink('toto6','SELECT * FROM index_global') AS t(a text ,c numeric );
                        CREATE TABLE test (LIKE index_global);
                        INSERT INTO test
                        SELECT * FROM index_global ORDER BY proba DESC;
                        DROP TABLE index_global;
                        ALTER TABLE test RENAME TO index_global;
                        SELECT dblink_disconnect('toto6');
                      """
                )
            else:
                print 'bip bip chui pas rentré'
            print 'okkkkkkkkkkkkkkk'
            conn.commit()
            return render_template('index_global_confirm.html', active="index_global")
        return render_template('index_global.html', active="index_global")
    else:
        return redirect(url_for('error'))

@app.route('/top_k', methods=['GET', 'POST'])
def top_k():
    if session.get('connexion'):
        if request.method == 'POST':
            conn = connect()
            cur1 = conn.cursor()
            cur1.execute(
                """SELECT * FROM index_global order by proba desc;"""
            )
            listeTuples = cur1.fetchall()   #on récupère l'index_global dans une liste
            top_k = request.form['nb_max']
            ProbaSeuil = []
            for tuple in listeTuples:    #pour chaque tuple de l'index_global, on extraie l'adresseIP et la farm_n grâce au champ "address" du tuple
                nomTuple = tuple[0].rstrip().split("-",1)
                adresseIP = nomTuple[0]
                farm_n = nomTuple[1]
                if adresseIP in adresseIPLocalhost:
                    cur1.execute(
                        """
                        SELECT dblink_connect('"""+adresseIP+"""', 'host="""+adresseIP+""" port=5432 dbname=PPD1 user=postgres password=root');
                        SELECT * FROM dblink('"""+adresseIP+"""', 'SELECT * FROM """+farm_n+""" order by proba desc LIMIT 1 OFFSET """+top_k+"""') AS tuple(id integer, p numeric);
                        """
                    )
                else:
                    cur1.execute(
                        """
                        SELECT dblink_connect('"""+adresseIP+"""', 'hostaddr="""+adresseIP+""" port=5432 dbname=PPD1 user=postgres password=root');
                        SELECT * FROM dblink('"""+adresseIP+"""', 'SELECT * FROM """+farm_n+""" order by proba desc LIMIT 1 OFFSET """+top_k+"""') AS tuple(id integer, p numeric);
                        """
                    )
                ProbaTemp = cur1.fetchone() #on récupère la kième probabilité de la farm correspondant au tuple
                if not ProbaSeuil:  #on stocke la kième proba et on détermine si elle va devenir la proba "seuil"
                    ProbaSeuil = ProbaTemp
                elif(ProbaTemp[1] >= ProbaSeuil[1]):
                    ProbaSeuil = ProbaTemp
                cur1.execute(
                    """
                    SELECT dblink_disconnect('"""+adresseIP+"""');
                    """
                )
            ProbaK = str(ProbaSeuil[1])
            topKProbas = []
            for tuple in listeTuples:       #pour chaque tuple de l'index_global on vérifie si la proba affectée à ce tuple (tuple[1]) est >= la proba "seuil"
                if (tuple[1]>= ProbaSeuil[1]) :
                    nomTuple = tuple[0].rstrip().split("-",1)
                    adresseIP = nomTuple[0]
                    farm_n = nomTuple[1]
                    if adresseIP in adresseIPLocalhost:
                        cur1.execute(
                            """
                            SELECT dblink_connect('"""+adresseIP+"""', 'host="""+adresseIP+""" port=5432 dbname=PPD1 user=postgres password=root');
                            SELECT * FROM dblink('"""+adresseIP+"""', 'SELECT * FROM """+farm_n+""" where proba >= """+ProbaK+""" order by proba desc;') AS tuple(id integer, p numeric);
                            """
                        )
                    else:
                         cur1.execute(
                            """
                            SELECT dblink_connect('"""+adresseIP+"""', 'hostaddr="""+adresseIP+""" port=5432 dbname=PPD1 user=postgres password=root');
                            SELECT * FROM dblink('"""+adresseIP+"""', 'SELECT * FROM """+farm_n+""" where >= """+ProbaK+""" order by proba desc;') AS tuple(id integer, p numeric);
                            """
                        )
                    Probas = cur1.fetchall()
                    for proba in Probas:
                        #probaT = list(proba)
                        #probaT[0] = tuple[0]
                        #topKProbas.extend(probaT)
                        test = [proba[1],adresseIP, farm_n]
                        topKProbas.append(test)
                    cur1.execute(
                        """
                        SELECT dblink_disconnect('"""+adresseIP+"""');
                        """
                    )
            topKProbas = sorted(topKProbas, key = lambda tup : tup[0], reverse=True)
            nbTotalTuples = len(topKProbas)
            top_k = int(top_k)
            nbTotalTuples = nbTotalTuples - (nbTotalTuples - top_k)
            topKProbas = topKProbas[:nbTotalTuples]
            conn.commit()
            return render_template("top_k_result.html", active="top_k", res=topKProbas)
        else:
            return render_template("top_k.html", active="top_k")
    else:
        return redirect(url_for('error'))

@app.route('/threshold', methods=['GET', 'POST'])
def threshold():
    if session.get('connexion'):
        if request.method == 'POST':
            conn = connect()
            cur1 = conn.cursor()
            cur2 = conn.cursor()
            seuil = request.form['seuil']
            print seuil + '==============================='
            cur1.execute(
                """
                DROP TABLE IF EXISTS threshold;
                CREATE TABLE threshold (LIKE index_global);
                DROP TABLE IF EXISTS help_proba;
                CREATE TABLE help_proba (proba NUMERIC(10,8));
                DROP TABLE IF EXISTS index_global_bis;
                CREATE TABLE index_global_bis (LIKE index_global);
                INSERT INTO index_global_bis
                SELECT * FROM  index_global WHERE proba>= """+seuil+""";
                """
            )
            cur1.execute(
                """
                SELECT adress FROM index_global_bis
                """
            )
            listeTuples = cur1.fetchall()
            tab = []
            for tuple in listeTuples:
                adressFull = tuple[0].rstrip()
                tabAdressFull = adressFull.split("-")
                ip = tabAdressFull[0]
                farm = tabAdressFull[1]
                print ip
                print farm
                if (ip == 'localhost'):
                    cur2.execute(
                        """
                        INSERT INTO help_proba
                        SELECT proba FROM """+farm+"""
                        WHERE proba>=
                        """+seuil+"""
                        """
                    )
                    cur2.execute(
                        """
                        SELECT * FROM help_proba
                        """
                    )
                    proba = cur2.fetchall()
                    for p in proba:
                        test = [p[0],ip, farm]
                        tab.append(test)


                else:

                    cur2.execute(
                        """
                        SELECT dblink_connect('conx', 'hostaddr="""+ip+""" port=5432 dbname=PPD user=postgres password=root');
                        """
                    )

                    cur2.execute(
                        """
                            INSERT INTO help_proba
                            SELECT * FROM dblink('conx','SELECT proba FROM """ + farm + """ WHERE proba>=""" + seuil + """ ') AS t(c numeric );
                        """
                    )

                    cur2.execute(
                        """
                        SELECT * FROM help_proba
                        """
                    )
                    proba = cur2.fetchall()
                    for p in proba:
                        test = [p[0], ip, farm]
                        tab.append(test)
                    cur2.execute(
                        """
                        SELECT dblink_disconnect('conx')
                        """
                    )

                tab.sort()
            conn.commit()
            return render_template("threshold_result.html", active="threshold", res=tab)
        return render_template("threshold.html", active="threshold")
    else:
        return redirect(url_for('error'))



@app.route('/db_link')
def db_link():
    return render_template('db_link.html', active="db_link")

@app.route('/error')
def error():
    return render_template("db_error.html")

app.secret_key = '6Mb0JgsZ4HLJpnbSjNiZuTwaSA7RwV3Inf6DUmnu'

if __name__ == '__main__':
    app.run()
