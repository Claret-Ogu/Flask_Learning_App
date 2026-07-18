from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app import db
from app.models import Item
from app.forms import ItemForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page"""
    items_count = Item.query.count()
    return render_template('index.html', items_count=items_count)

@main_bp.route('/items')
def list_items():
    """List all items with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = 5
    
    # Paginate items
    pagination = Item.query.order_by(Item.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    items = pagination.items
    
    return render_template('items.html', items=items, pagination=pagination)

@main_bp.route('/items/add', methods=['GET', 'POST'])
def add_item():
    """Add a new item"""
    form = ItemForm()
    
    if form.validate_on_submit():
        # Create new item
        item = Item(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(item)
        db.session.commit()
        
        flash(f'Item "{item.name}" created successfully!', 'success')
        return redirect(url_for('main.list_items'))
    
    return render_template('add_item.html', form=form)

@main_bp.route('/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_item(item_id):
    """Handle individual item operations (RESTful)"""
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'GET':
        # Get single item
        return render_template('item_detail.html', item=item)
    
    elif request.method == 'PUT':
        # Update item (API endpoint)
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        item.name = data.get('name', item.name)
        item.description = data.get('description', item.description)
        db.session.commit()
        
        return jsonify({
            'message': 'Item updated successfully',
            'item': item.to_dict()
        }), 200
    
    elif request.method == 'DELETE':
        # Delete item (API endpoint)
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({
            'message': f'Item "{item.name}" deleted successfully'
        }), 200

@main_bp.route('/api/items')
def api_items():
    """RESTful API endpoint for all items"""
    items = Item.query.all()
    return jsonify([item.to_dict() for item in items])

@main_bp.route('/api/items/<int:item_id>')
def api_item_detail(item_id):
    """RESTful API endpoint for single item"""
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())

# Error handlers
@main_bp.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@main_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500