import sqlite3
conn = sqlite3.connect('ecommerce.db')


conn.execute(''' create table if not exists customer (
id integer primary key,
firstname text,
lastname text,
email text,
password text
)''')

conn.execute(''' create table if not exists categories (
categoryId integer primary key,
categoryName text
)''')


conn.execute('''create table if not exists products (
productId integer primary key,
productName text,
productPrice real,
productDescription text,
productImage text,
categoryId integer,
foreign key (categoryId) references categories (categoryId)
)''')

conn.execute(''' create table if not exists cart (
id integer,
productId integer,
foreign key (id) references customer(id)
foreign key (productId) references products(productId)
)''')




conn.close()
