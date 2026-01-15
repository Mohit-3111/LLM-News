import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend
);

// Configurable website URL
const WEBSITE_URL = 'https://llm-news-nu.vercel.app';

export default function AnalyticsDashboard() {
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [days, setDays] = useState(7);

    const fetchAnalytics = async () => {
        try {
            const res = await fetch(`/api/analytics?days=${days}`);
            const data = await res.json();
            setAnalytics(data);
        } catch (error) {
            console.error('Failed to fetch analytics:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAnalytics();
        // Auto-refresh every 60 seconds
        const interval = setInterval(fetchAnalytics, 60000);
        return () => clearInterval(interval);
    }, [days]);

    // Chart colors
    const chartColors = {
        primary: 'rgba(99, 102, 241, 0.8)',
        secondary: 'rgba(139, 92, 246, 0.8)',
        tertiary: 'rgba(167, 139, 250, 0.8)',
        success: 'rgba(34, 197, 94, 0.8)',
        warning: 'rgba(245, 158, 11, 0.8)',
        info: 'rgba(59, 130, 246, 0.8)',
    };

    const pieColors = [
        chartColors.primary,
        chartColors.secondary,
        chartColors.tertiary,
        chartColors.success,
        chartColors.warning,
        chartColors.info,
        'rgba(236, 72, 153, 0.8)',
        'rgba(20, 184, 166, 0.8)',
        'rgba(251, 146, 60, 0.8)',
        'rgba(148, 163, 184, 0.8)',
    ];

    // Bar chart data
    const barChartData = {
        labels: analytics?.dailyViews?.map(d => {
            const date = new Date(d.date);
            return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
        }) || [],
        datasets: [
            {
                label: 'Page Views',
                data: analytics?.dailyViews?.map(d => d.views) || [],
                backgroundColor: chartColors.primary,
                borderColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 1,
                borderRadius: 6,
            },
        ],
    };

    const barChartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: 'rgba(26, 26, 36, 0.95)',
                titleColor: '#f8fafc',
                bodyColor: '#94a3b8',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                padding: 12,
                cornerRadius: 8,
            },
        },
        scales: {
            x: {
                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                ticks: { color: '#64748b' },
            },
            y: {
                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                ticks: { color: '#64748b' },
                beginAtZero: true,
            },
        },
    };

    // Doughnut chart data
    const doughnutData = {
        labels: analytics?.viewsBySource?.map(s => s.source) || [],
        datasets: [
            {
                data: analytics?.viewsBySource?.map(s => s.count) || [],
                backgroundColor: pieColors,
                borderColor: '#1a1a24',
                borderWidth: 2,
            },
        ],
    };

    const doughnutOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    color: '#94a3b8',
                    padding: 12,
                    usePointStyle: true,
                    pointStyle: 'circle',
                },
            },
            tooltip: {
                backgroundColor: 'rgba(26, 26, 36, 0.95)',
                titleColor: '#f8fafc',
                bodyColor: '#94a3b8',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                padding: 12,
                cornerRadius: 8,
            },
        },
    };

    return (
        <>
            <Head>
                <title>Analytics | Admin Dashboard</title>
                <link rel="preconnect" href="https://fonts.googleapis.com" />
                <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet" />
            </Head>

            <div className="dashboard">
                {/* Header */}
                <header className="dashboard-header">
                    <h1 className="dashboard-title">
                        <span>📊</span> Analytics Dashboard
                    </h1>
                    <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                        <select
                            value={days}
                            onChange={(e) => setDays(parseInt(e.target.value))}
                            className="range-select"
                        >
                            <option value={7}>Last 7 days</option>
                            <option value={14}>Last 14 days</option>
                            <option value={30}>Last 30 days</option>
                            <option value={90}>Last 90 days</option>
                        </select>
                        <Link href="/" className="back-link">
                            ← Back to Dashboard
                        </Link>
                    </div>
                </header>

                {loading ? (
                    <div className="loading">
                        <div className="spinner"></div>
                        Loading analytics...
                    </div>
                ) : (
                    <>
                        {/* Stats Grid */}
                        <div className="stats-grid">
                            <div className="stat-card total">
                                <div className="stat-label">Total Views</div>
                                <div className="stat-value">{analytics?.totalViews?.toLocaleString() || 0}</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-label">Today</div>
                                <div className="stat-value">{analytics?.todayViews?.toLocaleString() || 0}</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-label">Last {days} Days</div>
                                <div className="stat-value">{analytics?.recentViews?.toLocaleString() || 0}</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-label">Articles Viewed</div>
                                <div className="stat-value">{analytics?.uniqueArticlesViewed || 0}</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-label">Avg/Day</div>
                                <div className="stat-value">{analytics?.avgDailyViews || 0}</div>
                            </div>
                        </div>

                        {/* Charts Row */}
                        <div className="charts-row">
                            {/* Bar Chart */}
                            <div className="section chart-section">
                                <div className="section-header">
                                    <h2 className="section-title">
                                        <span>📈</span> Page Views Over Time
                                    </h2>
                                </div>
                                <div className="chart-container">
                                    {analytics?.dailyViews?.length > 0 ? (
                                        <Bar data={barChartData} options={barChartOptions} />
                                    ) : (
                                        <div className="no-data">No data yet. Views will appear as users visit your site.</div>
                                    )}
                                </div>
                            </div>

                            {/* Doughnut Chart */}
                            <div className="section chart-section-small">
                                <div className="section-header">
                                    <h2 className="section-title">
                                        <span>📰</span> Views by Source
                                    </h2>
                                </div>
                                <div className="chart-container-small">
                                    {analytics?.viewsBySource?.length > 0 ? (
                                        <Doughnut data={doughnutData} options={doughnutOptions} />
                                    ) : (
                                        <div className="no-data">No source data yet.</div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Top Articles */}
                        <div className="section">
                            <div className="section-header">
                                <h2 className="section-title">
                                    <span>🏆</span> Top Articles
                                </h2>
                            </div>
                            <div className="table-wrapper">
                                <table className="articles-table">
                                    <thead>
                                        <tr>
                                            <th style={{ width: '50px' }}>#</th>
                                            <th>Article</th>
                                            <th>Source</th>
                                            <th style={{ width: '100px' }}>Views</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {analytics?.topArticles?.length > 0 ? (
                                            analytics.topArticles.map((article, index) => (
                                                <tr key={article._id || index}>
                                                    <td>
                                                        <span className={`rank-badge rank-${index + 1}`}>
                                                            {index + 1}
                                                        </span>
                                                    </td>
                                                    <td className="article-title-cell">
                                                        {article._id ? (
                                                            <a
                                                                href={`${WEBSITE_URL}/article/${article._id}`}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="article-title"
                                                            >
                                                                {article.title}
                                                            </a>
                                                        ) : (
                                                            <span className="article-title">{article.title}</span>
                                                        )}
                                                    </td>
                                                    <td>{article.source || '-'}</td>
                                                    <td>
                                                        <span className="views-count">{article.views}</span>
                                                    </td>
                                                </tr>
                                            ))
                                        ) : (
                                            <tr>
                                                <td colSpan="4" style={{ textAlign: 'center', padding: '2rem' }}>
                                                    No article views yet
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <div className="last-updated">
                            Last updated: {analytics?.generatedAt ? new Date(analytics.generatedAt).toLocaleString() : '-'}
                            {' • '}
                            Auto-refreshes every 60s
                        </div>
                    </>
                )}
            </div>

            <style jsx>{`
                .charts-row {
                    display: grid;
                    grid-template-columns: 2fr 1fr;
                    gap: 1.5rem;
                    margin-bottom: 1.5rem;
                }

                .chart-section {
                    min-height: 350px;
                }

                .chart-section-small {
                    min-height: 350px;
                }

                .chart-container {
                    height: 280px;
                    padding: 1rem 1.25rem;
                }

                .chart-container-small {
                    height: 280px;
                    padding: 1rem;
                }

                .no-data {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100%;
                    color: var(--text-muted);
                    font-size: 0.875rem;
                }

                .range-select {
                    padding: 0.5rem 1rem;
                    background: var(--bg-card);
                    border: 1px solid var(--border-color);
                    border-radius: 0.5rem;
                    color: var(--text-primary);
                    font-size: 0.875rem;
                    cursor: pointer;
                    outline: none;
                }

                .range-select:hover {
                    border-color: var(--border-color-hover);
                }

                .range-select:focus {
                    border-color: var(--accent-primary);
                }

                .rank-badge {
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    width: 28px;
                    height: 28px;
                    border-radius: 50%;
                    font-size: 0.75rem;
                    font-weight: 600;
                    background: var(--bg-card-hover);
                    color: var(--text-secondary);
                }

                .rank-badge.rank-1 {
                    background: linear-gradient(135deg, #ffd700, #ffb300);
                    color: #000;
                }

                .rank-badge.rank-2 {
                    background: linear-gradient(135deg, #c0c0c0, #a0a0a0);
                    color: #000;
                }

                .rank-badge.rank-3 {
                    background: linear-gradient(135deg, #cd7f32, #a0522d);
                    color: #fff;
                }

                .views-count {
                    display: inline-flex;
                    align-items: center;
                    gap: 0.25rem;
                    padding: 0.25rem 0.625rem;
                    background: rgba(99, 102, 241, 0.15);
                    color: var(--accent-tertiary);
                    border-radius: 9999px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    font-family: var(--font-mono);
                }

                @media (max-width: 1024px) {
                    .charts-row {
                        grid-template-columns: 1fr;
                    }
                }

                @media (max-width: 768px) {
                    .chart-container,
                    .chart-container-small {
                        height: 220px;
                    }
                }
            `}</style>
        </>
    );
}
