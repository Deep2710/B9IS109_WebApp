from flask import *
import sqlite3,hashlib,os
from werkzeug.utils import secure_filename
import re

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def home():
    loggedIn,firstname = getLoginDetails()
    with sqlite3.connect('ecommerce.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT products.productId, products.productName, products.productPrice, products.productDescription, products.productImage,categories.categoryName FROM products,categories WHERE products.categoryId = categories.categoryId')
        itemData = cur.fetchall()
        cur.execute('SELECT categoryId, categoryName FROM categories')
        categoryData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('home.html', itemData=itemData, loggedIn=loggedIn, firstname=firstname,categoryData=categoryData)

#Fetch user details if logged in
def getLoginDetails():
    with sqlite3.connect('ecommerce.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            firstname = " "
            totalItems = 0
            
        else:
            loggedIn = True
            cur.execute("SELECT id, firstname FROM customer WHERE email = '" + session['email'] + "'")
            id = cur.fetchone()
            print (str (id) + "000" )
            firstname = cur.fetchone()
            
    conn.close()
    return (loggedIn,firstname)


@app.route('/login',methods = ['GET','POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        if valid (email,password):
            session['email'] = email
            return redirect(url_for('home'))

        else:
            msg = 'Incorrect email/password!'
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect(url_for('home'))

@app.route('/register',methods = ['GET','POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'email' in request.form and 'password' in request.form:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        with sqlite3.connect('ecommerce.db') as conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO customer VALUES (NULL,?,?,?,?)',(firstname,lastname,email,hashlib.md5(password.encode()).hexdigest()))
            conn.commit()
            msg = 'You have successfully registered'
            return redirect(url_for('login'))

    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)


def valid (email,password):
    conn = sqlite3.connect('ecommerce.db')
    cur = conn.cursor()
    cur.execute('SELECT email,password from customer')
    data = cur.fetchall()
    for row in data :
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        productName = request.form['productName']
        productPrice = float(request.form['productPrice'])
        productDescription = request.form['productDescription']
        categoryId = int(request.form['categoryId'])

        productImage = request.files['productImage']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO products (productName,productPrice,productDescription,productImage,categoryId) VALUES (?, ?, ?, ?, ?)''', (name, price, description, imagename, categoryId))
                conn.commit()
                msg="Added successfully"
            except:
                msg="Error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return redirect(url_for('root'))

@app.route("/productDescription")
def productDescription():
    loggedIn, firstName = getLoginDetails()
    productId = request.args.get('productId')
    with sqlite3.connect('ecommerce.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, productName, productPrice, productDescription, productImage FROM products WHERE productId = ' + productId)
        productData = cur.fetchone()
        cur.execute('SELECT categoryId, categoryName FROM categories')
        categoryData = cur.fetchall()
    conn.close()
    return render_template("productDescription.html", data=productData, loggedIn = loggedIn, firstName = firstName,categoryData=categoryData)

@app.route("/displayCategory")
def displayCategory():
        loggedIn, firstName = getLoginDetails()
        categoryId = request.args.get("categoryId")
        with sqlite3.connect('ecommerce.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT products.productId, products.productName, products.productPrice, products.productImage, categories.categoryName FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = " + categoryId)
            data = cur.fetchall()
        conn.close()
        categoryName = data[0][4]
        data = parse(data)
        return render_template('displayCategory.html', data=data, loggedIn=loggedIn, firstName=firstName, categoryName=categoryName)

@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        productId = int(request.args.get('productId'))
        with sqlite3.connect('ecommerce.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM customer WHERE email = '" + session['email'] + "'")
            id = cur.fetchone()
            try:
                cur.execute("INSERT INTO cart (id, productId) VALUES (?,?)", (id, productId))
                conn.commit()
                msg = "Added successfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        return redirect(url_for('home'))

@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('login'))
    loggedIn, firstName = getLoginDetails()
    email = session['email']
    with sqlite3.connect('ecommerce.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM customer WHERE email = '" + email + "'")
        id = cur.fetchone()
        cur.execute("SELECT products.productId, products.productName, products.productPrice, products.productImage FROM products, cart WHERE products.productId = cart.productId AND cart.id = " + str(id))
        products = cur.fetchall()
        cur.execute('SELECT categoryId, categoryName FROM categories')
        categoryData = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, totalItems=totalItems,categoryData=categoryData)

@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('login'))
    email = session['email']
    productId = int(request.args.get('productId'))
    with sqlite3.connect('ecommerce.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM customer WHERE email = '" + email + "'")
        id = cur.fetchone()
        try:
            cur.execute("DELETE FROM cart WHERE id = " + str(id) + " AND productId = " + str(productId))
            conn.commit()
            msg = "removed successfully"
        except:
            conn.rollback()
            msg = "error occured"
    conn.close()
    return redirect(url_for('cart'))

@app.route("/checkout")
def checkout():
    if 'email' not in session:
        return redirect(url_for('login'))
    loggedIn, firstName = getLoginDetails()
    email = session['email']
    with sqlite3.connect('ecommerce.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM customer WHERE email = '" + email + "'")
        id = cur.fetchone()
        cur.execute("SELECT products.productId, products.productName, products.productPrice, products.productImage FROM products, cart WHERE products.productId = cart.productId AND cart.id = " + str(id))
        products = cur.fetchall()
        cur.execute('SELECT categoryId, categoryName FROM categories')
        categoryData = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("checkout.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName,categoryData=categoryData)

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

if __name__ == '__main__':
    app.run(debug = True)
