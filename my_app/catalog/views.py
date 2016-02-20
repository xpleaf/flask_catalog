import os
from werkzeug import secure_filename
from flask import request, jsonify, Blueprint, render_template, \
    flash, redirect, url_for
from sqlalchemy.orm.util import join
from my_app import db, redis
from my_app.catalog.models import Product, Category
from .decorators import template_or_json
from .forms import ProductForm, CategoryForm
from .. import app
from my_app import ALLOWED_EXTENSTIONS

catalog = Blueprint('catalog', __name__)


def allowed_file(filename):
    return '.' in filename and \
        filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSTIONS


@catalog.route('/')
@catalog.route('/home')
@template_or_json('home.html')
def home():
    products = Product.query.all()
    return {'count': len(products)}


@catalog.route('/product/<id>')
def product(id):
    product = Product.query.get_or_404(id)
    # product_key = 'product-%s' % product.id
    # redis.set(product_key, product.name)
    # redis.expire(product_key, 30)
    return render_template('product.html', product=product)


@catalog.route('/recent-products')
def recent_products():
    keys_alive = redis.keys('product-*')
    products = [redis.get(k) for k in keys_alive]
    return jsonify({'products': products})


@catalog.route('/products')
@catalog.route('/products/<int:page>')
def products(page=1):
    # products = Product.query.paginate(page, 2).items
    # res = {}
    # for product in products:
    #     res[product.id] = {
    #         'name': product.name,
    #         'price': str(product.price),
    #         'category': product.category.name
    #     }
    # return jsonify(res)
    products = Product.query.paginate(page, 2)
    return render_template('products.html', products=products)


@catalog.route('/product-create', methods=['GET', 'POST'])
def create_product():
    form = ProductForm(request.form)

    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        category = Category.query.get_or_404(
            form.category.data
        )
        image = request.files['image']
        filename = ''
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        product = Product(name, price, category, filename)
        db.session.add(product)
        db.session.commit()
        flash('The product %s has been created' % name, 'success')
        return redirect(url_for('catalog.product', id=product.id))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('product-create.html', form=form)


@catalog.route('/category-create', methods=['GET', 'POST'])
def create_category():
    form = CategoryForm(request.form)

    if form.validate_on_submit():
        name = form.name.data
        category = Category(name)
        db.session.add(category)
        db.session.commit()
        flash('The category %s has been created' % name,
              'success')
        return redirect(url_for('catalog.create_category',
                                id=category.id))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('category-create.html', form=form)


@catalog.route('/category/<int:id>')
def category(id):
    category = Category.query.get_or_404(id)
    return render_template('category.html', category=category)


@catalog.route('/categories')
def categories():
    categories = Category.query.all()
    # res = {}
    # for category in categories:
    #     res[category.id] = {
    #         'name': category.name
    #     }
    #     res[category.id]['products'] = {}
    #     for product in category.products:
    #         # res[category.id]['products'].setdefault(product.id,
    #         #                                         {'name': product.name,
    #         #                                          'price': product.price})
    #         res[category.id]['products'][product.id] = {'name': product.name,
    #                                                     'price': product.price}
    # return jsonify(res)
    return render_template('categories.html', categories=categories)


@catalog.route('/product-search')
@catalog.route('/product-search/<int:page>')
def product_search(page=1):
    name = request.args.get('name')
    price = request.args.get('price')
    company = request.args.get('company')
    category = request.args.get('category')
    products = Product.query
    if name:
        products = products.filter(Product.name.like('%' + name +'%'))
    if price:
        products = products.filter(Product.price == price)
    if company:
        products = products.filter(Product.company.like('%' +company + '%'))
    if category:
        products = products.select_from(join(Product,
             Category)).filter(
                Category.name.like('%' + category + '%'))
    return render_template(
            'products.html', products=products.paginate(page, 10)
    )
