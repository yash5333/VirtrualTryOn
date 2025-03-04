from flask import Flask, render_template,request,jsonify,redirect,url_for,session
import os
import random
import json
from PIL import Image

app = Flask(__name__)
app.secret_key = 'your_secret_key'


with open('data.json', 'r') as jf:
    data = json.load(jf)

@app.route('/get_data', methods=['GET'])
def getData():
    try:
        with open('dataset.json', 'r') as file:
            dataset = file.read()
            return jsonify(dataset)
    except FileNotFoundError:
        return jsonify({"error": "Dataset not found"}), 404

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/', methods=['GET', 'POST'])
def login():
  
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        print('user'+email+ "password" +password )

        session['user']=email
        session.permanent = True
        if data['login'].get(email, None) and data['login'][email]==password:
            return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirmPassword = request.form['confirm-password']

        print('user'+email+ "password" +password +'confirmPassword'+confirmPassword )
        data['login'][email] = password

        with open('data.json', 'w') as f:
            json.dump(data, f)

        session['user']=email
        session.permanent = True

        return redirect(url_for('home'))
    
    return render_template('register.html')



def get_womens_items():

    global womens_images_folder
    womens_images_folder = os.path.join(app.static_folder, 'assets', 'women','tops')

    # Get a list of filenames in the folder
    womens_clothing_images = [file for file in os.listdir(womens_images_folder) if file.endswith(('.jpg', '.png', '.jpeg'))]

    # Create a list of dictionaries with image and random price
    womens_clothing_data = [{'image': file, 'price': random.randint(400, 600)} for file in womens_clothing_images]

    return womens_clothing_data


# @app.route('/women', methods=['GET', 'POST'])
# def women():

#     women_data = get_womens_items()

#     if request.method == 'POST':
#         index = int(request.form.get('index'))
#         uploaded_file = request.files['file']

#         # do processing
#         im = Image.open(os.path.join(womens_images_folder, women_data[index]['image']))
#         im.save('./inputs/cloth.jpg')
#         uploaded_file.save('./inputs/model.jpg')

#         #temp image src , replace with result src
#         image="/static/assets/mens/tshirt-4.png"
#         return jsonify(image)
        

#     return render_template('women.html',women_data=women_data,len=len(women_data))


# Dynamic route for individual product pages
@app.route('/<gender>/<category>/<int:index>', methods=['GET','POST'])
def product_details(gender, category, index):

    print(gender,category,index)
    if request.method == 'POST':
        gender = gender.replace('"','')
        with open('dataset.json', 'r') as file:
            dataset = json.load(file)
            products = dataset.get(gender, {}).get(category, [])

            print(products)
            if 0 <= index < len(products):
                # Retrieve the details of the selected product using the index
                selected_product = products[index]

                # cloth image path
                img = selected_product['img']
                uploaded_img = request.files['file']

                # do processing

                print("Reached Here !")

                #temp image src , replace with result src
                image="/static/assets/mens/shirts/shirt2.png"
                return jsonify(image)
            return jsonify("No products found")
    else:
        print("out of if")
        with open('dataset.json', 'r') as file:
            dataset = json.load(file)
            products = dataset.get(gender, {}).get(category, [])

            if 0 <= index < len(products):
                # Retrieve the details of the selected product using the index
                selected_product = products[index]
                img = selected_product['img'].replace("./static/","")
                return render_template('product_details.html', product=selected_product,gender=gender,img=img,index=index)
            else:
                return render_template('error.html', message=f'Invalid index for {category}')
        

# Assuming cart.json exists and is initially an empty dictionary
cart_data = {}

@app.route('/add_to_cart/<gender>/<category>/<int:index>', methods=['POST'])
def addToCart(gender, category, index):
    try:
        with open('dataset.json', 'r') as file:
            dataset = json.load(file)
            products = dataset.get(gender, {}).get(category, [])

            if 0 <= index < len(products):
                # Retrieve the details of the selected product using the index
                selected_product = products[index]

                user = session.get('user')
                # Construct the key for the user in the cart
                user_key = user + str(request.remote_addr)

                # If the user does not exist in the cart, create an empty list
                if user_key not in cart_data:
                    cart_data[user_key] = []

                # Append the selected product to the user's cart
                cart_data[user_key].append(selected_product)

                # Save the updated cart data to cart.json
                with open('cart.json', 'w') as cart_file:
                    json.dump(cart_data, cart_file, indent=2)

                return jsonify({"message": "Added to Cart"})
            else:
                return jsonify({"error": f'Invalid index for {category}'}), 404
    except FileNotFoundError:
        return jsonify({"error": 'Dataset not found'}), 500




@app.route('/men', methods=['GET','POST'])
def men():
    return render_template('men.html')

@app.route('/women', methods=['GET','POST'])
def women():
    return render_template('women.html')

@app.route('/view-cart', methods=['GET','POST'])
def view_cart():
    if 'user' not in session:
        # If the user is not logged in, redirect them to the login page
        return redirect('/login')  # Provide the correct login page URL

    current_user = session['user']
    if request.method == 'GET':
        # Read cart data from cart.json for the current user
        with open('cart.json', 'r') as cart_file:
            cart_data = json.load(cart_file).get(current_user+str(request.remote_addr), [])

        print(cart_data)

        return render_template('view_cart.html', cart_data=cart_data)

if __name__ == '__main__':
    app.run(debug=True)