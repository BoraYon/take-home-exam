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

    sql_create_nutrition = """CREATE TABLE IF NOT EXISTS nutrition (
                                 food_id int REFERENCES food(id) NOT NULL,
                                 nutrient_id int REFERENCES nutrient(id) NOT NULL,
                                 amount float NOT NULL,
                                 num_data_points int NOT NULL,
                                 std_error float,
                                 source_code text NOT NULL DEFAULT '',
                                 derivation_code text,
                                 reference_food_id REFERENCES food(id),
                                 added_nutrient text,
                                 num_studients int,
                                 min float,
                                 max float,
                                 degrees_freedom int,
                                 lower_error_bound float,
                                 upper_error_bound float,
                                 comments text,
                                 modification_date text,
                                 confidence_code text,
                                 PRIMARY KEY(food_id, nutrient_id)
       );"""

    sql_create_weights = """ CREATE TABLE IF NOT EXISTS weight (
        food_id int REFERENCES food(id) NOT NULL,
        sequence_num int NOT NULL,
        amount float NOT NULL,
        description text NOT NULL DEFAULT '',
        gm_weight float NOT NULL,
        num_data_pts int,
        std_dev float,
        PRIMARY KEY(food_id, sequence_num)
    );"""

    sql_create_nutrient = """CREATE TABLE nutrient (
              id int PRIMARY KEY NOT NULL,
              units text NOT NULL DEFAULT '',
              tagname text NOT NULL DEFAULT '',
              name text NOT NULL DEFAULT '',
              num_decimal_places text NOT NULL,
              sr_order int NOT NULL
    );"""

    sql_create_nutrient_index = """CREATE INDEX nutrient_name_search_index ON nutrient(name);"""

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

        create_table(conn, sql_create_nutrition)
        sql_insert = ''' INSERT OR IGNORE INTO 
            nutrition(food_id,nutrient_id,amount,num_data_points,std_error,
            source_code,derivation_code,reference_food_id,added_nutrient,num_studients,min,max,
            degrees_freedom,lower_error_bound,upper_error_bound,comments,modification_date,confidence_code) 
            VALUES (?, ?,?,?, ?,?,?, ?,?,?, ?,?,?, ?,?,?, ?,?) '''
        with open('NUT_DATA.txt', 'r') as fr:
            for line in fr.readlines():
                line = line.replace('\n', '').replace(' ', '').split('^')
                a, b, c, d, e, f, g, h, i, j, k, lt, m, n, o, p, r, s = line
                a = int(a) if isint(a) else int(0)
                b = int(b) if isint(b) else int(0)
                c = float(c) if isfloat(c) else float(0)
                d = int(d) if isint(d) else int(0)
                h = int(h) if isint(h) else int(0)
                j = int(j) if isint(j) else int()
                k = float(k) if isfloat(k) else float()
                lt = float(lt) if isfloat(lt) else float()
                m = int(m) if isint(m) else int()
                n = float(n) if isfloat(n) else float()
                o = float(o) if isfloat(o) else float()
                conn.execute(sql_insert, (
                    int(a), int(b), float(c), int(d), e, f, g, int(h), i, j, k,
                    float(lt), int(m), float(n), float(o), p, r, s))
        conn.commit()

        create_table(conn, sql_create_weights)
        sql_insert = ''' INSERT OR IGNORE INTO weight(food_id, sequence_num, amount, description, gm_weight, num_data_pts, std_dev) 
                                                  VALUES (?,?,?,?,?,?,? ) '''
        with open('WEIGHT.txt', 'r') as fr:
            for line in fr.readlines():
                line = line.replace('\n', '').replace(' ', '').split('^')
                a, b, c, d, e, f, g = line
                a = int(a) if isint(a) else int(0)
                b = int(b) if isint(b) else int(0)
                c = float(c) if isfloat(c) else float()
                e = float(e) if isfloat(e) else float()
                f = int(f) if isint(f) else int()
                g = float(g) if isfloat(g) else float()
                conn.execute(sql_insert, (int(a), int(b), c, d, float(e), int(f), float(g)))
        conn.commit()

        create_table(conn, sql_create_nutrient)
        create_table(conn, sql_create_nutrient_index)
        # adding data into nutrient
        sql_insert = ''' INSERT OR IGNORE INTO nutrient(id,units,tagname,name,
                                            num_decimal_places,sr_order) VALUES (?, ?, ?, ?, ?, ?) '''
        with open('NUTR_DEF.txt', 'r') as fr:
            for line in fr.readlines():
                line = line.replace('\n', '').replace(' ', '').split('^')
                a, b, c, d, e, f= line
                a = int(a) if isint(a) else int(0)
                g = int(g) if isint(g) else int()
                conn.execute(sql_insert, (int(a), b, c, d, e, int(f)))
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
    food_goups_items = c.execute('SELECT * FROM food_group').fetchall()

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

# show food's nutritions info
@app.route('/showNutrients/<int:id>-<int:current_page>', methods=['GET'])
def shownutrients(id, current_page):
    c = get_db().cursor()
    food_nutrients = c.execute('SELECT nu.name, n.amount, n.num_data_points, n.derivation_code, n.min, n.degrees_freedom FROM nutrition n INNER JOIN nutrient nu ON '
                            'n.nutrient_id = nu.id WHERE n.food_id = ?', [id]).fetchall()
    return render_template("shownutrition.html", food_nutrients=food_nutrients, current_page=current_page)

# show food's weights info
@app.route('/showFoodWeights/<int:id>-<int:current_page>', methods=['GET'])
def showfoodweights(id, current_page):
    c = get_db().cursor()
    food_weights = c.execute('SELECT * FROM weight WHERE weight.food_id = ?', [id]).fetchall()
    return render_template("showweight.html", food_weights=food_weights, current_page=current_page)


if __name__ == "__main__":
    main()
    app.run(debug=True)
