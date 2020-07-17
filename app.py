import sqlite3
from sqlite3 import Error
from flask import Flask, render_template, request, session, g, redirect, url_for, flash

app = Flask(__name__)


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def main():

    sql_create_food_group_table = """ CREATE TABLE IF NOT EXISTS food_group (
                                         id int PRIMARY KEY NOT NULL,
                                         name text NOT NULL,
                                         UNIQUE (id)
                                    );"""

    sql_create_food_table = """ CREATE TABLE IF NOT EXISTS food(
                                      id int PRIMARY KEY NOT NULL,
                                      food_group_id int REFERENCES food_group(id) NOT NULL,
                                      long_desc text NOT NULL DEFAULT '',
                                      short_desc text NOT NULL DEFAULT '',
                                      common_names text NOT NULL DEFAULT '',
                                      manufac_name text NOT NULL DEFAULT '',
                                      survey text NOT NULL DEFAULT '',
                                      ref_desc text NOT NULL DEFAULT '',
                                      refuse int NOT NULL,
                                      sci_name text NOT NULL DEFAULT '',
                                      nitrogen_factor float NOT NULL,
                                      protein_factor float NOT  NULL,
                                      fat_factor float NOT NULL,
                                      calorie_factor float NOT NULL
                                );"""

    sql_create_food_group_index_1 = """CREATE INDEX food_short_desc_search_index ON food(short_desc);"""

    sql_create_food_group_index_2 = """CREATE INDEX food_long_desc_search_index ON food(long_desc);"""

    # create a database connection
    conn = create_connection('usda.db')

    # create tables
    if conn is not None:
        # create food_group table
        create_table(conn, sql_create_food_group_table)

        # adding data into the food_group
        sql_insert = ''' INSERT OR IGNORE INTO food_group(id,name) VALUES (?, ?) '''
        with open('FD_GROUP.txt', 'r') as fr:
            for line in fr.readlines():
                line = line.replace('\n', '').replace(' ', '').split('^')
                t, f = line
                conn.execute(sql_insert, (int(t), f))
        conn.commit()

        create_table(conn, sql_create_food_table)
        create_table(conn, sql_create_food_group_index_1)
        create_table(conn, sql_create_food_group_index_2)
        sql_insert = ''' INSERT OR IGNORE INTO food(id,food_group_id,long_desc,short_desc,common_names,manufac_name,survey,ref_desc,refuse,sci_name,nitrogen_factor,protein_factor,fat_factor,calorie_factor) 
                                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,? ) '''
        with open('FOOD_DES.txt', 'r') as fr:
            for line in fr.readlines():
                line = line.replace('\n', '').replace(' ', '').split('^')
                a, b, c, d, e, f, g, h, i, j, k, lt, m, n = line
                a = int(a) if isint(a) else int(0)
                i = int(i) if isint(i) else int(0)
                k = float(k) if isfloat(k) else float(0)
                lt = float(lt) if isfloat(lt) else float(0)
                m = float(m) if isfloat(m) else float(0)
                n = float(n) if isfloat(n) else float(0)
                conn.execute(sql_insert, (int(a), int(b), c, d, e, f, g, h, int(i), j, k, lt, m, n))
        conn.commit()

    else:
        print("Error! cannot create the database connection.")
    conn.close()


def isint(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('usda.db')
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


app.secret_key = 'secr3t'
app.config['SESSION_TYPE'] = 'filesystem'


@app.route("/")
@app.route("/home")
def home():
    c = get_db().cursor()
    food_group = c.execute('SELECT * FROM food_group')
    return render_template("home.html", all_food_group=food_group)


# show one groups foods
@app.route('/show/<id>/', methods=['GET'])
def show(id):
    c = get_db().cursor()
    group_foods = c.execute('SELECT f.short_desc, f.nitrogen_factor, f.protein_factor, f.fat_factor, f.calorie_factor FROM food AS f '
                           'INNER JOIN food_group AS fg ON f.food_group_id = fg.id  WHERE fg.id = ?',[id])

    return render_template("show.html", foods=group_foods)


# show all foods and pagination
@app.route('/about/', defaults={'page': 0})
@app.route('/about/<int:page>/', methods=['GET', 'POST'])
def about(page):
    every_page = 10
    prev_page = (page-1) if (page > 0) else page
    next_page = page + 1
    c = get_db().cursor()
    current_page = page
    page = page*every_page
    food_items = c.execute('SELECT f.id,f.short_desc, f.long_desc,f.manufac_name, f.sci_name,fg.name AS fgname FROM food f '
                           'INNER JOIN food_group fg ON '
                           'f.food_group_id = fg.id LIMIT ?, ?', (page, every_page)).fetchall()
    food_goups_items = c.execute('SELECT * FROM food_group')

    return render_template("about.html", all_food=food_items, food_groups=food_goups_items, prev_page=prev_page,
                           next_page=next_page, current_page=current_page)


# update food
@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':

        f_id = request.form['id']
        short_desc = request.form['short_desc']
        long_desc = request.form['long_desc']
        manufac_name = request.form['manufac_name']
        sci_name = request.form['sci_name']
        group_name = request.form['name']
        current_page = request.form['current_page']

        c = get_db().cursor()
        group_id = c.execute('SELECT f.id FROM food_group AS f WHERE f.name=?', [group_name]).fetchone()[0]
        update_sql =''' UPDATE food SET food_group_id = ?, short_desc = ?, long_desc = ?, manufac_name = ?, sci_name = ?
              WHERE id = ?'''
        c.execute(update_sql, (group_id, short_desc, long_desc, manufac_name, sci_name, f_id))
        get_db().commit()
        flash("Food Updated Successfully")
        return redirect(url_for('about', page=current_page))


if __name__ == "__main__":
    main()
    app.run(debug=True)
