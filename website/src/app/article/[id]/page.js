
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { fetchArticleById, fetchArticles } from '@/lib/mongodb';

// Revalidate every 5 minutes
export const revalidate = 300;

/**
 * Generate metadata for the article page.
 */
export async function generateMetadata({ params }) {
    const { id } = await params;

    try {
        const article = await fetchArticleById(id);

        if (!article) {
            return {
                title: 'Article Not Found',
            };
        }

        const title = article.title || 'Untitled Article';
        const description = article.platforms?.website?.summary ||
            article.curated?.summary ||
            article.description ||
            'Read this article on LLM Daily';

        return {
            title,
            description,
            openGraph: {
                title,
                description,
                type: 'article',
                publishedTime: article.publishedAt,
                images: article.images?.website?.path ? [{
                    url: article.images.website.path,
                    width: 1280,
                    height: 720,
                }] : [],
            },
            twitter: {
                card: 'summary_large_image',
                title,
                description,
            },
        };
    } catch (error) {
        return {
            title: 'Article',
        };
    }
}

/**
 * Format date for display.
 */
function formatDate(dateString) {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    });
}

/**
 * Calculate reading time.
 */
function getReadingTime(content) {
    if (!content) return '1 min read';
    const wordsPerMinute = 200;
    const words = content.split(/\s+/).length;
    const minutes = Math.ceil(words / wordsPerMinute);
    return `${minutes} min read`;
}

export default async function ArticlePage({ params }) {
    const { id } = await params;

    let article = null;
    let relatedArticles = [];

    try {
        article = await fetchArticleById(id);

        if (article) {
            // Fetch related articles
            const result = await fetchArticles({ status: 'processed', limit: 4 });
            relatedArticles = result.articles.filter(a => a._id !== id).slice(0, 3);
        }
    } catch (error) {
        console.error('Failed to fetch article:', error);
    }

    if (!article) {
        notFound();
    }

    const {
        title,
        source,
        publishedAt,
        createdAt,
        curated,
        platforms,
        images,
        url: originalUrl,
    } = article;

    // Get content from platform-specific or curated data
    const content = platforms?.website?.full_article ||
        curated?.rewritten_content ||
        article.content ||
        '';

    const summary = platforms?.website?.summary || curated?.summary || '';
    // Ensure hashtags and entities are arrays
    const rawHashtags = curated?.hashtags;
    const rawEntities = curated?.entities;
    const hashtags = Array.isArray(rawHashtags) ? rawHashtags : [];
    const entities = Array.isArray(rawEntities) ? rawEntities : [];

    // Get the image URL - prefer ImgBB cloud URL, fallback to local path
    const imageUrl = images?.website?.url || null;
    const imagePath = images?.website?.path || null;
    const imageSrc = imageUrl || (imagePath ? (imagePath.startsWith('/') ? imagePath : `/${imagePath}`) : null);

    const sourceName = source?.name || source || 'Unknown Source';
    const displayDate = formatDate(publishedAt || createdAt);
    const readingTime = getReadingTime(content);

    return (
        <article className="article-page">
            <div className="container">
                {/* Hero Image */}
                {imageSrc && (
                    <div className="article-hero-image animate-fade-in">
                        <img
                            src={imageSrc}
                            alt={title || 'Article image'}
                            style={{
                                width: '100%',
                                height: '100%',
                                objectFit: 'cover'
                            }}
                        />
                    </div>
                )}

                {/* Article Header */}
                <header className="article-header animate-fade-in-up">
                    <div className="article-meta">
                        <span className="badge">{sourceName}</span>
                        <span>{displayDate}</span>
                        <span>•</span>
                        <span>{readingTime}</span>
                    </div>

                    <h1 className="article-title">{title}</h1>

                    {summary && (
                        <p style={{
                            fontSize: '1.25rem',
                            color: 'var(--text-secondary)',
                            lineHeight: 1.7
                        }}>
                            {summary}
                        </p>
                    )}
                </header>

                {/* Article Content */}
                <div className="article-content animate-fade-in-up">
                    {content.split('\n\n').map((paragraph, index) => {
                        // Check if it's a heading (starts with # or is short and ends with :)
                        if (paragraph.startsWith('## ')) {
                            return <h2 key={index}>{paragraph.replace('## ', '')}</h2>;
                        }
                        if (paragraph.startsWith('### ')) {
                            return <h3 key={index}>{paragraph.replace('### ', '')}</h3>;
                        }
                        if (paragraph.trim()) {
                            return <p key={index}>{paragraph}</p>;
                        }
                        return null;
                    })}
                </div>

                {/* Tags */}
                {(hashtags.length > 0 || entities.length > 0) && (
                    <div className="article-tags">
                        {hashtags.map((tag, index) => (
                            <span key={`hash-${index}`} className="tag">
                                {tag.startsWith('#') ? tag : `#${tag}`}
                            </span>
                        ))}
                        {entities.map((entity, index) => (
                            <span key={`entity-${index}`} className="tag">
                                {entity}
                            </span>
                        ))}
                    </div>
                )}

                {/* Original Source Link */}
                {originalUrl && (
                    <div style={{
                        textAlign: 'center',
                        marginTop: 'var(--space-8)',
                        paddingTop: 'var(--space-8)',
                        borderTop: '1px solid var(--border-color)'
                    }}>
                        <a
                            href={originalUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn btn-secondary"
                        >
                            Read Original Source
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3" />
                            </svg>
                        </a>
                    </div>
                )}

                {/* Related Articles */}
                {relatedArticles.length > 0 && (
                    <section style={{ marginTop: 'var(--space-16)' }}>
                        <h2 style={{
                            fontSize: '1.5rem',
                            marginBottom: 'var(--space-8)',
                            textAlign: 'center'
                        }}>
                            More Articles
                        </h2>
                        <div className="news-grid" style={{ maxWidth: '1000px', margin: '0 auto' }}>
                            {relatedArticles.map((related) => (
                                <Link
                                    key={related._id}
                                    href={`/article/${related._id}`}
                                    className="glass-card"
                                    style={{
                                        padding: 'var(--space-6)',
                                        display: 'block'
                                    }}
                                >
                                    <span className="badge mb-2">
                                        {related.source?.name || related.source || 'News'}
                                    </span>
                                    <h3 style={{
                                        fontSize: '1rem',
                                        fontWeight: 600,
                                        lineHeight: 1.4,
                                        display: '-webkit-box',
                                        WebkitLineClamp: 2,
                                        WebkitBoxOrient: 'vertical',
                                        overflow: 'hidden'
                                    }}>
                                        {related.title}
                                    </h3>
                                </Link>
                            ))}
                        </div>
                    </section>
                )}

                {/* Back to Home */}
                <div style={{ textAlign: 'center', marginTop: 'var(--space-12)' }}>
                    <Link href="/" className="btn btn-primary">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M19 12H5M12 19l-7-7 7-7" />
                        </svg>
                        Back to Home
                    </Link>
                </div>
            </div>
        </article>
    );
}
