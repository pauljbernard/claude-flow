# React Dashboard How-To Guide

This guide explains how to run the React-based dashboard included with Claude Flow and outlines the available features.

## Prerequisites

- Node.js 18 or later
- The API server running from the repository root
- Optional: set `VITE_API_BASE_URL` in `frontend-react/.env` if the API runs on a different host/port

## Starting the Servers

1. **Backend** – from the repository root:
   ```bash
   npm install
   npm run dev    # API server at http://localhost:3000
   ```
2. **Frontend** – in another terminal:
   ```bash
   cd frontend-react
   npm install
   npm run dev    # React dev server at http://localhost:5173
   ```
3. Open `http://localhost:5173` in your browser.

## Interface Overview

The dashboard contains four main tabs:

| Tab       | Purpose                                          |
|-----------|--------------------------------------------------|
| **Metrics** | View performance charts and request live metrics |
| **Reports** | Run reporting tools such as cost analysis        |
| **Analysis** | Launch analysis tools like bottleneck scans     |
| **Health** | Monitor system health metrics and load graphs    |

Select a tab at the top of the page to view its tools.

### Metrics Tab

- **Performance Report** – fetch a summary of recent performance
- **Token Usage** – display token consumption
- **Collect Metrics** – gather the latest metrics snapshot
- **Usage Stats** – retrieve usage statistics
- **Historical Metrics** – view saved metric history
- **Request Metrics** – triggers a WebSocket request to stream updates to the charts in real time

Charts include response time history and a token usage doughnut chart.

### Reports Tab

- **Performance Report** – same report accessible from the Metrics tab
- **Cost Analysis** – estimate cost based on token usage
- **Quality Assess** – run quality evaluation checks
- **Benchmark Run** – execute built-in benchmarks

Each button sends a request to the API and shows the JSON result below the charts.

### Analysis Tab

- **Bottleneck Analysis** – analyze performance bottlenecks
- **Trend Analysis** – inspect long term trends
- **Error Analysis** – review error patterns
- **Capacity Plan** – generate a capacity planning report

Results appear under the tool list in formatted JSON.

### Health Tab

- **Health Check** – perform a full system health check
- **Load Monitor** – show current system load statistics

This tab displays a radar chart for health metrics and a line chart for system load.

## Building for Production

To create a production bundle:
```bash
cd frontend-react
npm run build
```
The static files will be placed in `dist/`.

## Summary

Use the dashboard to run analysis tools, view live metrics, and monitor system health. Tabs organize the tools by category, and results are displayed in real time with WebSocket updates for metrics.
