import sqlite3
import cv2
import os
import pickle
import sys
import numpy
import matplotlib.pyplot as plt
from enhance import image_enhance
from skimage.morphology import skeletonize, thin

from run import FingerprintNotFoundError

def removedot(invertThin):
    temp0 = numpy.array(invertThin[:])
    temp0 = numpy.array(temp0)
    temp1 = temp0 / 255
    temp2 = numpy.array(temp1)

    enhanced_img = numpy.array(temp0)
    filter0 = numpy.zeros((10, 10))
    W, H = temp0.shape[:2]
    filtersize = 6

    for i in range(W - filtersize):
        for j in range(H - filtersize):
            filter0 = temp1[i:i + filtersize, j:j + filtersize]

            flag = 0
            if sum(filter0[:, 0]) == 0:
                flag += 1
            if sum(filter0[:, filtersize - 1]) == 0:
                flag += 1
            if sum(filter0[0, :]) == 0:
                flag += 1
            if sum(filter0[filtersize - 1, :]) == 0:
                flag += 1
            if flag > 3:
                temp2[i:i + filtersize, j:j +
                      filtersize] = numpy.zeros((filtersize, filtersize))
    return temp2

def get_descriptors(img):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img = clahe.apply(img)
    img = image_enhance.image_enhance(img)
    img = numpy.array(img, dtype=numpy.uint8)
    # Threshold
    ret, img = cv2.threshold(
        img, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    # Normalize to 0 and 1 range
    img[img == 255] = 1

    skeleton = skeletonize(img)
    skeleton = numpy.array(skeleton, dtype=numpy.uint8)
    skeleton = removedot(skeleton)
    harris_corners = cv2.cornerHarris(img, 3, 3, 0.04)
    harris_normalized = cv2.normalize(
        harris_corners,
        0,
        255,
        norm_type=cv2.NORM_MINMAX,
        dtype=cv2.CV_32FC1)
    threshold_harris = 125
    # Extract keypoints
    keypoints = []
    for x in range(0, harris_normalized.shape[0]):
        for y in range(0, harris_normalized.shape[1]):
            if harris_normalized[x][y] > threshold_harris:
                keypoints.append(cv2.KeyPoint(y, x, 1))
    orb = cv2.ORB_create()
    _, des = orb.compute(img, keypoints)
    return (keypoints, des)


def main(image_path,filename):
    des = get_des_input(image_path)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    user = comparisons_with_permitted_images(des, bf,filename)
    if user:
        return user
    else:
        return False

def comparisons_with_permitted_images(sample_fingerprint, bf, filename):
    score_threshold = 33
    for user in users_authorization_and_authentication():
        permitted_fingerprint = get_des_permitted(filename)
        matches = sorted(bf.match(sample_fingerprint, permitted_fingerprint), key=lambda match: match.distance)
        print(user["fingerprint"])
        score = 0
        for match in matches:
            score += match.distance
        actual_score = score / len(matches)
        print(actual_score)

        if actual_score < score_threshold:
            return user

def get_des_permitted(image_name):
    image_pickle = "database/pickles/" + image_name

    print("nome da imagem "+ image_name)

    if os.path.exists(image_pickle):
        print("unpickled")
        pickle_file = open(image_pickle, 'rb')
        image_desc = pickle.load(pickle_file)
        pickle_file.close
    else:
        print("pickled")
        image_path = "database/permitted/" + image_name
        image_desc = get_des(image_path)
        pickle_file = open(image_pickle, 'wb')
        pickle.dump(image_desc, pickle_file)
        pickle_file.close

    return image_desc

def get_des_input(image_path):
    print(image_path)
    return get_des(image_path)

def get_des(image_path):
    if os.path.exists(image_path):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        kp, des = get_descriptors(img)
        return des
    else:
        raise FingerprintNotFoundError()

def users_authorization_and_authentication():
    # Conectar ao banco de dados
    conn = sqlite3.connect('pesticides.db')
    cursor = conn.cursor()
    cursor.execute("SELECT firstname || ' ' || lastname AS name, pesticide, 3  FROM farmers")
    database = []

    for row in cursor.fetchall():
        database.append({
            "name": row[0],
            "fingerprint": row[1],
            "level": int(row[2])
        })
    # Fechar a conexão
    conn.close()

    return database

if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except BaseException:
        raise

    import sqlite3

    import cv2
    from flask import (
        Flask,
        render_template,
        redirect,
        request,
        url_for,
        flash,
        session
    )
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy import text
    import app as login_user
    import os
    import re
    import secrets

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pesticides.db'
    db = SQLAlchemy(app)


    # Modelos do banco de dados
    class Farmer(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        firstname = db.Column(db.String(50))
        lastname = db.Column(db.String(50))
        localization = db.Column(db.String(100))
        level = db.Column(db.Integer)
        fingerprint = db.Column(db.String(100))


    # Criar as tabelas
    with app.app_context():
        db.create_all()


    @app.route('/')
    def index():
        return redirect('/login', code=302)


    @app.route('/login')
    def login():
        username = session.get('name')
        level = session.get('level')

        if username and level:
            return redirect('/farmers', code=302)
        else:
            return render_template('login.html')


    class FingerprintNotFoundError(Exception):
        pass  # Sem mensagem específica para a exceção


    @app.route('/login', methods=['POST'])
    def login_post():
        file = request.files['file']
        filename = file.filename

        if re.match(r'.*\.(png|tif|gif|tiff)$', filename):
            image_path = os.path.join('database/uploaded', filename)
            file.save(image_path)

            try:
                user = login_user.main(image_path, filename)
                if user:
                    session['name'] = user['name']
                    session['level'] = user['level']
                    return redirect('/farmers')
                else:
                    flash('Impressão digital incorreta ou não autorizada!')
                    return redirect('/login', code=302)
            except FingerprintNotFoundError:
                flash('Impressão digital incorreta ou não autorizada!')  # Mensagem genérica
                return redirect('/login', code=302)

            except Exception:
                # Capturar qualquer outro erro inesperado e redirecionar também para o login
                flash('Erro no processamento da impressão digital! Tente novamente.')
                return redirect('/login', code=302)
        else:
            flash('Impressão digital incorreta ou não autorizada!')
            return redirect('/login', code=302)


    @app.route('/logout', methods=['POST'])
    def logout():
        session.pop('name')
        session.pop('level')

        return redirect('/login', code=302)


    @app.route('/farmers/')
    def farmers():
        username = session.get('name')
        level = session.get('level')

        if username and level:
            levels = [*range(1, level + 1)]
            levels_string = str(levels).replace('[', '(').replace(']', ')')

            results = Farmer.query.filter(Farmer.level.in_(levels)).all()

            return render_template('farmers.html', results=results, username=username, level=level)

        else:
            flash('Não autorizado!')
            return redirect('/login', code=302)


    @app.route('/view_database')
    def view_database():
        # Consultar o banco de dados para buscar todos os registros da tabela farmers
        records = Farmer.query.all()

        with app.app_context():
            db.session.query(Farmer).delete()
            db.session.commit()

        # Enviar os dados para o template view_database.html
        return render_template('view_database.html', records=records)


    # Função para validar se a imagem possui características de uma impressão digital
    def is_fingerprint(image_path):
        # Carrega a imagem em escala de cinza
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        # Aplica um filtro de limiar para destacar linhas
        _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)

        # Detecta contornos para identificar padrões de cristas e vales
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Definir um critério básico para impressão digital: quantidade de contornos
        if len(contours) > 20 and len(contours) < 200:  # Ajuste o número conforme necessário
            return True
        else:
            return False


    # Rota para o cadastro
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            localization = request.form['localization']
            level = request.form['level']
            file = request.files['file']

            if re.match(r'.*\.(png|tif|gif|tiff)$', file.filename):
                fingerprint_path = os.path.join('database/permitted', file.filename)
                os.makedirs(os.path.dirname(fingerprint_path), exist_ok=True)
                file.save(fingerprint_path)

                # Valida se a imagem tem características de uma impressão digital
                if not is_fingerprint(fingerprint_path):
                    flash("A imagem não parece ser uma impressão digital válida.")
                    os.remove(fingerprint_path)  # Remove a imagem inválida
                    return redirect('/register')

                # Cria novo registro no SQLAlchemy
                new_farmer = Farmer(
                    firstname=firstname, lastname=lastname,
                    localization=localization, level=int(level), fingerprint=fingerprint_path
                )
                db.session.add(new_farmer)
                db.session.commit()

                # Adicionar o novo registro à tabela farmers no SQLite
                with sqlite3.connect('pesticides.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO farmers (firstname, lastname, localization, pesticide, category)
                        VALUES (?, ?, ?, ?, ?)
                    """, (firstname, lastname, localization, "Desconhecido", level))

                flash('Usuário cadastrado com sucesso!')
                return redirect('/login')

            else:
                flash('Arquivo de impressão digital inválido!')

        return render_template('login.html')


    if __name__ == "__main__":
        app.secret_key = secrets.token_urlsafe(24)
        app.config['SESSION_TYPE'] = 'filesystem'
        app.run(debug=True)