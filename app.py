from flask import Flask, render_template, jsonify, request
import pandas as pd
from ip3_router import IP3Router
import socket
import logging
from threading import Thread
import time
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#  Aliases bellow
router = None
simulation_mode = True

DESTINATION_ALIASES = {

}


#
# Source and Destination Categories
#

SOURCE_CATEGORIES = {

}

DESTINATION_CATEGORIES = {
    
}

def categorize_with_mapping(items, category_map):
    """Categorize items based on custom mapping"""
    categories = {}
    uncategorized = []

    for category, category_items in category_map.items():
        categories[category] = []
        for item in items:
            if item in category_items:
                categories[category].append(item)
        categories[category].sort()

    categorized_items = [item for sublist in category_map.values() for item in sublist]
    uncategorized = [item for item in items if item not in categorized_items]

    if uncategorized:
        categories['Other'] = sorted(uncategorized)

    categories = {k: v for k, v in categories.items() if v}

    return dict(sorted(categories.items()))

def load_router_config():
    try:
        df = pd.read_csv('IP3_DB.csv')
        sources = df['Source'].dropna().tolist()
        destinations = df['Destination'].dropna().tolist()
        
        # Add alias destinations while keeping originals
        for alias in DESTINATION_ALIASES.keys():
            if DESTINATION_ALIASES[alias] in destinations:
                destinations.append(alias)
        
        grouped_sources = categorize_with_mapping(sources, SOURCE_CATEGORIES)
        grouped_destinations = categorize_with_mapping(destinations, DESTINATION_CATEGORIES)
        
        logger.info(f"Loaded and categorized router configuration")
        return grouped_sources, grouped_destinations
    except Exception as e:
        logger.error(f"Error loading router config: {str(e)}")
        return {}, {}
    

def try_router_connection():
    """Attempt to connect to the router"""
    global router, simulation_mode
    try:
        router = IP3Router('IP-ADDRESS')
        simulation_mode = False
        logger.info("Successfully connected to physical router")
        return True
    except Exception as e:
        logger.warning(f"Router connection failed: {str(e)}")
        router = RouterSimulator()
        return False

def initialize_router():
    """Initialize router connection"""
    global router
    if router is None:
        try_router_connection()


@app.route('/')
def index():
    grouped_sources, grouped_destinations = load_router_config()
    
    sources = []
    destinations = []
    
    for category_items in grouped_sources.values():
        sources.extend(category_items)
    
    for category_items in grouped_destinations.values():
        destinations.extend(category_items)
    
    sources = sorted(list(set(sources)))
    destinations = sorted(list(set(destinations)))
    
    return render_template('index.html',
                         sources=sources,
                         destinations=destinations,
                         source_categories=SOURCE_CATEGORIES.keys(),
                         destination_categories=DESTINATION_CATEGORIES.keys(),
                         source_to_categories={src: [cat for cat, items in SOURCE_CATEGORIES.items() if src in items] for src in sources},
                         destination_to_categories={dst: [cat for cat, items in DESTINATION_CATEGORIES.items() if dst in items] for dst in destinations},
                         simulation_mode=simulation_mode,
                         datetime=datetime)

@app.route('/route', methods=['POST'])
def make_route():
    if router is None:
        initialize_router()
    try:
        data = request.json
        source = data.get('source')
        destination = data.get('destination')
        
        if not source or not destination:
            return jsonify({
                'success': False, 
                'message': 'Source and destination required'
            })
        
        router_destination = DESTINATION_ALIASES.get(destination, destination)
        router_source = SOURCE_ALIASES.get(source, source)
        
        result = router.route(router_source, router_destination)
        
        if result == "locked":
            return jsonify({
                'success': False,
                'locked': True,
                'message': 'Destination is locked, contact Engineering',
                'simulation': simulation_mode
            })
        
        return jsonify({
            'success': True,
            'result': result,
            'simulation': simulation_mode
        })
            
    except Exception as e:
        logger.error(f"Error in route operation: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}',
            'simulation': simulation_mode
        })

@app.route('/status/<destination>')
def get_status(destination):
    if router is None:
        initialize_router()
    try:
        router_destination = DESTINATION_ALIASES.get(destination, destination)
        current_source = router.status(router_destination)
        
        return jsonify({
            'success': True if current_source else False,
            'source': current_source,
            'destination': destination,
            'simulation': simulation_mode
        })
    except Exception as e:
        logger.error(f"Error in status check: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e),
            'simulation': simulation_mode
        })

@app.route('/router_status')
def router_status():
    """Endpoint to check current router connection status"""
    if router is None:
        initialize_router()
    return jsonify({
        'simulation_mode': simulation_mode,
        'status': 'Simulated' if simulation_mode else 'Connected'
    })


if __name__ == '__main__':
    logger.info("Starting Flask server...")
    initialize_router()
    app.run(debug=True, host='0.0.0.0', port=5000)
