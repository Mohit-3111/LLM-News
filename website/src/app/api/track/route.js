/**
 * Analytics Tracking API
 * 
 * Stores one document per article with:
 * - articleId: The article's MongoDB _id
 * - title: Article title
 * - count: Total view count (for ranking)
 * - timestamps: Array of view timestamps
 */

import { getDatabase } from '@/lib/mongodb';

export async function POST(request) {
    try {
        const body = await request.json();
        const { articleId, title } = body;

        console.log('Track API called with:', { articleId, title });

        // Only track article views (articleId is required)
        if (!articleId) {
            return Response.json({ error: 'articleId is required' }, { status: 400 });
        }

        const db = await getDatabase();
        console.log('Connected to database:', db.databaseName);

        const pageviewsCollection = db.collection('pageviews');
        const timestamp = new Date().toISOString();

        // Upsert: Update if exists, insert if not
        const result = await pageviewsCollection.updateOne(
            { articleId },
            {
                $set: {
                    articleId,
                    title: title || 'Untitled',
                    lastViewed: timestamp
                },
                $inc: { count: 1 },
                $push: { timestamps: timestamp }
            },
            { upsert: true }
        );

        console.log('MongoDB updateOne result:', {
            matchedCount: result.matchedCount,
            modifiedCount: result.modifiedCount,
            upsertedId: result.upsertedId
        });

        return Response.json({
            success: true,
            upserted: !!result.upsertedId,
            modified: result.modifiedCount > 0
        });
    } catch (error) {
        console.error('Failed to track pageview:', error);
        return Response.json({ error: 'Failed to track', details: error.message }, { status: 500 });
    }
}

// GET endpoint to retrieve basic stats
export async function GET() {
    try {
        const db = await getDatabase();
        const pageviewsCollection = db.collection('pageviews');

        const articles = await pageviewsCollection.find({}).toArray();
        console.log('GET /api/track - Found articles:', articles.length, articles);

        const totalViews = articles.reduce((sum, a) => sum + (a.count || 0), 0);

        return Response.json({
            totalViews,
            articlesTracked: articles.length,
            articles: articles
        });
    } catch (error) {
        console.error('Failed to get stats:', error);
        return Response.json({ error: 'Failed to get stats', details: error.message }, { status: 500 });
    }
}
