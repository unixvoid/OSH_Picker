# OSHPark Random Board Picker

A Python script that scrapes [OSHPark's shared projects](https://oshpark.com/shared_projects/) and returns a random PCB design matching your criteria.

**Try it live**: Visit [bitnuke.io/osh-picker/](https://bitnuke.io/osh-picker/) to use the web interface!

## Features

- Pick a random PCB design from OSHPark
- Filter by keyword (e.g., `esp32`, `stm32`, `arduino`)
- Filter by maximum price (3-board pricing)
- Filter by layer; 2, 4, and/or 6 layers supported

## Installation

### Requirements
- Python 3.7+
- `requests` library

### Setup

```bash
pip install requests
```

## Usage

### Basic Usage

```bash
python3 random_board.py
```

Returns a random 2-layer board with its price and OSHPark link.

### Examples

```bash
# Random 2-layer board
python3 random_board.py

# Random board under $5
python3 random_board.py --max-price 5

# Find a random ESP32 board
python3 random_board.py --keyword esp32

# ESP32 board under $12
python3 random_board.py --keyword esp32 --max-price 12

# Include 2, 4, and 6 layer boards
python3 random_board.py --layers 2 4 6

# Verbose output to see what's happening
python3 random_board.py --keyword esp32 -v
```

## Command-Line Options

```
--keyword TEXT          Search keyword (e.g., esp32, stm32, arduino)
--max-price FLOAT       Maximum price for 3-board option (in dollars)
--per-page INT          Results per page from OSHPark (default: 100)
--layers INT [INT ...]  PCB layer counts to include (default: 2)
                        Can specify multiple: --layers 2 4 6
-v, --verbose           Print status messages during execution
-h, --help              Show help message
```

## Output

The script prints the randomly selected board in the following format:

```
Random Board: Board <PROJECT_ID>
URL: https://oshpark.com/shared_projects/<PROJECT_ID>
3-Board Price: $<PRICE>
```

### Example Output

```
Random Board: Board LFLycZxZ
URL: https://oshpark.com/shared_projects/LFLycZxZ
3-Board Price: $2.35
```

## How It Works

1. **Check Sitemap Cache**: Looks for a cached sitemap (updated every 30 minutes)
2. **Fetch/Parse Project List**: Uses cached sitemap if available, otherwise fetches from OSHPark
3. **Filter by Keyword** (optional): Narrows the project pool using title/description matching
4. **Random Selection Loop**: Randomly picks projects from the pool and checks each one until finding a match
5. **Apply Filters**: Validates that the board meets all criteria:
   - Layer count
   - Price (if max-price specified)
6. **Return Match**: Returns the first board that matches all filters

## About Keyword Searching

OSHPark's search is fully client-side (JavaScript) - the server doesn't filter results. This script works around that by:
- Using cached sitemap metadata (title/description) for fast keyword filtering
- Only fetching individual project pages for boards that might match
- The cache keeps keyword searches instant after the first run

## Performance Notes

- The script fetches the full project pool once (instant)
- Then randomly samples projects until finding a match
- Each project check requires fetching one webpage (~40-50KB)
- Typically finds a match within 5-15 requests for common filters

## Caching

The script automatically caches the sitemap to `.sitemap_cache/sitemap.json`. The cache is considered fresh for 30 minutes.

- **First run**: Fetches sitemap from OSHPark and saves to cache
- **Subsequent runs (within 30 minutes)**: Uses cached sitemap (skips network request entirely)
- **After 30 minutes**: Automatically refreshes the cache with fresh data from OSHPark

This dramatically reduces query load and improves performance for repeated runs.

## Limitations

- Only searches 2-layer boards by default (can be changed with --layers flag)
- Project titles are dynamically loaded in the browser, so they show as project IDs
- Scraping is rate-limited by network speed, not the site
- Keyword searching requires filtering the sitemap metadata, which is instant but limited to title/description only

## Troubleshooting

**"No boards found matching your criteria"**
- Try removing or adjusting your `--max-price` filter
- Try removing your `--keyword` filter to search the entire pool
- Check that your layer count preference (`--layers`) isn't too restrictive

**Script runs slowly**
- This is expected if you're using tight filters (specific keyword + low price)
- Loosen your filters to find matches faster
- Use `-v` flag to see what the script is checking

## License

This is a personal project for scraping publicly available OSHPark designs. Use responsibly and be respectful of the OSHPark service.

## Notes

- This script is not affiliated with OSHPark
- Respects OSHPark's robots.txt and doesn't hammer their servers
- Designed for personal use and learning