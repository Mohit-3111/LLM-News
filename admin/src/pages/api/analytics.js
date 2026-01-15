/**
 * Analytics API Endpoint
 * Returns analytics data for the admin dashboard.
 */

import { getAnalyticsData } from '../../lib/mongodb';

export default async function handler(req, res) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        // Get days parameter (default: 7)
        const days = parseInt(req.query.days) || 7;

        const analytics = await getAnalyticsData(days);

        res.status(200).json({
            success: true,
            ...analytics,
            generatedAt: new Date().toISOString()
        });
    } catch (error) {
        console.error('Failed to fetch analytics:', error);
        res.status(500).json({
            error: 'Failed to fetch analytics',
            message: error.message
        });
    }
}
