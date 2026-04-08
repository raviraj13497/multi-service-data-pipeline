import os
import json
import logging
from flask import Flask, jsonify, request

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'customers.json')

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Data file not found at {DATA_FILE}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON at {DATA_FILE}")
        return []

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

@app.route('/api/customers', methods=['GET'])
def get_customers():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    if page < 1 or limit < 1:
        return jsonify({"error": "Page and limit must be positive integers"}), 400

    data = load_data()
    total = len(data)
    
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    paginated_data = data[start_idx:end_idx]
    
    return jsonify({
        "data": paginated_data,
        "total": total,
        "page": page,
        "limit": limit
    })

@app.route('/api/customers/<string:customer_id>', methods=['GET'])
def get_customer(customer_id):
    data = load_data()
    for customer in data:
        if customer['customer_id'] == customer_id:
            return jsonify(customer)
    return jsonify({"error": "Customer not found"}), 404

if __name__ == '__main__':
    logger.info("Starting Mock Server...")
    # Serve using app.run because we just need a simple mock. But typically handled implicitly by debug/dev setups.
    app.run(host='0.0.0.0', port=5000)
