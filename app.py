#!/usr/bin/env python3
"""
Flask web server for OSHPark Random Board Picker

The web UI lives in index.html (a fully static, client-side app that can also
be hosted on GitHub Pages). This server keeps the JSON API available and serves
the same index.html for local development.
"""

from flask import Flask, request, jsonify, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
from random_board import OSHParkScraper

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)


@app.route('/osh-picker/api/board', methods=['GET'])
def get_board():
    """
    Get a random board matching the specified criteria
    
    Query parameters:
        keyword: Search keyword (optional)
        max_price: Maximum price (optional)
        layers: Layer counts (space or comma separated, optional)
        verbose: Enable verbose logging (optional)
    
    Returns:
        JSON with board details or error message
    """
    try:
        # Parse query parameters
        keyword = request.args.get('keyword', None)
        max_price = request.args.get('max_price', type=float, default=None)
        layers_str = request.args.get('layers', None)
        verbose = request.args.get('verbose', 'false').lower() == 'true'
        
        # Parse layers - support both space and comma separated
        layers = None
        if layers_str:
            # Handle both "2 4 6" and "2,4,6"
            layers = [int(x.strip()) for x in layers_str.replace(',', ' ').split()]
        
        # Create scraper with specified criteria
        scraper = OSHParkScraper(
            keyword=keyword,
            max_price=max_price,
            layers=layers,
            verbose=verbose
        )
        
        # Get random board
        board = scraper.get_random_board()
        
        if board:
            return jsonify({
                'success': True,
                'board': {
                    'title': board['title'],
                    'url': board['url'],
                    'price': board['price'],
                    'project_id': board['project_id'],
                    'layer_count': board['layer_count'],
                    'dimensions': board.get('dimensions'),
                    'description': board.get('description')
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No boards found matching your criteria'
            }), 404
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/osh-picker/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200


@app.route('/osh-picker/', methods=['GET'])
def index():
    """Serve the static frontend (shared with the GitHub Pages build)"""
    return send_from_directory(app.root_path, 'index.html')


if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
