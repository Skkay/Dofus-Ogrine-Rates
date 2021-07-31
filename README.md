# Dofus - Ogrine Rates
Small web application to display the Ogrine rate from March 24, 2019 to present day.

Get the Ogrine rate from the official Dofus website (https://www.dofus.com/en/buy-kamas/rate-kama-ogrines) using a Python script, save it in a CSV file, then display a line graph using [Highcharts](https://github.com/highcharts/highcharts).

## Setup
Create `config.yaml` file with:
```yaml
csv_path: "rates.csv"
log_path: "log.txt"
webhooks:
    - "your Discord webhooks"
```
Adjust opened CSV file name in `index.html` as configured above.
