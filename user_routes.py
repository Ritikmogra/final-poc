from flask import Blueprint,request,jsonify
from models import db,User1,Product,CartItem
import bcrypt
import jwt
from functools import wraps
from abc_1 import app

user_blueprint = Blueprint('user', __name__)  


app.config["SECRET_KEY"] = 'your_secret_key_here'


def token_required(f):
    @wraps (f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token is missing"}), 403
        try:
            token=token.split(" ") [1]
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token is invalid"}), 403

    return decorated



def role_required(rid):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"error": "Token is missing"}), 403

            try:
                token = token.split(" ")[1]
                payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
                user_id = payload["rid"]
                user = user.query.get(rid)
                if user.role != rid:
                    return jsonify({"error": "Insufficient permissions to access this resource"}), 403
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token has expired"}), 403
            except (jwt.InvalidTokenError, KeyError):
                return jsonify({"error": "Token is invalid"}), 403

        return decorated

    return decorator



@user_blueprint.route('/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')  
    if not username or not email or not password or not role: 
        return jsonify({'error': 'Username, email, password, and role are required'}), 400
    existing_user = User1.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 400
    existing_email = User1.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({'error': 'Email already exists'}), 400
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User1(username=username, email=email, password_hash=password_hash, role=role) 
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201



@user_blueprint.route('/user/login', methods=['POST'])
def login_user():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'email and password are required'}), 400
    user = User1.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    if bcrypt.checkpw(password.encode('utf-8'),user.password_hash.encode('utf-8')):
        token_payload = {'user_id': user.id}
        token = jwt.encode(token_payload, app.config["SECRET_KEY"], algorithm='HS256')
        return jsonify({'message':'Login Successfully' ,'token': token}), 200
    else:
        return jsonify({'error':'Invalid email or password'}),401




@user_blueprint.route('/user/shop', methods=['GET'])
@token_required
def shop():
    products = Product.query.all()
    product_list = []
    for product in products:
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price
        }
        product_list.append(product_data)
    return jsonify(product_list), 200




@user_blueprint.route('/user/product/<int:id>', methods=['GET'])
@token_required
def product_detail(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    product_data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price
    }
    return jsonify(product_data), 200 




@user_blueprint.route('/user/cart', methods=['GET'])
@token_required
def view_cart():
    user1_id = request.args.get('user_id')
    if not user1_id:
        return jsonify({'error': 'User ID is required to view the cart'}), 400
    cart_items = CartItem.query.filter_by(user1_id=user1_id).all()
    cart_data = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product:
            cart_data.append({
                'product_id': item.product_id,
                'name': product.name,
                'price': product.price,
                'quantity': item.quantity
            })
    return jsonify(cart_data), 200





@user_blueprint.route('/user/cart/add', methods=['POST'])
@token_required
def add_to_cart():
    data = request.json
    user1_id = data.get('user1_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not user1_id or not product_id:
        return jsonify({'error': 'User ID and Product ID are required to add to cart'}), 400
    
    existing_item = CartItem.query.filter_by(user1_id=user1_id, product_id=product_id).first()
    if existing_item:
        existing_item.quantity += quantity
    else:
        new_item = CartItem(user1_id=user1_id, product_id=product_id, quantity=quantity)
        db.session.add(new_item)
    
    db.session.commit()
    
    return jsonify({'message': 'Item added to cart successfully'}), 201




@user_blueprint.route('/user/cart/remove', methods=['POST'])
@token_required
def remove_from_cart():
    data = request.json
    user1_id = data.get('user1_id')
    product_id = data.get('product_id')
    
    if not user1_id or not product_id:
        return jsonify({'error': 'User1 ID and Product ID are required to remove from cart'}), 400
    
    item_to_remove = CartItem.query.filter_by(user1_id=user1_id, product_id=product_id).first()
    if item_to_remove:
        db.session.delete(item_to_remove)
        db.session.commit()
        return jsonify({'message': 'Item removed from cart successfully'}), 200
    else:
        return jsonify({'error': 'Item not found in cart'}), 404