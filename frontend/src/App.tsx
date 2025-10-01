import React, { useState, useEffect } from 'react';
import Autocomplete from './components/Autocomplete';
import './App.css';

interface HealthStatus {
  status: string;
  opensearch: {
    connected: boolean;
  };
  redis?: {
    connected: boolean;
  };
}

function App() {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const response = await fetch('/api/v1/health');
      if (response.ok) {
        const data = await response.json();
        setHealthStatus(data);
        setHealthError(null);
      } else {
        setHealthError('Backend service is not responding');
      }
    } catch (err) {
      setHealthError('Cannot connect to backend service');
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>ChatBI 智能补全演示</h1>
        <p className="subtitle">Intelligent Autocomplete with Hybrid Search</p>
        {healthStatus && (
          <div className="health-status">
            <span className={`status-indicator ${healthStatus.status === 'healthy' ? 'healthy' : 'unhealthy'}`}>
              ●
            </span>
            <span>Backend: {healthStatus.status}</span>
            {healthStatus.opensearch && (
              <span className="service-status">
                OpenSearch: {healthStatus.opensearch.connected ? '✓' : '✗'}
              </span>
            )}
            {healthStatus.redis && (
              <span className="service-status">
                Redis: {healthStatus.redis.connected ? '✓' : '✗'}
              </span>
            )}
          </div>
        )}
        {healthError && (
          <div className="health-error">
            ⚠️ {healthError}
          </div>
        )}
      </header>

      <main className="app-main">
        <div className="demo-container">
          <div className="demo-section">
            <h2>搜索演示</h2>
            <p className="description">
              输入查询内容，体验基于关键词、向量和用户个性化的混合搜索自动补全功能。
              支持中英文混合输入。
            </p>
            <Autocomplete />
          </div>

          <div className="features-section">
            <h3>功能特点</h3>
            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon">🔍</div>
                <h4>混合搜索</h4>
                <p>结合关键词匹配和语义向量搜索，提供更精准的建议</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">🌏</div>
                <h4>中英文支持</h4>
                <p>完整支持中英文混合输入和搜索</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">👤</div>
                <h4>个性化推荐</h4>
                <p>基于用户历史行为提供个性化建议</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">⚡</div>
                <h4>实时响应</h4>
                <p>快速响应，300ms 防抖优化</p>
              </div>
            </div>
          </div>

          <div className="examples-section">
            <h3>试试这些查询</h3>
            <div className="example-queries">
              <button className="example-query" onClick={() => document.querySelector<HTMLInputElement>('.search-input')!.value = '销售'}>
                销售
              </button>
              <button className="example-query" onClick={() => document.querySelector<HTMLInputElement>('.search-input')!.value = '客户'}>
                客户
              </button>
              <button className="example-query" onClick={() => document.querySelector<HTMLInputElement>('.search-input')!.value = '市场'}>
                市场
              </button>
              <button className="example-query" onClick={() => document.querySelector<HTMLInputElement>('.search-input')!.value = '业绩'}>
                业绩
              </button>
              <button className="example-query" onClick={() => document.querySelector<HTMLInputElement>('.search-input')!.value = 'revenue'}>
                revenue
              </button>
            </div>
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <p>Powered by FastAPI + React + TypeScript</p>
        <p>
          <a href="/docs" target="_blank" rel="noopener noreferrer">API 文档</a>
          {' | '}
          <a href="https://github.com/whoishu/aibi" target="_blank" rel="noopener noreferrer">GitHub</a>
        </p>
      </footer>
    </div>
  );
}

export default App;
