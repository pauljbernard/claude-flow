import React, { useEffect, useRef, useState } from 'react';
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  DoughnutController,
  ArcElement,
  RadarController,
  RadialLinearScale,
} from 'chart.js';

Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  DoughnutController,
  ArcElement,
  RadarController,
  RadialLinearScale,
);

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';
const endpointMap: Record<string, string> = {
  performance_report: `${API_BASE}/api/analysis/performance-report`,
  bottleneck_analyze: `${API_BASE}/api/analysis/bottleneck-analyze`,
  token_usage: `${API_BASE}/api/analysis/token-usage`,
  benchmark_run: `${API_BASE}/api/analysis/benchmark-run`,
  metrics_collect: `${API_BASE}/api/analysis/metrics-collect`,
  trend_analysis: `${API_BASE}/api/analysis/trend-analysis`,
  cost_analysis: `${API_BASE}/api/analysis/cost-analysis`,
  quality_assess: `${API_BASE}/api/analysis/quality-assess`,
  error_analysis: `${API_BASE}/api/analysis/error-analysis`,
  usage_stats: `${API_BASE}/api/analysis/usage-stats`,
  health_check: `${API_BASE}/api/analysis/health-check`,
  load_monitor: `${API_BASE}/api/analysis/load-monitor`,
  capacity_plan: `${API_BASE}/api/analysis/capacity-plan`,
  historical_metrics: `${API_BASE}/api/analysis/historical-metrics`,
};

const tabs = ['metrics', 'reports', 'analysis', 'health'] as const;

type Tab = (typeof tabs)[number];

const toolGroups: Record<Tab, { id: string; label: string }[]> = {
  metrics: [
    { id: 'performance_report', label: 'Performance Report' },
    { id: 'token_usage', label: 'Token Usage' },
    { id: 'metrics_collect', label: 'Collect Metrics' },
    { id: 'usage_stats', label: 'Usage Stats' },
    { id: 'historical_metrics', label: 'Historical Metrics' },
  ],
  reports: [
    { id: 'performance_report', label: 'Performance Report' },
    { id: 'cost_analysis', label: 'Cost Analysis' },
    { id: 'quality_assess', label: 'Quality Assess' },
    { id: 'benchmark_run', label: 'Benchmark Run' },
  ],
  analysis: [
    { id: 'bottleneck_analyze', label: 'Bottleneck Analysis' },
    { id: 'trend_analysis', label: 'Trend Analysis' },
    { id: 'error_analysis', label: 'Error Analysis' },
    { id: 'capacity_plan', label: 'Capacity Plan' },
  ],
  health: [
    { id: 'health_check', label: 'Health Check' },
    { id: 'load_monitor', label: 'Load Monitor' },
  ],
};

interface ResultMap {
  [key: string]: any;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('metrics');
  const [results, setResults] = useState<ResultMap>({});
  const perfChartRef = useRef<HTMLCanvasElement>(null);
  const tokenChartRef = useRef<HTMLCanvasElement>(null);
  const healthChartRef = useRef<HTMLCanvasElement>(null);
  const loadChartRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const perfCtx = perfChartRef.current?.getContext('2d');
    const tokenCtx = tokenChartRef.current?.getContext('2d');
    const healthCtx = healthChartRef.current?.getContext('2d');
    const loadCtx = loadChartRef.current?.getContext('2d');

    let perfChart: Chart | undefined;
    let tokenChart: Chart | undefined;
    let healthChart: Chart | undefined;
    let loadChart: Chart | undefined;

