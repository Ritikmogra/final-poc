from flask import Blueprint,request,jsonify
from models import db, Admin, Product, Category,User1
from user_routes import token_required


admin_blueprint = Blueprint('admin',__name__)


@admin_blueprint.route('/admin/login', methods=['POST'])
def login_admin():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    admin = Admin.query.filter_by(username=username, password=password).first()
    if not admin:
        return jsonify({'error': 'Invalid username or password'}), 401
    return jsonify({'message': 'Admin logged in successfully'}), 200




@admin_blueprint.route('/admin/dashboard', methods=['GET'])
def dashboard():
    total_users_count = User1.query.count()
    total_products_count = Product.query.count()

    dashboard_data = {
        'total_users': total_users_count,
        'total_products': total_products_count,
    }
    return jsonify(dashboard_data), 200


@admin_blueprint.route('/admin/products', methods=['POST'])
def add_product():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    if not name or not price:
        return jsonify({'error': 'Name and price are required'}), 400
    new_product = Product(name=name, description=description, price=price)
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product added successfully'}), 201



@admin_blueprint.route('/admin/products', methods=['GET'])
def list_products():

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    sort_by = request.args.get('sort_by', 'id')  
    sort_order = request.args.get('sort_order', 'asc') 

    search_term = request.args.get('search_term', '')

    products_query = Product.query.filter(Product.name.ilike(f'%{search_term}%'))

    if sort_order == 'asc':
        products_query = products_query.order_by(sort_by)
    else:
        products_query = products_query.order_by(db.desc(sort_by))

    paginated_products = products_query.paginate(page=page, per_page=per_page, error_out=False)

    products = []
    for product in paginated_products.items:
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price
        }
        products.append(product_data)

    
    return jsonify({
        'products': products,
        'total_products': paginated_products.total,
        'current_page': paginated_products.page,
        'total_pages': paginated_products.pages
    }), 200


@admin_blueprint.route('/admin/categories', methods=['POST'])
def add_category():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    new_category = Category(name=name, description=description)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'message': 'Category added successfully'}), 201


@admin_blueprint.route('/admin/categories', methods=['GET'])
@token_required
def list_categories():
    categories = Category.query.all()
    category_list = []
    for category in categories:
        category_data = {
            'id': category.id,
            'name': category.name,
            'description': category.description
        }
        category_list.append(category_data) 
    return jsonify(category_list), 200


@admin_blueprint.route('/admin/categories/<int:id>', methods=['PUT'])
def update_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    data = request.json
    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    
    db.session.commit()
    
    return jsonify({'message': 'Category updated successfully'}), 200