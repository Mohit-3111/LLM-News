import { NextResponse } from 'next/server';
import { markArticlePublished, fetchArticleById } from '@/lib/mongodb';

/**
 * POST /api/publish
 * 
 * Body:
 * - articleId: string (required) - MongoDB ObjectId of the article to publish
 * 
 * This endpoint is used by the posting agent to mark articles as published
 * after they have been successfully posted to platforms.
 */
export async function POST(request) {
    try {
        const body = await request.json();
        const { articleId } = body;

        // Validate articleId
        if (!articleId) {
            return NextResponse.json(
                { success: false, error: 'articleId is required' },
                { status: 400 }
            );
        }

        // Check if article exists
        const article = await fetchArticleById(articleId);
        if (!article) {
            return NextResponse.json(
                { success: false, error: 'Article not found' },
                { status: 404 }
            );
        }

        // Check if already published
        if (article.status === 'published') {
            return NextResponse.json({
                success: true,
                message: 'Article is already published',
                article: {
                    id: article._id,
                    title: article.title,
                    status: article.status,
                    publishedAt: article.publishedAt,
                },
            });
        }

        // Mark as published
        const updated = await markArticlePublished(articleId);

        if (!updated) {
            return NextResponse.json(
                { success: false, error: 'Failed to update article status' },
                { status: 500 }
            );
        }

        return NextResponse.json({
            success: true,
            message: 'Article marked as published',
            article: {
                id: articleId,
                title: article.title,
                status: 'published',
                publishedAt: new Date().toISOString(),
            },
        });
    } catch (error) {
        console.error('API Error - POST /api/publish:', error);

        return NextResponse.json(
            {
                success: false,
                error: 'Failed to publish article',
                message: error.message
            },
            { status: 500 }
        );
    }
}
