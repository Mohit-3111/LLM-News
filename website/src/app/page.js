import HeroSection from '@/components/HeroSection';
import NewsGrid from '@/components/NewsGrid';
import { fetchArticles } from '@/lib/mongodb';

// Revalidate every 5 minutes to show fresh content
export const revalidate = 300;

export default async function HomePage() {
  let articles = [];
  let error = null;

  try {
    const result = await fetchArticles({
      status: 'processed',
      limit: 21
    });
    articles = result.articles;
  } catch (e) {
    console.error('Failed to fetch articles:', e);
    error = e.message;
  }

  // Separate featured article from the rest
  const featuredArticle = articles.length > 0 ? articles[0] : null;
  const remainingArticles = articles.slice(1);

  return (
    <>
      <HeroSection featuredArticle={featuredArticle} />

      {error ? (
        <section className="news-section">
          <div className="container">
            <div className="glass-card" style={{
              padding: 'var(--space-8)',
              textAlign: 'center',
              background: 'rgba(239, 68, 68, 0.1)',
              borderColor: 'rgba(239, 68, 68, 0.3)'
            }}>
              <h3 style={{ marginBottom: 'var(--space-4)', color: '#ef4444' }}>
                Unable to Load Articles
              </h3>
              <p style={{ color: 'var(--text-secondary)' }}>
                {error.includes('config')
                  ? 'Please ensure config.yaml is properly configured with MongoDB credentials.'
                  : 'There was an error connecting to the database. Please try again later.'}
              </p>
            </div>
          </div>
        </section>
      ) : (
        <NewsGrid
          articles={remainingArticles}
          title="Latest AI & LLM News"
        />
      )}
    </>
  );
}
