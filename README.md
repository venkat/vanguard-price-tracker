# Vanguard Price Tracker

Automated price tracker for the **Vanguard Target Retirement 2070 Trust** fund. This project fetches daily NAV (Net Asset Value) data from Vanguard's API and publishes it as JSON for use with [Portfolio Performance](https://www.portfolio-performance.info/).

## Why This Exists

Vanguard Target Retirement Trust funds (used in 401k plans) don't have publicly available price feeds. This project works around that limitation by:

1. Fetching price data from Vanguard's internal API
2. Accumulating historical prices over time (the API only returns ~10 days)
3. Publishing the data as a JSON file accessible via GitHub Pages

## Output URL

The price data is published to:

```
https://venkat.io/vanguard-price-tracker/vanguard_target_2070_trust_prices.json
```

## Portfolio Performance Configuration

To import this data into Portfolio Performance:

1. Add a new security for the Vanguard Target Retirement 2070 Trust
2. Configure the historical quotes with:
   - **Feed Provider**: JSON
   - **URL**: `https://venkat.io/vanguard-price-tracker/vanguard_target_2070_trust_prices.json`
   - **Path to Date**: `$[*].asOfDate`
   - **Path to Close**: `$[*].netAssetValue`

## How It Works

### Automated Daily Updates

A GitHub Actions workflow (`.github/workflows/scheduled_fetch.yml`) runs daily at midnight UTC:

1. **Fetch**: Downloads raw JSONP data from Vanguard's API using `wget`
2. **Process**: Runs `fetch_2070_trust.py` to parse and merge new data
3. **Publish**: Commits the updated JSON file, which is served via GitHub Pages

### Data Processing (`fetch_2070_trust.py`)

The Python script:

1. Reads the raw JSONP response from `vanguard_raw.jsonp`
2. Extracts the JSON payload from the JSONP wrapper
3. Loads existing historical data from `vanguard_target_2070_trust_prices.json`
4. Merges new price entries, avoiding duplicates
5. Applies a 90-day rolling window (configurable via `ROLLING_WINDOW_DAYS`)
6. Saves the updated data

### Data Format

Each entry in the JSON output:

```json
{
  "asOfDate": "12/26/2025",
  "netAssetValue": "159.32",
  "change": null,
  "changePercentage": null
}
```

## Files

| File | Description |
|------|-------------|
| `fetch_2070_trust.py` | Main script that processes and merges price data |
| `vanguard_raw.jsonp` | Raw API response (kept for debugging) |
| `vanguard_target_2070_trust_prices.json` | Output file with historical prices |
| `.github/workflows/scheduled_fetch.yml` | GitHub Actions workflow for automation |
| `index.html` | Landing page for GitHub Pages |
| `_config.yml` | Jekyll configuration |

## Manual Execution

To run the price fetch manually:

```bash
# Fetch raw data
wget --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
     --referer="https://investor.vanguard.com/" \
     -O vanguard_raw.jsonp \
     "https://api.vanguard.com/rs/ire/01/pe/fund/M013/price/.jsonp?callback=angular.callbacks._2&planId=093926&portId=M013"

# Process the data
python fetch_2070_trust.py
```

You can also trigger the workflow manually from the GitHub Actions tab using "workflow_dispatch".

## Configuration

The rolling window size can be adjusted by changing `ROLLING_WINDOW_DAYS` in `fetch_2070_trust.py`:

```python
ROLLING_WINDOW_DAYS = 90  # Number of days of historical data to retain
```

## Concurrency Control

The workflow uses GitHub Actions' `concurrency` feature to prevent race conditions:

```yaml
concurrency:
  group: price-fetch
  cancel-in-progress: false
```

This ensures that if multiple runs are triggered (e.g., manual + scheduled), they execute sequentially rather than in parallel, preventing data loss from concurrent file writes.

## Limitations

- **API returns limited history**: Vanguard's API only provides ~10 days of historical data per request. This project accumulates data over time to build up a longer history.
- **No real-time data**: Prices are updated once daily.
- **Fund-specific**: Currently configured only for the 2070 Trust (fund ID: M013).
