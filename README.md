# Einführung

In diesem Projekt im Rahmen des Moduls Web Mining untersuchen wir die Preisentwicklung von Last-Minute-Flügen und analysieren, welche Parameter diese beeinflussen. Dabei extrahieren wir Flugdaten von verschiedenen Fluggesellschaften und führen Analysen durch, um Muster und Abhängigkeiten zu erkennen. Zusätzlich haben wir externe Einflussfaktoren wie Wetterdaten und Aktienkurse der Fluggesellschaften gecrawlt, um deren potenziellen Einfluss auf die Flugpreise zu analysieren. Die zentrale Fragestellung besteht darin, herauszufinden, welche Faktoren die Preisentwicklung von Last-Minute-Flügen bestimmen.
# Projektstruktur

Dieses Projekt ist in vier Hauptordner unterteilt, die spezifische Aufgaben erfüllen:

- Der Ordner flight-crawlers enthält die Skripte zum Web-Crawling von Flugdaten und speichert die dabei gewonnenen Ergebnisse sowie Logs.
- Der Ordner weather-stock-crawlers umfasst die Erfassung und Speicherung von Wetter- und Börsendaten für die Fluggesellschaften und Reiseziele.
- Im Ordner data-preparation werden die Rohdaten aus verschiedenen Quellen zusammengeführt und für die Analyse aufbereitet.
- Im Ordner analysis werden die finalen Analysen der Flugdaten durchgeführt.

## Ordnerübersicht

[**flight-crawlers**](./flight-crawlers)

[logs:](./flight-crawlers/logs) Enthält die Logs für die Crawling-Prozesse der Fluggesellschaften.
- logging_AustrianAirlines.csv
- logging_KLM.csv
- logging_QatarAirways.csv

[results:](./flight-crawlers/results) Enthält die gesammelten Flugdaten.
- results_AustrianAirlines.csv
- results_KLM.csv
- results_QatarAirways.csv
- austrian_airlines_crawler.py: Python-Skript zum Crawlen der Austrian Airlines Webseite.
- klm_crawler.py: Python-Skript zum Crawlen der KLM Webseite.
- qatar_airways_crawler.py: Python-Skript zum Crawlen der Qatar Airways Webseite.
- base_crawler.py: Grundgerüst für die Crawler-Skripte.

[**weather-stock-crawlers**](./weather-stock-crawler)

[weather:](./weather-stock-crawler/weather) Enthält Wetterdaten zu den analysierten Flugzielen.
- Berlin_weather.csv, Frankfurt_weather.csv, etc.: Wetterdaten für verschiedene Städte.
- combined_weather.csv: Kombinierte Wetterdaten für die analysierten Ziele.
- weather_stock_crawler.ipynb: Notebook, das den Crawling-Prozess für Wetter- und Börsendaten beschreibt.

[stocks:](./weather-stock-crawler/stocks) Enthält Börsendaten der Fluggesellschaften.
- combined_stocks.csv: Kombinierte Börsendaten der analysierten Fluggesellschaften.
- KLM_stock_data.csv, Lufthansa_stock_data.csv, Turkish_stock_data.csv: Einzelne Börsendaten.

[**data-preparation**](./data-preparation)

- merge_flight_data.ipynb: Jupyter Notebook für die Datenaufbereitung, in dem die verschiedenen Flugdaten zusammengeführt werden.
- merge_all_crawling_data.ipynb: Jupyter Notebook, das alle Crawler-Daten in eine kombinierte Datei zusammenführt.

[**analysis**](./analysis)

- analysis_dataset.csv: Datensatz für die finale Analyse.
- analysis.ipynb: Jupyter Notebook für die Analyse der Flugdaten und deren Einflussfaktoren.

## Notwendige Installationen

Um sicherzustellen, dass alle benötigten Bibliotheken für das Projekt installiert sind, führe folgende Befehle in deiner Python-Umgebung aus:

```bash
# Grundlegende Bibliotheken für Datenverarbeitung und Analyse
pip install pandas numpy matplotlib seaborn

# Web Crawling und Parsing
pip install selenium beautifulsoup4

# Wetterdaten und Finanzdaten
pip install meteostat yfinance

# Maschinelles Lernen
pip install scikit-learn

# Statistische Bibliotheken
pip install scipy scikit-posthocs statsmodels

# Zusätzliche Bibliotheken (falls noch nicht installiert)
pip install logging itertools
