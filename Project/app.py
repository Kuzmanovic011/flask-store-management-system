
from flask import *
from functools import *
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "funkcionalnoProgramiranje"

def ucitajKorisnike():
    with open('users.json') as f:
        users = json.load(f)
    return users

def ucitajProizvode():
    with open('proizvodi.json') as f:
        proizvodi = json.load(f)
    return proizvodi

def sacuvajKorisnike(korisnici):
    with open('users.json', "w", encoding="utf-8") as f:
        json.dump(korisnici, f, indent=4)

def sacuvajProizvode(proizvodi):
    with open('proizvodi.json', "w", encoding="utf-8") as f:
        json.dump(proizvodi, f, indent=4)

class Korisnik():
    def __init__(self,ime,prezime,username,password,uloga):
        self.ime = ime
        self.prezime = prezime
        self.username = username
        self.sifra = password
        self.uloga = uloga


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pocetna')
def pocetna():
    users = ucitajKorisnike()

    if 'admin' in session:

        proizvodi = ucitajProizvode()
        vrednosti_proizvoda = list(map(lambda p: int(p['cena']) * int(p['stanje']), proizvodi.values()))
        ukupna_vrednost = reduce(lambda x, y: x + y, vrednosti_proizvoda, 0)

        username = session['admin']

        for user in users.values():
            if user['username'] == username:
                korisnik = Korisnik(
                    user['ime'],
                    user['prezime'],
                    user['username'],
                    user['sifra'],
                    user['uloga']
                )


                return render_template(
                    'korisnik.html',
                    korisnik=korisnik,
                    proizvodi=proizvodi,
                    korisnici=users,
                    ukupna_vrednost=ukupna_vrednost
                )

    elif 'korisnik' in session:
        username = session['korisnik']
        proizvodi = ucitajProizvode()
        dostupniProizvodi = dict(
            filter(lambda x: int(x[1]['stanje']) > 0, proizvodi.items())
        )
        for user in users.values():
            if user['username'] == username:
                korisnik = Korisnik(
                    user['ime'],
                    user['prezime'],
                    user['username'],
                    user['sifra'],
                    user['uloga']
                )

                return render_template(
                    'korisnik.html',
                    korisnik=korisnik,
                    proizvodi = dostupniProizvodi,
                )


    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    users = ucitajKorisnike()
    # print(users)

    if request.method == 'GET':
        return redirect(url_for('index'))
    elif request.method == 'POST':
        username = request.form['username'].lower().strip()
        password = request.form['password'].lower().strip()

        if username == '' or password == '':
            return redirect(url_for('index'))


        for user in users.values():
            if user['username'] == username and user['sifra'] != password:
                flash("Pogresili ste sifru")
                return redirect(url_for('index'))

            if user['username'] == username and user['sifra'] == password and user['uloga'] == 'korisnik':
                session.clear()
                session['korisnik'] = username

                return redirect(url_for('pocetna'))

            elif user['username'] == username and user['sifra'] == password and user['uloga'] == 'admin':
                session.clear()
                session['admin'] = username

                return redirect(url_for('pocetna'))


        return render_template('registracija.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        users = ucitajKorisnike()
        ind = 1

        for i in users.items():
            ind+=1

        username = request.form['username'].lower().strip()
        password = request.form['password'].lower().strip()
        ime = request.form['ime'].lower().strip()
        prezime = request.form['prezime'].lower().strip()
        uloga = request.form['uloga'].lower().strip()

        korisnik = Korisnik(ime,prezime,username,password,uloga)

        for user in users.values():
            if username == user['username']:
                flash('Korisnik sa unetim korisnickim imenom vec postoji')
                return redirect(url_for('register'))

        users[str(ind)] = korisnik.__dict__
        sacuvajKorisnike(users)
        return redirect(url_for('index'))

    else:
        return render_template('registracija.html')

@app.route('/izmenaProizvoda/<id>',methods=['GET', 'POST'])
def izmenaProizvoda(id):
    if 'admin' not in session:
        return redirect(url_for('index'))

    proizvodi = ucitajProizvode()
    if request.method == 'GET':

        proizvod = list(filter(lambda x: x == id, proizvodi.keys()))

        return render_template('izmenaProizvoda.html',
                               proizvod = proizvodi[proizvod[0]],
                               idProizvoda = int(proizvod[0]))

    elif request.method == 'POST':

        proizvodi[id]['cena'] = request.form['cena']
        proizvodi[id]['stanje'] = request.form['stanje']

        sacuvajProizvode(proizvodi)
        return redirect(url_for('pocetna'))
        # print('dosao sam iz forme')

@app.route('/izmenaKorisnika/<id>',methods=['GET', 'POST'])

def izmenaKorisnika(id):
    if 'admin' not in session:
        return redirect(url_for('index'))

    korisnici = ucitajKorisnike()

    if request.method == 'GET':
        korisnik = list(filter(lambda x: x == id, korisnici.keys()))
        # print(korisnik)
        if session['admin'] == korisnici[korisnik[0]]['username']:
            flash('ne mozete sami sebi menjati status')
            return redirect(url_for('pocetna'))

        return render_template('izmenaKorisnika.html',
                               korisnik=korisnici[korisnik[0]],
                               idKorisnika=int(korisnik[0]))

    elif request.method == 'POST':
        if request.form['uloga'] == '':
            return redirect(url_for('pocetna'))

        korisnici[id]['uloga'] = request.form['uloga']
        sacuvajKorisnike(korisnici)
        return redirect(url_for('pocetna'))

@app.route('/obrisiProizvod/<id>',methods=['GET', 'POST'])
def obrisiProizvod(id):
    proizvodi = ucitajProizvode()
    if request.method == 'GET':
        proizvodi.pop(id)
        sacuvajProizvode(proizvodi)
        flash("Proizvod je uspešno obrisan")
        return redirect(url_for('pocetna'))

@app.route('/narucivanje',methods=['GET', 'POST'])
def narucivanjef():
    proizvodi = ucitajProizvode()
    if 'korisnik' not in session:
        return redirect(url_for('index'))
    idProizvoda = request.form['idProizvoda']

    proizvodi[idProizvoda]['stanje'] = str(int(proizvodi[idProizvoda]['stanje']) - int(request.form['kolicina']))
    print(proizvodi[idProizvoda]['stanje'])
    sacuvajProizvode(proizvodi)
    cenaRacuna = float(proizvodi[idProizvoda]['cena']) * float(request.form['kolicina'])
    sada = datetime.now()

    datum_vreme = sada.strftime("%d.%m.%Y_%H-%M-%S")
    nazivDatoteke = session['korisnik']+datum_vreme

    with open(f'racuni/{nazivDatoteke}.txt', 'w') as f:
        f.write(f'Korisnik {session['korisnik']} {datum_vreme}\n'
                f'Cena Racuna je: {cenaRacuna}RSD\n'
                f'Kupili ste {proizvodi[idProizvoda]['naziv']} - kolicina {request.form["kolicina"]}\n')

    return redirect(url_for('pocetna'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)