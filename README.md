# OSHPark Random Board Picker

A Python script that scrapes [OSHPark's shared projects](https://oshpark.com/shared_projects/) and returns a random PCB design matching your criteria.

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

**Get a random board under $5:**
```bash
python3 random_board.py --max-price 5
```

**Find a random ESP32 board:**
```bash
python3 random_board.py --keyword esp32
```

**Find an affordable ESP32 board (under $12):**
```bash
python3 random_board.py --keyword esp32 --max-price 12
```

**Search for 4-layer boards:**
```bash
python3 random_board.py --layers 4
```

**Include multiple layer counts (2, 4, or 6 layers):**
```bash
python3 random_board.py --layers 2 4 6
```

**Find ESP32 boards with 4 or 6 layers:**
```bash
python3 random_board.py --keyword esp32 --layers 4 6
```

**Search for STM32 boards, checking up to 200 projects:**
```bash
python3 random_board.py --keyword stm32 --max-projects 200
```

**See what the script is doing (verbose mode):**
```bash
python3 random_board.py --keyword esp32 -v
```

**Combine all options:**
```bash
python3 random_board.py --keyword "Arduino" --max-price 15 --layers 2 4 --max-projects 200 --verbose
```

## Command-Line Options

```
--keyword TEXT          Search keyword (e.g., esp32, stm32, arduino)
--max-price FLOAT       Maximum price for 3-board option (in dollars)
--max-projects INT      Maximum number of projects to check (default: 200)
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

1. **Get Project List**: Fetches the OSHPark shared projects page (which contains a sitemap of all ~26k projects)
2. **Extract Project IDs**: Uses regex to find all project IDs from the response
3. **Limit Results**: Takes only the first N projects (configurable, default 200) to keep search fast
4. **Fetch Details**: Downloads each project page to extract:
   - Price (3-board cost)
   - Layer count
   - Page content (for keyword matching)
5. **Apply Filters**: Filters out boards that don't match your criteria:
   - Layer count
   - Price (if max-price specified)
   - Keyword (if keyword specified - searches page content)
6. **Pick Random**: Selects a random board from the matches

## About Keyword Searching

OSHPark's search is fully client-side (JavaScript) - the server doesn't filter results. This script works around that by:
- Fetching individual project pages
- Searching the page content for your keyword
- Since keywords are sparse, you may need to increase `--max-projects` to find matches

For example, ESP32 boards appear in roughly 1 per 100 projects, so you might need `--max-projects 300` or higher.

## Performance Notes

- Each project requires fetching a separate webpage (~40-50KB)
- Default `--max-projects 200` will take ~30-60 seconds depending on your connection
- OSHPark has ~26,000+ shared projects total
- Use `--max-projects` to control how thorough the search is:
  - **50**: ~15-20 seconds (quick, good for repeated runs)
  - **200**: ~30-60 seconds (default, good balance)
  - **500+**: ~2+ minutes (very thorough)

## Limitations

- Only searches 2-layer boards by default (can be changed with --layers flag)
- Project titles are dynamically loaded in the browser, so they show as project IDs
- Scraping is rate-limited by network speed, not the site
- Keyword searching requires filtering the sitemap metadata, which is instant but limited to title/description only

## Troubleshooting

**"No boards found matching your criteria"**
- Try increasing `--max-projects` to search more boards
- Try removing or changing your `--max-price` filter
- Try removing your `--keyword` filter

**Script runs slowly**
- This is expected - each project page must be fetched individually
- Try using a smaller `--max-projects` value for faster results
- For quick tests, use `--max-projects 50`

## License

This is a personal project for scraping publicly available OSHPark designs. Use responsibly and be respectful of the OSHPark service.

## Notes

- This script is not affiliated with OSHPark
- Respects OSHPark's robots.txt and doesn't hammer their servers
- Designed for personal use and learning