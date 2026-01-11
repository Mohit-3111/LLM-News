import ArticleCard from './ArticleCard';

export default function NewsGrid({ articles, title = 'Latest News' }) {
    if (!articles || articles.length === 0) {
        return (
            <section className="news-section">
                <div className="container">
                    <div className="news-header">
                        <h2 className="news-title">{title}</h2>
                    </div>

                    <div style={{
                        textAlign: 'center',
                        padding: 'var(--space-16) 0',
                        color: 'var(--text-secondary)'
                    }}>
                        <svg
                            width="64"
                            height="64"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1.5"
                            style={{ margin: '0 auto var(--space-4)', opacity: 0.5 }}
                        >
                            <path d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                        </svg>
                        <p>No articles available at the moment.</p>
                        <p style={{ fontSize: '0.875rem', marginTop: 'var(--space-2)' }}>
                            Check back soon for the latest AI news!
                        </p>
                    </div>
                </div>
            </section>
        );
    }

    return (
        <section className="news-section">
            <div className="container">
                <div className="news-header">
                    <h2 className="news-title">{title}</h2>
                </div>

                <div className="news-grid stagger-animation">
                    {articles.map((article) => (
                        <ArticleCard key={article._id} article={article} />
                    ))}
                </div>
            </div>
        </section>
    );
}
