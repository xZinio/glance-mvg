# 🚇 MVG Departure Widget

![MVG](https://img.shields.io/badge/MVG-München-blue?style=for-the-badge&logo=metro) ![Status](https://img.shields.io/badge/Status-Live-green?style=for-the-badge)

A real-time public transport departure board for your personal dashboard. It pulls live data directly from the Munich Transport Corporation (MVG) API to show upcoming U-Bahn, Tram, and Bus departures for your chosen station.

## ✨ Features

* **Live Data:** Shows real-time departure times (in minutes).
* **Transport Icons:** visual indicators for U-Bahn, Tram, and Bus.
* **Smart Coloring:** Color-coded lines (e.g., U1, U2) matching the official MVG system.
* **Collapsible List:** Automatically hides later departures to keep your dashboard clean.

## 🛠️ Prerequisites

You do not need an API key for this widget, but you **do** need the unique **Global ID** for the station you want to monitor.

### How to find your Station ID
The easiest way to find a Station ID is to query the MVG "Locations" endpoint directly in your browser.

1.  Open your web browser.
2.  Paste the following URL, replacing `STATION_NAME` with your stop (e.g., `Marienplatz` or `Hauptbahnhof`):
    `https://www.mvg.de/api/fib/v2/location?query=STATION_NAME`
3.  Look for the `"globalId"` in the search results (it usually starts with `de:09...`).

> **Example:** Marienplatz is `de:09162:2`.


## 🛠️ Setup Guide

This setup uses a small **Python Backend** (intermediary) to fetch data from MVG. This prevents CORS issues and allows for better data formatting before it reaches your dashboard.

---

### 1. Project Structure
Create a folder named `mvg-widget` and set up the following structure:

```text
mvg-widget/
├── app.py
├── requirements.txt
├── Dockerfile
└── compose.yaml
```
Put this folder inside of your already existing Glance docker compose directory (the one in which your `compose.yaml` is located in).

### 2. Compose
Add this to your glance `compose.yaml`:
```yml
services:
  mvg-api:
    build: .
    container_name: mvg-api
    restart: unless-stopped
    ports:
      - "5000:5000"
```
Lastly, run `docker-compose up -d --build` in the same directoy.

### Glance widget

Add the following block to your dashboard configuration file (e.g., `glance.yml`) and adjust it to your liking.

```yaml
- type: custom-api
  title: Departures - Marienplatz
  cache: 30s
  # Replace 'de:09162:2' with your own Station Global ID
  url: [https://www.mvg.de/api/fib/v2/departure?globalId=de:09162:2&limit=10&transportTypes=UBAHN,TRAM,BUS,SBAHN](https://www.mvg.de/api/fib/v2/departure?globalId=de:09162:2&limit=10&transportTypes=UBAHN,TRAM,BUS,SBAHN)
  template: |
    <ul class="list list-gap-10 collapsible-container" data-collapse-after="5">
      {{ range .JSON.Array }}
        <li class="flex gap-10 items-center">
          <span class="badge" 
                style="min-width: 3rem; text-align: center; 
                background-color: {{ if eq .product "UBAHN" }}#005293{{ else if eq .product "TRAM" }}#D82020{{ else if eq .product "BUS" }}#005851{{ else }}#444{{ end }}; 
                color: #fff;">
            {{ .label }}
          </span>
          <div class="flex-grow">
            {{ .destination }}
          </div>
          <div class="color-subdue">
            {{ .timeDiff }} min
          </div>
        </li>
      {{ else }}
        <p class="color-negative">No departures found.</p>
      {{ end }}
    </ul>
```
## LICENSE