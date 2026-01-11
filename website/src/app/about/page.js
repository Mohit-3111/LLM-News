export const metadata = {
    title: 'About',
    description: 'Learn about LLM Daily - your automated AI news aggregator powered by intelligent agents.',
};

export default function AboutPage() {
    const features = [
        {
            icon: '🔍',
            title: 'Smart Scraping',
            description: 'Our scraper agent collects news from multiple sources including NewsAPI and Google News, ensuring comprehensive coverage of the AI landscape.',
        },
        {
            icon: '🤖',
            title: 'AI-Powered Curation',
            description: 'Content is processed by LLMs to create unique summaries, extract key insights, and generate platform-optimized content.',
        },
        {
            icon: '🎨',
            title: 'AI Image Generation',
            description: 'Each article features custom AI-generated imagery that captures the essence of the story.',
        },
        {
            icon: '⚡',
            title: 'Real-Time Updates',
            description: 'The pipeline runs every 15 minutes, ensuring you always have access to the latest developments in AI.',
        },
        {
            icon: '📱',
            title: 'Multi-Platform',
            description: 'Content is tailored for website, Telegram, and Instagram, reaching audiences wherever they are.',
        },
        {
            icon: '🔧',
            title: 'Open Source Stack',
            description: 'Built entirely with open-source and free tools, demonstrating the power of accessible AI technology.',
        },
    ];

    return (
        <div className="container" style={{ paddingTop: 'var(--space-12)', paddingBottom: 'var(--space-12)' }}>
            {/* Hero Section */}
            <section style={{ textAlign: 'center', maxWidth: '800px', margin: '0 auto var(--space-16)' }}>
                <div className="hero-badge animate-fade-in" style={{ display: 'inline-flex' }}>
                    <span>About Us</span>
                </div>

                <h1 className="animate-fade-in-up" style={{ marginTop: 'var(--space-6)', marginBottom: 'var(--space-6)' }}>
                    The Future of{' '}
                    <span className="text-gradient">AI News</span>{' '}
                    is Automated
                </h1>

                <p className="animate-fade-in-up" style={{
                    fontSize: '1.25rem',
                    color: 'var(--text-secondary)',
                    lineHeight: 1.7
                }}>
                    LLM Daily is an intelligent news aggregation system that leverages cutting-edge
                    AI technology to curate, process, and deliver the most relevant AI and LLM news
                    directly to you.
                </p>
            </section>

            {/* How It Works */}
            <section style={{ marginBottom: 'var(--space-16)' }}>
                <h2 style={{ textAlign: 'center', marginBottom: 'var(--space-10)' }}>
                    How It Works
                </h2>

                <div className="glass-card animate-fade-in-up" style={{
                    padding: 'var(--space-8)',
                    maxWidth: '900px',
                    margin: '0 auto'
                }}>
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                        gap: 'var(--space-6)',
                        textAlign: 'center'
                    }}>
                        {[
                            { step: '1', label: 'Scrape', desc: 'Collect news' },
                            { step: '2', label: 'Orchestrate', desc: 'Coordinate pipeline' },
                            { step: '3', label: 'Curate', desc: 'AI processing' },
                            { step: '4', label: 'Generate', desc: 'Create images' },
                            { step: '5', label: 'Publish', desc: 'Deploy content' },
                        ].map((item, index) => (
                            <div key={index}>
                                <div style={{
                                    width: '48px',
                                    height: '48px',
                                    margin: '0 auto var(--space-3)',
                                    background: 'var(--accent-gradient)',
                                    borderRadius: 'var(--radius-full)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontWeight: 700,
                                    fontSize: '1.25rem'
                                }}>
                                    {item.step}
                                </div>
                                <h4 style={{ marginBottom: 'var(--space-1)' }}>{item.label}</h4>
                                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{item.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Features Grid */}
            <section style={{ marginBottom: 'var(--space-16)' }}>
                <h2 style={{ textAlign: 'center', marginBottom: 'var(--space-10)' }}>
                    Key Features
                </h2>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                    gap: 'var(--space-6)'
                }} className="stagger-animation">
                    {features.map((feature, index) => (
                        <div key={index} className="glass-card" style={{ padding: 'var(--space-6)' }}>
                            <span style={{ fontSize: '2rem', marginBottom: 'var(--space-4)', display: 'block' }}>
                                {feature.icon}
                            </span>
                            <h3 style={{ marginBottom: 'var(--space-3)', fontSize: '1.125rem' }}>
                                {feature.title}
                            </h3>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9375rem', lineHeight: 1.6 }}>
                                {feature.description}
                            </p>
                        </div>
                    ))}
                </div>
            </section>

            {/* Tech Stack */}
            <section style={{ marginBottom: 'var(--space-16)' }}>
                <h2 style={{ textAlign: 'center', marginBottom: 'var(--space-10)' }}>
                    Technology Stack
                </h2>

                <div style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    justifyContent: 'center',
                    gap: 'var(--space-3)'
                }}>
                    {[
                        'Python', 'Next.js', 'MongoDB', 'Groq LLM',
                        'NewsAPI', 'Pollinations.ai', 'APScheduler'
                    ].map((tech, index) => (
                        <span key={index} className="tag" style={{ fontSize: '1rem', padding: 'var(--space-3) var(--space-5)' }}>
                            {tech}
                        </span>
                    ))}
                </div>
            </section>

            {/* CTA */}
            <section className="glass-card animate-fade-in-up" style={{
                padding: 'var(--space-12)',
                textAlign: 'center',
                background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1))'
            }}>
                <h2 style={{ marginBottom: 'var(--space-4)' }}>
                    Stay Updated
                </h2>
                <p style={{
                    color: 'var(--text-secondary)',
                    marginBottom: 'var(--space-6)',
                    maxWidth: '500px',
                    margin: '0 auto var(--space-6)'
                }}>
                    Follow us on Telegram and Instagram for real-time AI news updates
                    delivered straight to your feed.
                </p>
                <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--space-4)', flexWrap: 'wrap' }}>
                    <a href="#" className="btn btn-primary">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
                        </svg>
                        Telegram
                    </a>
                    <a href="#" className="btn btn-secondary">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                        </svg>
                        Instagram
                    </a>
                </div>
            </section>
        </div>
    );
}
