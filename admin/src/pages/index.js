import { useState, useEffect } from 'react';
import Head from 'next/head';

// Configurable website URL - change this to your deployed website
const WEBSITE_URL = 'https://llm-news-nu.vercel.app';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  // Fetch stats
  const fetchStats = async () => {
    try {
      const res = await fetch('/api/stats');
      const data = await res.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  // Fetch articles
  const fetchArticles = async (statusFilter = 'all') => {
    try {
      const url = statusFilter === 'all'
        ? '/api/articles?limit=20'
        : `/api/articles?limit=20&status=${statusFilter}`;
      const res = await fetch(url);
      const data = await res.json();
      setArticles(data.articles || []);
    } catch (error) {
      console.error('Failed to fetch articles:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchStats(), fetchArticles()]);
      setLoading(false);
    };
    loadData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchStats();
      fetchArticles(filter);
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleFilterChange = (newFilter) => {
    setFilter(newFilter);
    fetchArticles(newFilter);
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  // Get article link based on status
  const getArticleLink = (article) => {
    // Processed/published articles go to our website
    if (article.status === 'processed' || article.status === 'published') {
      return `${WEBSITE_URL}/article/${article._id}`;
    }
    // All other statuses (filtered, raw, curated, error) go to original source
    return article.url;
  };

  // Get link label for tooltip
  const getLinkLabel = (article) => {
    if (article.status === 'processed' || article.status === 'published') {
      return 'View on LLM News';
    }
    return 'View original source';
  };

  return (
    <>
      <Head>
        <title>Admin Dashboard | LLM News</title>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet" />
      </Head>

      <div className="dashboard">
        {/* Header */}
        <header className="dashboard-header">
          <h1 className="dashboard-title">
            <span>🛠️</span> Admin Dashboard
          </h1>
          <a href={WEBSITE_URL} className="back-link" target="_blank" rel="noopener">
            ← Back to Website
          </a>
        </header>

        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            Loading dashboard...
          </div>
        ) : (
          <>
            {/* Stats Grid */}
            <div className="stats-grid">
              <div className="stat-card total">
                <div className="stat-label">Total Articles</div>
                <div className="stat-value">{stats?.total || 0}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Raw</div>
                <div className="stat-value">{stats?.articles?.raw || 0}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Curated</div>
                <div className="stat-value">{stats?.articles?.curated || 0}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Processed</div>
                <div className="stat-value">{stats?.articles?.processed || 0}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Filtered</div>
                <div className="stat-value">{stats?.articles?.filtered || 0}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Errors</div>
                <div className="stat-value">{stats?.articles?.error || 0}</div>
              </div>
            </div>

            {/* Articles Section */}
            <div className="section">
              <div className="section-header">
                <h2 className="section-title">
                  <span>📰</span> Recent Articles
                </h2>
                <div className="filter-tabs">
                  {['all', 'raw', 'curated', 'processed', 'filtered', 'error'].map(status => (
                    <button
                      key={status}
                      className={`filter-tab ${filter === status ? 'active' : ''}`}
                      onClick={() => handleFilterChange(status)}
                    >
                      {status.charAt(0).toUpperCase() + status.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              <div className="table-wrapper">
                <table className="articles-table">
                  <thead>
                    <tr>
                      <th>Title</th>
                      <th>Status</th>
                      <th>Source</th>
                      <th>Images</th>
                      <th>Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {articles.length === 0 ? (
                      <tr>
                        <td colSpan="5" style={{ textAlign: 'center', padding: '2rem' }}>
                          No articles found
                        </td>
                      </tr>
                    ) : (
                      articles.map(article => (
                        <tr key={article._id}>
                          <td className="article-title-cell">
                            <a
                              href={getArticleLink(article)}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="article-title"
                              title={`${article.title}\n\n${getLinkLabel(article)}`}
                            >
                              {article.title}
                              {(article.status === 'processed' || article.status === 'published') && (
                                <span className="link-badge">🔗</span>
                              )}
                            </a>
                          </td>
                          <td>
                            <span className={`status-badge ${article.status}`}>
                              {article.status}
                            </span>
                          </td>
                          <td>{article.source || '-'}</td>
                          <td>
                            <span className={`image-indicator ${article.hasImages ? 'has-images' : 'no-images'}`}>
                              {article.hasImages ? '✓ Yes' : '✗ No'}
                            </span>
                          </td>
                          <td>{formatDate(article.createdAt)}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              <div className="last-updated">
                Last updated: {formatDate(stats?.lastUpdated)}
                {' • '}
                Auto-refreshes every 30s
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );
}
