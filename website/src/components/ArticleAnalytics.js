'use client';

/**
 * ArticleAnalytics - Client-side analytics for article pages
 * Wraps the AnalyticsTracker for article pages
 */

import AnalyticsTracker from './AnalyticsTracker';

export default function ArticleAnalytics({ articleId, title }) {
    return <AnalyticsTracker articleId={articleId} title={title} />;
}