    if (perfCtx) {
      perfChart = new Chart(perfCtx, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Response Time', data: [] }] },
      });
    }
    if (tokenCtx) {
      tokenChart = new Chart(tokenCtx, {
        type: 'doughnut',
        data: {
          labels: ['Input', 'Output', 'Cached'],
          datasets: [{ data: [0, 0, 0] }],
        },
      });
    }
    if (healthCtx) {
      healthChart = new Chart(healthCtx, {
        type: 'radar',
        data: { labels: ['CPU', 'Memory', 'Disk', 'Network', 'API', 'DB'], datasets: [{ data: [100, 100, 100, 100, 100, 100] }] },
        options: { scales: { r: { beginAtZero: true, max: 100 } } },
      });
    }
    if (loadCtx) {
      loadChart = new Chart(loadCtx, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Load', data: [] }] },
      });
    }

    const wsBase = API_BASE
      ? API_BASE.replace(/^http/, location.protocol === 'https:' ? 'wss' : 'ws')
      : `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}`;
    const ws = new WebSocket(`${wsBase}/api/analysis/ws`);
    wsRef.current = ws;
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'metrics_update') {
        const { performance, tokens, health, load } = data.payload;
        if (perfChart) {
          const labels = perfChart.data.labels as string[];
          labels.push('');
          (perfChart.data.datasets[0].data as number[]).push(performance.responseTime);
          if (labels.length > 20) {
            labels.shift();
            (perfChart.data.datasets[0].data as number[]).shift();
          }
          perfChart.update();
        }
        if (tokenChart) {
          tokenChart.data.datasets[0].data = [tokens.inputTokens, tokens.outputTokens, tokens.cachedTokens];
          tokenChart.update();
        }
        if (healthChart) {
          healthChart.data.datasets[0].data = Object.values(health);
          healthChart.update();
        }
        if (loadChart) {
          const labels = loadChart.data.labels as string[];
          labels.push('');
          (loadChart.data.datasets[0].data as number[]).push(load.current);
          if (labels.length > 20) {
            labels.shift();
            (loadChart.data.datasets[0].data as number[]).shift();
          }
          loadChart.update();
        }
      }
    };

    return () => {
      ws.close();
      perfChart?.destroy();
      tokenChart?.destroy();
      healthChart?.destroy();
      loadChart?.destroy();
    };
  }, []);

  const runTool = async (id: string) => {
    const endpoint = endpointMap[id];
    try {
      const res = await fetch(endpoint);
      const json = await res.json();
      setResults((r) => ({ ...r, [id]: json }));
    } catch (err) {
      setResults((r) => ({ ...r, [id]: { error: String(err) } }));
    }
  };

  const requestMetrics = () => {
    wsRef.current?.send(JSON.stringify({ type: 'request_metrics' }));
  };

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: 20 }}>
      <h1>Claude Flow Analysis Tools</h1>
      <nav style={{ marginBottom: 20 }}>
        {tabs.map((tab) => (
          <button
            key={tab}
            style={{ marginRight: 8, fontWeight: activeTab === tab ? 'bold' : 'normal' }}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </nav>

      <section>
        {toolGroups[activeTab].map((tool) => (
          <button key={tool.id} style={{ marginRight: 8, marginBottom: 8 }} onClick={() => runTool(tool.id)}>
            {tool.label}
          </button>
        ))}
      </section>

      <div style={{ marginTop: 20 }}>
        {activeTab === 'metrics' && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 20 }}>
            <canvas ref={perfChartRef} width={300} height={200}></canvas>
            <canvas ref={tokenChartRef} width={200} height={200}></canvas>
            <button onClick={requestMetrics}>Request Metrics</button>
          </div>
        )}
        {activeTab === 'health' && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 20 }}>
            <canvas ref={healthChartRef} width={250} height={250}></canvas>
            <canvas ref={loadChartRef} width={300} height={200}></canvas>
          </div>
        )}
      </div>

      <div style={{ marginTop: 20 }}>
        {toolGroups[activeTab].map((tool) => (
          <div key={tool.id} style={{ marginBottom: 20 }}>
            <h3>{tool.label} Result</h3>
            <pre style={{ background: '#f0f0f0', padding: 10 }}>
              {JSON.stringify(results[tool.id], null, 2) || 'No data'}
            </pre>
          </div>
        ))}
      </div>
    </div>
  );
}
