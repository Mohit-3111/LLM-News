'use client';

/**
 * AnalyticsTracker Component
 * Fires article view tracking on mount.
 * Only tracks if articleId is provided.
 */

import { useEffect } from 'react';

export default function AnalyticsTracker({ articleId = null, title = null }) {

    useEffect(() => {
        // Only track if we have an articleId
        if (!articleId) {
            console.debug('AnalyticsTracker: No articleId, skipping');
            return;
        }

        const trackPageView = async () => {
            console.log('AnalyticsTracker: Tracking article:', articleId, title);
            try {
                const response = await fetch('/api/track', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        articleId,
                        title,
                    }),
                });

                const data = await response.json();
                console.log('AnalyticsTracker: Response:', data);
            } catch (error) {
                console.error('AnalyticsTracker: Failed:', error);
            }
        };

        trackPageView();
    }, [articleId, title]);

    // This component renders nothing
    return null;
}
