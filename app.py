#!/usr/bin/env python3
"""
Flask web server for OSHPark Random Board Picker
"""

from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import sys
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
    """Simple HTML interface"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSHPark Random Board Picker</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Monaco', 'Courier New', monospace;
            background: #191f2c;
            color: #d0d0d0;
            line-height: 1.6;
        }
        
        .container {
            max-width: 500px;
            margin: 100px auto;
            padding: 40px;
            background: #12171f;
            border: 1px solid #333;
            border-radius: 4px;
        }
        
        h1 {
            color: #ffffff;
            margin-bottom: 10px;
            font-size: 24px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        
        .subtitle {
            color: #888;
            font-size: 13px;
            margin-bottom: 30px;
        }
        
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #333;
            text-align: center;
            font-size: 12px;
        }
        
        .footer a {
            color: #4a9eff;
            text-decoration: none;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        
        .footer a:hover {
            color: #6bb3ff;
        }
        
        .github-icon {
            width: 16px;
            height: 16px;
            display: inline-block;
        }
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #b0b0b0;
            font-size: 12px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        input, select {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #333;
            background: #0f0f0f;
            color: #d0d0d0;
            border-radius: 3px;
            font-size: 13px;
            font-family: 'Monaco', 'Courier New', monospace;
            transition: border-color 0.2s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #555;
        }
        
        input::placeholder {
            color: #555;
        }
        
        button {
            width: 100%;
            padding: 11px 0;
            background: #2a2a2a;
            color: #d0d0d0;
            border: 1px solid #444;
            border-radius: 3px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            font-family: 'Monaco', 'Courier New', monospace;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            transition: all 0.2s;
        }
        
        button:hover {
            background: #333;
            border-color: #555;
            color: #ffffff;
        }
        
        button:active {
            background: #2a2a2a;
        }
        
        #result {
            margin-top: 30px;
            padding: 20px;
            background: #0f0f0f;
            border: 1px solid #333;
            display: none;
            border-radius: 3px;
        }
        
        #result.show {
            display: block;
        }
        
        #result.error {
            border-color: #555;
            background: #0f0f0f;
        }
        
        .board-title {
            font-size: 16px;
            color: #ffffff;
            margin-bottom: 12px;
            word-break: break-word;
        }
        
        .board-meta {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            font-size: 12px;
        }
        
        .board-price {
            color: #4a9eff;
            font-weight: 600;
        }
        
        .board-layers {
            color: #888;
        }
        
        .board-link {
            display: inline-block;
            color: #4a9eff;
            text-decoration: none;
            font-size: 12px;
            border: 1px solid #333;
            padding: 8px 12px;
            border-radius: 3px;
            transition: all 0.2s;
        }
        
        .board-link:hover {
            border-color: #4a9eff;
            color: #4a9eff;
        }
        
        .board-details {
            font-size: 12px;
            color: #888;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #333;
            line-height: 1.8;
        }
        
        .board-details-label {
            color: #b0b0b0;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: block;
            margin-top: 8px;
            margin-bottom: 2px;
        }
        
        .board-details-label:first-child {
            margin-top: 0;
        }
        
        .board-dimensions {
            color: #d0d0d0;
        }
        
        .board-description {
            color: #999;
            font-style: italic;
            margin-top: 8px;
        }
        
        .error-message {
            color: #ff6b6b;
            font-size: 13px;
        }
        
        .loading {
            display: none;
            color: #888;
            font-size: 12px;
            text-align: center;
        }
        
        @media (max-width: 640px) {
            .container {
                margin: 20px auto;
                padding: 20px;
            }
            
            h1 {
                font-size: 20px;
            }
            
            .board-meta {
                flex-direction: column;
                gap: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>OSH Picker</h1>
        <div class="subtitle">Random PCB finder</div>
        
        <form id="boardForm">
            <div class="form-group">
                <label for="keyword">Keyword <span style="color: #666;">(optional)</span>:</label>
                <input type="text" id="keyword" name="keyword" placeholder="esp32, stm32, arduino">
            </div>
            
            <div class="form-group">
                <label for="maxPrice">Max Price <span style="color: #666;">(optional)</span>:</label>
                <input type="number" id="maxPrice" name="maxPrice" placeholder="15.00" step="0.01" min="0">
            </div>
            
            <div class="form-group">
                <label for="layers">Layer Counts:</label>
                <select id="layers" name="layers">
                    <option value="2">2-layer (default)</option>
                    <option value="4">4-layer</option>
                    <option value="6">6-layer</option>
                    <option value="2 4">2 or 4 layer</option>
                    <option value="2 4 6">2, 4, or 6 layer</option>
                </select>
            </div>
            
            <button type="submit">Find Board</button>
        </form>
        
        <div class="loading" id="loading">
            searching...
        </div>
        
        <div id="result">
            <div class="board-title" id="boardTitle"></div>
            <div class="board-meta">
                <span class="board-price" id="boardPrice"></span>
                <span class="board-layers" id="boardLayers"></span>
            </div>
            <div id="boardDescriptionMain" style="display: none; margin: 12px 0; padding: 12px 0; border-top: 1px solid #333; border-bottom: 1px solid #333;">
                <span id="boardDescriptionText" style="color: #999; font-size: 12px; line-height: 1.6;"></span>
            </div>
            <div class="board-details" id="boardDetails" style="display: none;">
                <div id="dimensionsSection"></div>
            </div>
            <a id="boardLink" class="board-link" target="_blank">open on osh park</a>
        </div>
        
        <div class="footer">
            <a href="https://github.com/unixvoid/OSH_Picker" target="_blank">
                <svg class="github-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v 3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                view source on github
            </a>
        </div>
    </div>
    
    <script>
        document.getElementById('boardForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const keyword = document.getElementById('keyword').value || null;
            const maxPrice = document.getElementById('maxPrice').value || null;
            const layers = document.getElementById('layers').value || '2';
            
            // Build query string
            const params = new URLSearchParams();
            if (keyword) params.append('keyword', keyword);
            if (maxPrice) params.append('max_price', maxPrice);
            params.append('layers', layers);
            
            const resultDiv = document.getElementById('result');
            const loadingDiv = document.getElementById('loading');
            
            resultDiv.classList.remove('show', 'error');
            loadingDiv.style.display = 'block';
            
            try {
                const response = await fetch(`/osh-picker/api/board?${params.toString()}`);
                const data = await response.json();
                
                loadingDiv.style.display = 'none';
                
                if (data.success) {
                    document.getElementById('boardTitle').textContent = data.board.title;
                    document.getElementById('boardPrice').textContent = `$${data.board.price.toFixed(2)}`;
                    document.getElementById('boardLayers').textContent = `${data.board.layer_count}-layer`;
                    document.getElementById('boardLink').href = data.board.url;
                    
                    // Handle description - show prominently
                    const descriptionMain = document.getElementById('boardDescriptionMain');
                    const descriptionText = document.getElementById('boardDescriptionText');
                    if (data.board.description) {
                        descriptionText.textContent = data.board.description;
                        descriptionMain.style.display = 'block';
                    } else {
                        descriptionMain.style.display = 'none';
                    }
                    
                    // Handle dimensions
                    const dimensionsSection = document.getElementById('dimensionsSection');
                    if (data.board.dimensions) {
                        dimensionsSection.innerHTML = `
                            <span class="board-details-label">Size</span>
                            <span class="board-dimensions">${data.board.dimensions.inches} inches (${data.board.dimensions.mm} mm)</span>
                        `;
                    } else {
                        dimensionsSection.innerHTML = '';
                    }
                    
                    // Show details section if we have dimensions
                    const boardDetails = document.getElementById('boardDetails');
                    if (data.board.dimensions) {
                        boardDetails.style.display = 'block';
                    } else {
                        boardDetails.style.display = 'none';
                    }
                    
                    resultDiv.classList.add('show');
                } else {
                    document.getElementById('boardTitle').innerHTML = `<span class="error-message">error: ${data.error}</span>`;
                    resultDiv.classList.add('show', 'error');
                }
            } catch (error) {
                loadingDiv.style.display = 'none';
                document.getElementById('boardTitle').innerHTML = `<span class="error-message">error: ${error.message}</span>`;
                resultDiv.classList.add('show', 'error');
            }
        });
    </script>
</body>
</html>
    '''


if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
