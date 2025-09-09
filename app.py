from flask import Flask, render_template, request, redirect, url_for,flash
import mysql.connector

app = Flask(__name__)
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='inventory_management'
)
cursor = db.cursor()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    products = None
    locations = None
    city = None
    if request.method == 'POST':
        city = request.form['city']
        table_name = city.replace(' ', '_') + '_products'
        if 'add_product' in request.form:
            name = request.form['name']
            quantity = request.form['quantity']
            cursor.execute('CREATE TABLE IF NOT EXISTS `{}` (product_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) UNIQUE, quantity INT)'.format(table_name))
            cursor.execute('INSERT INTO `{}` (name, quantity) VALUES (%s, %s)'.format(
                table_name), (name, quantity,))
            db.commit()
        elif 'edit_product' in request.form:
            product_id = request.form['product_id']
            new_quantity = request.form['new_quantity']
            cursor.execute('CREATE TABLE IF NOT EXISTS `{}` (product_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) UNIQUE, quantity INT)'.format(table_name))
            cursor.execute('UPDATE `{}` SET quantity = %s WHERE product_id = %s'.format(
                table_name), (new_quantity, product_id,))
            db.commit()
        elif 'delete_product' in request.form:
            product_id = request.form['product_id']
            cursor.execute('CREATE TABLE IF NOT EXISTS `{}` (product_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) UNIQUE, quantity INT)'.format(table_name))
            cursor.execute('DELETE FROM `{}` WHERE product_id = %s'.format(table_name), (product_id,))
            db.commit()
        elif 'add_location' in request.form:
            name = request.form['location_name']
            cursor.execute(
                'INSERT INTO Location (name) VALUES (%s)', (name,))
            table_name_loc = name.replace(' ', '_') + '_products'
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS `{}` (product_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) UNIQUE, quantity INT)'.format(table_name_loc))
            db.commit()
    cursor.execute('SELECT * FROM Location')
    locations = cursor.fetchall()
    if city:
        table_name = city.replace(' ', '_') + '_products'
        cursor.execute('CREATE TABLE IF NOT EXISTS `{}` (product_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) UNIQUE, quantity INT)'.format(table_name))
        cursor.execute('SELECT * FROM `{}`'.format(table_name))
        products = cursor.fetchall()
    return render_template('inventory.html', products=products, locations=locations, city=city)


@app.route('/locations', methods=['GET', 'POST'])
def locations():
    if request.method == 'POST':
        if 'add_location' in request.form:
            name = request.form['name']
            cursor.execute('INSERT INTO Location (name) VALUES (%s)', (name,))
            db.commit()
            table_name = name.replace(' ', '_') + '_products'
            cursor.execute('CREATE TABLE `{}` (product_id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100) UNIQUE, quantity INT)'.format(table_name))
        elif 'delete_location' in request.form:
            name = request.form['name']
            cursor.execute('DELETE FROM Location WHERE name = %s', (name,))
            db.commit()
        return redirect(url_for('locations'))
    else:
        cursor.execute('SELECT * FROM Location')
        locations = cursor.fetchall()
        return render_template('locations.html', locations=locations)


@app.route('/movements', methods=['GET', 'POST'])
def movements():
    cursor.execute('SELECT * FROM ProductMovement')
    movements = cursor.fetchall()
    return render_template('movement.html', movements=movements)


@app.route('/result', methods=['POST'])  # create result page
def result():
    if request.method == 'POST':
        try:
            # get data from html page
            starting_location = request.form['Start']
            ending_location = request.form['End']
            item = request.form['item']
            stock_quantity = request.form['kg']

            table_start = starting_location.replace(' ', '_') + '_products'
            table_end = ending_location.replace(' ', '_') + '_products'

            #product Movements
            cursor.execute("INSERT INTO ProductMovement (from_location, to_location, product, qty) VALUES (%s, %s, %s, %s)", (starting_location, ending_location, item, stock_quantity,))
            db.commit()

            # fetching current details
            cursor.execute("SELECT * FROM `{}` WHERE name = %s".format(table_start), (item,))
            startloc_current = cursor.fetchall()
            cursor.execute("SELECT * FROM `{}` WHERE name = %s".format(table_end), (item,))
            endloc_current = cursor.fetchall()

            # fetching CURRENT stock record for START and DESTINATION location

            cursor.execute("SELECT quantity FROM `{}` WHERE name = %s".format(table_start), (item,))
            startloc_current_stock = cursor.fetchall()
            cursor.execute("SELECT quantity FROM `{}` WHERE name = %s".format(table_end), (item,))
            endloc_current_stock = cursor.fetchall()

            # Consume unread result
            cursor.fetchall()

            # Handle if product doesn't exist in destination
            if len(endloc_current_stock) == 0:
                endloc_current_stock = [[0]]
            if len(endloc_current) == 0:
                endloc_current = [(0, item, 0)]

            # POSSIBLE ERRORS
            # current stock less than transport stock
            if startloc_current_stock[0][0] < int(stock_quantity):
                flash("Products not available to transport your quantity....")
                return render_template('index.html')
            elif str(starting_location) == str(ending_location):  # user selecting same locations
                flash("Select Appropriate District....")
                return render_template('index.html')
            else:
                # UPDATING stock record
                startloc_after_stock = int(startloc_current_stock[0][0]) - int(stock_quantity)
                endloc_after_stock = int(endloc_current_stock[0][0]) + int(stock_quantity)
                cursor.execute("UPDATE `{}` SET quantity = %s where name = %s ".format(table_start),
                               (startloc_after_stock, item,))
                cursor.execute("INSERT INTO `{}` (name, quantity) VALUES (%s, %s) ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)".format(table_end),
                               (item, endloc_after_stock))

                # fetching UPDATED stock record for START and DESTINATION location
                cursor.execute("SELECT * FROM `{}` where name = %s".format(table_start), (item,))
                after_transport_startloc_item = cursor.fetchall()
                cursor.execute("SELECT * FROM `{}` where name = %s".format(table_end), (item,))
                after_transport_endloc_item = cursor.fetchall()

                # Handle if after fetch is empty
                if len(after_transport_endloc_item) == 0:
                    after_transport_endloc_item = [(0, item, endloc_after_stock)]
                if len(after_transport_startloc_item) == 0:
                    after_transport_startloc_item = [(0, item, startloc_after_stock)]
            return render_template('result.html', starting_location=starting_location, startloc_current=startloc_current[0],ending_location = ending_location, endloc_current=endloc_current[0], after_transport_startloc_item=after_transport_startloc_item[0], after_transport_endloc_item=after_transport_endloc_item[0], item = item)
        #return render_template('result.html')
        except Exception as e:
            flash("An error occurred: {}".format(str(e)))
            return render_template('index.html')#



if __name__ == '__main__':
    app.secret_key = 'qwertyuiop'
    app.run(debug=True)
