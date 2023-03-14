from flask import render_template, url_for, request, redirect, flash
from shop import app, db
from shop.models import User, Item, Stats
from shop.forms import RegistrationForm, LoginForm, AddtoCart, ItemFilter, CheckoutForm
from flask_login import login_user, logout_user, current_user
from sqlalchemy import desc, asc

@app.route('/',methods=['GET','POST'])
def landing():
    return redirect(url_for("home"))

@app.route('/home',methods=['GET','POST'])
def home():
    form = AddtoCart()
    item_filter = ItemFilter()
    filter_option = item_filter.sort_type.data
    stats = Stats.query.get(0)
    sale_rec_ratio = (f"{stats.sale_rec_ratio:.2f}")

    if current_user.is_authenticated:               # https://stackoverflow.com/questions/20419228/flask-login-check-if-user-is-authenticated-without-decorator
        logged_in_as = current_user.username        # https://github.com/maxcountryman/flask-login
    else:
        logged_in_as = None

    if filter_option == "default":          # https://stackoverflow.com/questions/4186062/sqlalchemy-order-by-descending
        items = Item.query.all()
    elif filter_option == "price_high":
        items = Item.query.order_by(desc(Item.price))
    elif filter_option == "price_low":
        items = Item.query.order_by(asc(Item.price))
    elif filter_option == "eco_low":
        items = Item.query.order_by(asc(Item.footprint))

    return render_template('home.html', items=items, form=form, item_filter=item_filter, logged_in_as=logged_in_as, stats=stats, sale_rec_ratio=sale_rec_ratio)

@app.route('/add_to_cart/<int:item_id>',methods=['GET','POST'])
def add_to_cart(item_id):
    current_cart = current_user.cart
    if (current_cart == None):
        new_cart = str(item_id)
        current_user.cart = new_cart
        db.session.commit()
        flash("Added to cart.")
        return redirect(url_for("home"))


    elif str(item_id) in current_cart:
        flash("Item is already in cart.")
        return redirect(url_for("home"))
    else:
        new_cart = current_cart+str(item_id)
        current_user.cart = new_cart
        db.session.commit()                     # https://stackoverflow.com/questions/6699360/flask-sqlalchemy-update-a-rows-information
        flash("Added to cart.")
        return redirect(url_for("home"))

@app.route('/remove_from_cart/<int:item_id>',methods=['GET','POST'])
def remove_from_cart(item_id):
    current_cart = current_user.cart
    if str(item_id) in current_cart:
        new_cart = current_cart.replace(str(item_id), '')
        current_user.cart = new_cart
        db.session.commit()
        flash("Item removed from cart.")
        return redirect(url_for("cart"))
    else:
        flash("Error removing item.")
        return redirect(url_for("cart"))


@app.route('/cart',methods=['GET','POST'])
def cart():
    form = AddtoCart()

    stats = Stats.query.get(0)
    reviews = stats.reviews
    review_list = reviews.split("|||")
    for review in review_list:
        if review == "":
            review_list.remove(review)

    review_list.reverse()   # Make the latest review show first

    if current_user.is_authenticated:
        logged_in_as = current_user.username
        customer = current_user

        cart_items = []
        for item_id in customer.cart:
            cart_items.append(Item.query.get(item_id))

        price_list = []
        for item in cart_items:
            price_list.append(item.price)
        total = 0
        for price in price_list:
            total += price
        total = (f"{total:.2f}")
    else:
        flash("You must be logged in to view the cart!")
        return redirect(url_for("home"))

    return render_template('cart.html', title='Shopping Cart', form=form, logged_in_as=logged_in_as, customer=customer, cart_items=cart_items, total=total, review_list=review_list)

@app.route('/checkout',methods=['GET','POST'])
def checkout():
    form = CheckoutForm()
    if form.validate_on_submit():
        cart_items = []
        for item_id in current_user.cart:       # Decrement stock
            cart_items.append(Item.query.get(item_id))

        for item in cart_items:
            item.stock = item.stock - 1

        current_user.cart = ""      # Empty cart

        stats = Stats.query.get(0)

        sales = stats.total_sales
        stats.total_sales = sales + 1

        if form.recommend.data == True:
            recommendations = stats.recommendations
            stats.recommendations = recommendations + 1

        db.session.commit()
        stats = Stats.query.get(0)
        stats.sale_rec_ratio = (stats.recommendations)/stats.total_sales

        if (form.comments.data != None) and (form.comments.data != ""):
            current_reviews = stats.reviews
            new_reviews = current_reviews+form.comments.data+"|||"
            stats.reviews = new_reviews

        db.session.commit()
        flash("Your order has been placed! Thank you for your purchase; your flatpack should arrive within 5 working days.", "checkout_success")
        flash("Your order number: #"+str(stats.total_sales))
        return redirect(url_for("home"))
    return render_template('checkout.html', title='Checkout', form=form)


@app.route('/item/<int:item_id>')
def item(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('item.html', name=item.name, item=item)

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data,email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flash("Success! You can now log in with your shiny new credentials. :))", "register_success")
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if (user is not None) and (user.verify_password(form.password.data)):
            login_user(user)
            flash("Logged in successfully.")
            return redirect(url_for("home"))
        flash("Username or password incorrect. Please try again.", "login_error")   # https://riptutorial.com/flask/example/32262/flashing-with-categories
    return render_template('login.html', title="Login", form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for('home'))
