#!/usr/bin/env python3
"""
OSHPark Random Board Picker
Scrapes OSHPark shared projects and returns a random board design
matching specified criteria (keyword, price, layer count)
"""

import requests
import random
import argparse
import re
import sys
import time
import os
import json
from urllib.parse import urljoin


class OSHParkScraper:
    """Scrapes OSHPark shared projects and filters by criteria"""
    
    BASE_URL = "https://oshpark.com/shared_projects"
    CACHE_DIR = ".sitemap_cache"
    CACHE_FILE = os.path.join(CACHE_DIR, "sitemap.json")
    CACHE_TTL = 30 * 60  # 30 minutes in seconds
    
    def __init__(self, keyword=None, max_price=None, records_per_page=100, layers=None, verbose=False):
        """
        Initialize scraper with filtering criteria
        
        Args:
            keyword: Search term for board designs (optional)
            max_price: Maximum price for 3-board option (optional)
            records_per_page: Number of results per page (default 100)
            layers: List of layer counts to include (default [2])
            verbose: Print status messages (optional)
        """
        self.keyword = keyword
        self.max_price = max_price
        self.records_per_page = records_per_page
        self.layers = layers if layers else [2]  # Default to 2-layer only
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def _log(self, message):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(message, file=sys.stderr)
    
    def _is_cache_valid(self):
        """Check if sitemap cache exists and is less than 30 minutes old"""
        if not os.path.exists(self.CACHE_FILE):
            return False
        
        file_age = time.time() - os.path.getmtime(self.CACHE_FILE)
        return file_age < self.CACHE_TTL
    
    def _load_cache(self):
        """Load projects from cache file"""
        try:
            with open(self.CACHE_FILE, 'r') as f:
                data = json.load(f)
                self._log(f"Loaded sitemap from cache ({len(data)} projects)")
                return data
        except (IOError, json.JSONDecodeError) as e:
            self._log(f"Error loading cache: {e}")
            return None
    
    def _save_cache(self, projects):
        """Save projects to cache file"""
        try:
            os.makedirs(self.CACHE_DIR, exist_ok=True)
            with open(self.CACHE_FILE, 'w') as f:
                json.dump(projects, f)
                self._log(f"Saved sitemap to cache ({len(projects)} projects)")
        except IOError as e:
            self._log(f"Error saving cache: {e}")
    
    def get_project_ids(self):
        """Fetch and search the sitemap for all matching projects"""
        # Try to load from cache first
        if self._is_cache_valid():
            projects = self._load_cache()
        else:
            # Fetch from OSHPark
            try:
                self._log(f"Fetching sitemap from OSHPark...")
                response = self.session.get(self.BASE_URL, timeout=15)
                response.raise_for_status()
            except requests.RequestException as e:
                self._log(f"Error fetching sitemap: {e}")
                return []
            
            # Parse the sitemap to extract projects with their titles and descriptions
            projects = self._parse_sitemap(response.text)
            self._log(f"Parsed {len(projects)} total projects from sitemap")
            
            # Save to cache
            self._save_cache(projects)
        
        # Filter by keyword if specified
        if self.keyword:
            keyword_lower = self.keyword.lower()
            projects = [p for p in projects if 
                       keyword_lower in (p['title'] or '').lower() or
                       keyword_lower in (p['description'] or '').lower()]
            self._log(f"Found {len(projects)} projects matching keyword '{self.keyword}'")
        
        # Extract project IDs (use entire pool)
        project_ids = [p['id'] for p in projects]
        
        self._log(f"Using pool of {len(project_ids)} projects")
        return project_ids
    
    def _parse_sitemap(self, html_content):
        """Parse the sitemap to extract project metadata"""
        projects = []
        
        # Split by <url> tags to process each project
        url_blocks = html_content.split('<url>')
        
        for block in url_blocks[1:]:  # Skip the first empty split
            # Extract project ID
            loc_match = re.search(r'<loc>https://oshpark\.com/shared_projects/([a-zA-Z0-9]+)</loc>', block)
            if not loc_match:
                continue
            
            project_id = loc_match.group(1)
            
            # Extract title
            title_match = re.search(r'<Attribute name="title">([^<]+)</Attribute>', block)
            title = title_match.group(1) if title_match else None
            
            # Extract description
            desc_match = re.search(r'<Attribute name="description">([^<]*)</Attribute>', block)
            description = desc_match.group(1) if desc_match else None
            
            projects.append({
                'id': project_id,
                'title': title,
                'description': description
            })
        
        return projects
    
    def fetch_project_details(self, project_id):
        """Fetch detailed information for a specific project"""
        url = f"{self.BASE_URL}/{project_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            self._log(f"Error fetching project {project_id}: {e}")
            return None
        
        return self.parse_project_page(response.text, project_id, url)
    
    def parse_project_page(self, html_content, project_id, project_url):
        """Parse individual project page to extract pricing and details"""
        try:
            title = "Unknown Board"
            price = None
            layer_count = None
            
            # Find layer count (must match one of the allowed layers)
            layer_pattern = r'(\d+)\s*layer\s*board'
            layer_match = re.search(layer_pattern, html_content, re.IGNORECASE)
            if layer_match:
                layer_count = int(layer_match.group(1))
                if layer_count not in self.layers:
                    self._log(f"  {project_id}: {layer_count}-layer board, but only {self.layers} supported, skipping")
                    return None  # Skip boards with unsupported layer counts
            else:
                self._log(f"  {project_id}: Could not determine layer count, skipping")
                return None
            
            # Find price - look for "Total Price" followed by a dollar amount
            # The HTML might have tags between them, so look for the pattern more broadly
            price_pattern = r'Total Price.*?\$\s*([\d.]+)'
            price_match = re.search(price_pattern, html_content, re.DOTALL)
            if price_match:
                try:
                    price = float(price_match.group(1))
                except ValueError:
                    price = None
            
            # Extract title from <title> tag
            title_match = re.search(r'<title>OSH Park ~ ([^<]*)</title>', html_content)
            if title_match:
                title = title_match.group(1).strip()
                if not title:
                    title = f"Board {project_id}"
            
            # If we couldn't find a price, skip this board
            if price is None:
                self._log(f"  {project_id}: No price found, skipping")
                return None
            
            # Apply price filter
            if self.max_price is not None and price > self.max_price:
                self._log(f"  {project_id}: Price ${price:.2f} exceeds max ${self.max_price:.2f}, skipping")
                return None
            
            self._log(f"  {project_id}: Found '{title}' - ${price:.2f}")
            
            return {
                'title': title,
                'url': project_url,
                'price': price,
                'project_id': project_id,
                'layer_count': layer_count
            }
        
        except Exception as e:
            self._log(f"Error parsing project {project_id}: {e}")
            return None
    
    def get_random_board(self):
        """Pick random projects from the pool until finding one matching criteria"""
        # Get list of all available project IDs
        project_ids = self.get_project_ids()
        
        if not project_ids:
            self._log("No projects found matching your search criteria.")
            return None
        
        # Shuffle to randomize order
        shuffled_ids = project_ids.copy()
        random.shuffle(shuffled_ids)
        
        self._log(f"Checking random projects from pool of {len(project_ids)}...")
        
        # Try each random project until we find one that meets criteria
        for project_id in shuffled_ids:
            self._log(f"Checking project: {project_id}")
            board_data = self.fetch_project_details(project_id)
            if board_data:
                self._log(f"Found matching board: {board_data['title']}")
                return board_data
        
        # If we exhausted the pool without finding a match
        self._log("No boards found matching your criteria after checking all available projects.")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Pick a random PCB design from OSHPark (2-layer boards only)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s                                 # Random 2-layer board
  %(prog)s --keyword esp32                 # Random ESP32 board
  %(prog)s --keyword esp32 --max-price 12  # Random ESP32 under $12 (3-board price)
  %(prog)s --max-price 5                   # Random board under $5
  %(prog)s --keyword stm32 -v              # Verbose output
  %(prog)s --layers 2 4 6                  # Include 2, 4, or 6 layer boards
  %(prog)s --keyword esp32 --layers 4 6    # ESP32 boards with 4 or 6 layers
        '''
    )
    
    parser.add_argument(
        '--keyword',
        help='Search keyword (e.g., esp32, stm32, arduino)'
    )
    parser.add_argument(
        '--max-price',
        type=float,
        help='Maximum price for 3-board option (in dollars)'
    )
    parser.add_argument(
        '--per-page',
        type=int,
        default=100,
        help='Number of results per page (default: 100)'
    )
    parser.add_argument(
        '--layers',
        type=int,
        nargs='+',
        default=[2],
        help='PCB layer counts to include (default: 2). Can specify multiple: --layers 2 4 6'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print status messages'
    )
    
    args = parser.parse_args()
    
    scraper = OSHParkScraper(
        keyword=args.keyword,
        max_price=args.max_price,
        records_per_page=args.per_page,
        layers=args.layers,
        verbose=args.verbose
    )
    
    board = scraper.get_random_board()
    
    if board:
        print(f"\nRandom Board: {board['title']}")
        print(f"URL: {board['url']}")
        print(f"3-Board Price: ${board['price']:.2f}")
        print()
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()