# saferoute-ai
"AI agent that predicts travel risk in Israel during missile threats"

## Requirements

* Python 3
* [`requests`](https://pypi.org/project/requests/)

Install the dependency with:

```bash
pip install requests
```

## API Key

`saferoute.py` calls the OpenRouteService API and needs an API key. The
script reads the key from the `ORS_API_KEY` environment variable. Set it
before running the script:

```bash
export ORS_API_KEY=your-api-key-here
```

Alternatively, you can edit the `ORS_API_KEY` constant in `saferoute.py`.

## Usage

Run the script with:

```bash
python saferoute.py
```
