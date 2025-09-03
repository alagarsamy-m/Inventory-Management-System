from flask import Flask, render_template, request, redirect, url_for,flash
import mysql.connector

app = Flask(__name__)
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='12345',
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
        if 'add_product' in request.form:
            name = request.form['name']
            quantity = request.form['quantity']
            cursor.execute('INSERT INTO {}_Products (product_name, quantity) VALUES (%s, %s)'.format(
                city), (name, quantity,))
            db.commit()
        elif 'edit_product' in request.form:
            product_id = request.form['product_id']
            new_quantity = request.form['new_quantity']
            cursor.execute('UPDATE {}_Products SET quantity = %s WHERE product_id = %s'.format(
                city), (new_quantity, product_id,))
            db.commit()
        elif 'delete_product' in request.form:
            product_id = request.form['product_id']
            cursor.execute('DELETE FROM {}_Products WHERE product_id = %s'.format(city), (product_id,))
            db.commit()
        elif 'add_location' in request.form:
            name = request.form['location_name']
            cursor.execute(
                'INSERT INTO Location (location_name) VALUES (%s)', (name,))
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS {}_Products (product_id INT, product_name VARCHAR(100) PRIMARY KEY, quantity INT, location_name VARCHAR(100))'.format(city))
            db.commit()
    cursor.execute('SELECT * FROM Location')
    locations = cursor.fetchall()
    if city:
        cursor.execute('SELECT * FROM {}_Products'.format(city))
        products = cursor.fetchall()
    return render_template('inventory.html', products=products, locations=locations, city=city)


@app.route('/locations', methods=['GET', 'POST'])
def locations():
    if request.method == 'POST':
        if 'add_location' in request.form:
            name = request.form['name']
            cursor.execute('INSERT INTO Location (name) VALUES (%s)', (name,))
            db.commit()
            cursor.execute('CREATE TABLE {}_products (product_id INT PRIMARY KEY AUTO_INCREMENT,name VARCHAR(100),quantity INT)'.format(name))
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

            #product Movements
            cursor.execute("INSERT INTO ProductMovement (from_location, to_location, product, qty) VALUES (%s, %s, %s, %s)", (starting_location, ending_location, item, stock_quantity,))
            db.commit()

            # fetching current details
            cursor.execute("SELECT * FROM {}_products".format(starting_location))
            startloc_current = cursor.fetchall()
            cursor.execute("SELECT * FROM {}_products".format(ending_location))
            endloc_current = cursor.fetchall()

            # fetching CURRENT stock record for START and DESTINATION location

            cursor.execute("SELECT quantity FROM {}_products".format(starting_location))
            startloc_current_stock = cursor.fetchall()
            cursor.execute("SELECT quantity FROM {}_products".format(ending_location))
            endloc_current_stock = cursor.fetchall()

            # Consume unread result
            cursor.fetchall()

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
                cursor.execute("UPDATE {}_products SET quantity = %s where product_name = %s ".format(starting_location),
                               (startloc_after_stock, item,))
                cursor.execute("UPDATE {}_products SET quantity = %s where product_name = %s ".format(ending_location),
                               (endloc_after_stock, item,))

                # fetching UPDATED stock record for START and DESTINATION location
                cursor.execute("SELECT * FROM {}_products where product_name = %s".format(starting_location), (item,))
                after_transport_startloc_item = cursor.fetchall()
                cursor.execute("SELECT * FROM {}_products where product_name = %s".format(ending_location), (item,))
                after_transport_endloc_item = cursor.fetchall()
            return render_template('result.html', starting_location=starting_location, startloc_current=startloc_current[0],ending_location = ending_location, endloc_current=endloc_current[0], after_transport_startloc_item=after_transport_startloc_item[0], after_transport_endloc_item=after_transport_endloc_item[0], item = item)
        #return render_template('result.html')
        except Exception as e:
            flash("An error occurred: {}".format(str(e)))
            return render_template('index.html')#



if __name__ == '__main__':
    app.secret_key = 'qwertyuiop'
    app.run(debug=True)
