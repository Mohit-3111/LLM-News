import Link from 'next/link';

/**
 * Format a date for display.
 */
function formatDate(dateString) {
    if (!dateString) return '';

    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffHours < 1) {
        return 'Just now';
    } else if (diffHours < 24) {
        return `${diffHours}h ago`;
    } else if (diffDays < 7) {
        return `${diffDays}d ago`;
    } else {
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
        });
    }
}

export default function ArticleCard({ article }) {
    const {
        _id,
        title,
        source,
        publishedAt,
        createdAt,
        curated,
        platforms,
        images,
    } = article;

    // Get the summary from platform-specific content or fallback to curated summary
    const summary = platforms?.website?.summary || curated?.summary || '';

    // Get hashtags from curated content
    const hashtags = curated?.hashtags?.slice(0, 3) || [];

    // Get the image path - use website image if available
    const imagePath = images?.website?.path || null;

    // Format the source name
    const sourceName = source?.name || source || 'Unknown Source';

    // Get the display date
    const displayDate = formatDate(publishedAt || createdAt);

    return (
        <article className="glass-card article-card">
            <Link href={`/article/${_id}`} className="article-card-image">
                {imagePath ? (
                    <img
                        src={imagePath.startsWith('/') ? imagePath : `/${imagePath}`}
                        alt={title || 'Article image'}
                        style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover'
                        }}
                        loading="lazy"
                    />
                ) : (
                    <div className="article-card-image-placeholder">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor" opacity="0.5">
                            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-5-7l-3 3.72L9 13l-3 4h12l-4-5z" />
                        </svg>
                    </div>
                )}
            </Link>

            <div className="article-card-content">
                <div className="article-card-meta">
                    <span className="article-card-source">{sourceName}</span>
                    <span>•</span>
                    <time dateTime={publishedAt || createdAt}>{displayDate}</time>
                </div>

                <h3 className="article-card-title">
                    <Link href={`/article/${_id}`}>
                        {title || 'Untitled Article'}
                    </Link>
                </h3>

                {summary && (
                    <p className="article-card-summary">{summary}</p>
                )}

                {hashtags.length > 0 && (
                    <div className="article-card-tags">
                        {hashtags.map((tag, index) => (
                            <span key={index} className="article-card-tag">
                                {tag.startsWith('#') ? tag : `#${tag}`}
                            </span>
                        ))}
                    </div>
                )}
            </div>
        </article>
    );
}
