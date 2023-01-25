# url_for untuk handel URL dan redirect untuk mengarahkan ke route tertentu
from flask import Flask, render_template, url_for, redirect, request, session, flash
from werkzeug.utils import secure_filename
import pymysql
import base64

app = Flask(__name__)
app.secret_key = 'asdfghjkl12345fdsa_fdsakld8rweodfds'

# mysql config
host = 'localhost'
user = 'root'
password = ''
db = 'bookshelves'
mysql = pymysql.connect(host=host,user=user,password=password,db=db,)

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    if request.form['username'] != 'admin' and request.form['password'] != '123':
      flash('Invalid username/password', 'danger')
    else:
      session['logged_in'] = True
      flash('Berhasil masuk', 'success')
      return redirect(url_for('dashboard'))
  return render_template('login.html')

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  flash('Berhasil keluar', 'success')
  return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
  cursor = mysql.cursor()
  cursor.execute(''' SELECT * FROM shelf_one ''')
  books = cursor.fetchall()
  pdf = base64.b64decode(books[4])
  cursor.close()
  return render_template('dashboard.html', books=books, pdf=pdf)


@app.route('/book/add', methods=['GET', 'POST'])
def addBook():
  if request.method == 'GET':
    return render_template('book/add.html')
  else:
    title = request.form['title']
    author = request.form['author']
    published = request.form['published']
    file = request.files['file']
    file.save(secure_filename(file.filename))
    file = file.filename

    cursor = mysql.cursor()
    cursor.execute(''' INSERT INTO shelf_one(title, author, published, file) VALUES(%s,%s,%s,%s) ''',(title,author,published, file))
    mysql.commit()
    cursor.close()
    flash('Data berhasil ditambahkan', 'success')
    return redirect(url_for('dashboard'))
  return render_template('dashboard.html')


@app.route('/book/edit/<int:id>', methods=['GET', 'POST'])
def editBook(id):
  if request.method == 'GET':
    cursor = mysql.cursor()
    cursor.execute('''
    SELECT * 
    FROM shelf_one 
    WHERE book_id=%s''', (id, ))
    book = cursor.fetchone()
    cursor.close()

    return render_template('book/edit.html', book=book)
  else:
    title = request.form['title']
    author = request.form['author']
    published = request.form['published']

    cursor = mysql.cursor()
    cursor.execute(''' 
    UPDATE shelf_one 
    SET 
        title = %s,
        author = %s,
        published = %s
    WHERE
        book_id = %s;
    ''',(title,author,published,id))
    
    mysql.commit()
    cursor.close()
    flash('Data berhasil diperbarui','success')
    return redirect(url_for('dashboard'))

  return render_template('dashboard.html')


@app.route('/book/delete/<int:id>', methods=['GET'])
def deleteBook(id):
  if request.method == 'GET':
    cursor = mysql.cursor()
    cursor.execute('''
    DELETE 
    FROM shelf_one 
    WHERE book_id=%s''', (id, ))
    mysql.commit()
    cursor.close()
    flash('Data berhasil dihapus', 'success')
    return redirect(url_for('dashboard'))

  return render_template('dashboard.html')

if __name__ == '__main__':
  app.run(debug=True)