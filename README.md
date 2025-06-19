# saferoute-ai
"AI agent that predicts travel risk in Israel during missile threats"

## Setup

Set the `ORS_API_KEY` environment variable with your OpenRouteService API key before running the script:

```bash
export ORS_API_KEY=your_api_key
python saferoute.py
```

## Missile Hit Scraper

`scrape_rocketalert.py` collects rocket alert reports from
[rocketalert.live](https://rocketalert.live/). The dataset is stored in
`missile_hits.json` and automatically updated once per day. On the first
run it downloads all available history starting 12 June 2024; subsequent runs
only fetch new alerts. Install required packages and start the scraper with:

```bash
pip install -r requirements.txt
python scrape_rocketalert.py
```

The risk assessment uses this dataset to consider nearby recent missile hits.
