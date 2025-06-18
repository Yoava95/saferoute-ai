# saferoute-ai
"AI agent that predicts travel risk in Israel during missile threats"

## Setup

Set the `ORS_API_KEY` environment variable with your OpenRouteService API key before running the script:

```bash
export ORS_API_KEY=your_api_key
python saferoute.py
```

## Rocket Alert Scraper

`scrape_rocketalert.py` collects rocket alert reports from
[rocketalert.live](https://rocketalert.live/). On first run it downloads all
available data starting from **12 June 2025** and saves it to
`missile_hits.json`. After the initial historical download, the scraper
updates the dataset twice a day (at **00:00** and **12:00** UTC). Install
required packages and start the scraper with:

```bash
pip install -r requirements.txt
python scrape_rocketalert.py
```

The risk assessment uses this dataset to consider nearby recent missile hits.
