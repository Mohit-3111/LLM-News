import Link from 'next/link';

export default function HeroSection({ featuredArticle }) {
    if (!featuredArticle) {
        return (
            <section className="hero">
                <div className="container">
                    <div className="hero-badge animate-fade-in">
                        <span className="hero-badge-dot" />
                        <span>Live AI News Updates</span>
                    </div>

                    <h1 className="hero-title animate-fade-in-up">
                        Your Daily Dose of{' '}
                        <span className="text-gradient">AI & LLM News</span>
                    </h1>

                    <p className="hero-subtitle animate-fade-in-up">
                        Stay ahead of the curve with curated news about artificial intelligence,
                        large language models, and the future of technology.
                    </p>
                </div>
            </section>
        );
    }

    const {
        _id,
        title,
        source,
        publishedAt,
        curated,
        platforms,
        images,
    } = featuredArticle;

    const summary = platforms?.website?.summary || curated?.summary || '';

    // Get the image URL - prefer ImgBB cloud URL, fallback to local path
    const imageUrl = images?.website?.url || null;
    const imagePath = images?.website?.path || null;
    const imageSrc = imageUrl || (imagePath ? (imagePath.startsWith('/') ? imagePath : `/${imagePath}`) : null);

    const sourceName = source?.name || source || 'Unknown Source';

    const displayDate = publishedAt
        ? new Date(publishedAt).toLocaleDateString('en-US', {
            month: 'long',
            day: 'numeric',
            year: 'numeric',
        })
        : '';

    return (
        <section className="hero">
            <div className="container">
                <div className="hero-badge animate-fade-in">
                    <span className="hero-badge-dot" />
                    <span>Live AI News Updates</span>
                </div>

                <h1 className="hero-title animate-fade-in-up">
                    Your Daily Dose of{' '}
                    <span className="text-gradient">AI & LLM News</span>
                </h1>

                <p className="hero-subtitle animate-fade-in-up">
                    Stay ahead of the curve with curated news about artificial intelligence,
                    large language models, and the future of technology.
                </p>

                <div className="hero-featured animate-fade-in-up">
                    <Link href={`/article/${_id}`} className="hero-featured-image glass-card">
                        {imageSrc ? (
                            <img
                                src={imageSrc}
                                alt={title || 'Featured article'}
                                style={{
                                    width: '100%',
                                    height: '100%',
                                    objectFit: 'cover'
                                }}
                            />
                        ) : (
                            <div className="article-card-image-placeholder" style={{
                                aspectRatio: '16/10',
                                background: 'var(--accent-gradient)',
                                opacity: 0.3
                            }} />
                        )}
                        <div className="hero-featured-overlay">
                            <span className="badge">{sourceName}</span>
                        </div>
                    </Link>

                    <div className="hero-featured-content">
                        <span className="badge mb-4">Featured</span>
                        <h2 className="hero-featured-title">
                            <Link href={`/article/${_id}`}>{title}</Link>
                        </h2>
                        {summary && (
                            <p className="hero-featured-summary">{summary}</p>
                        )}
                        <div style={{ display: 'flex', gap: 'var(--space-4)', alignItems: 'center' }}>
                            <Link href={`/article/${_id}`} className="btn btn-primary">
                                Read Article
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M5 12h14M12 5l7 7-7 7" />
                                </svg>
                            </Link>
                            {displayDate && (
                                <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                    {displayDate}
                                </span>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
