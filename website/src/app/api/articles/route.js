import { NextResponse } from 'next/server';
import { fetchArticles, getCategories } from '@/lib/mongodb';

/**
 * GET /api/articles
 * 
 * Query parameters:
 * - status: 'processed' | 'published' (default: 'processed')
 * - limit: number (default: 20)
 * - skip: number (default: 0)
 * - category: string (optional)
 */
export async function GET(request) {
    try {
        const { searchParams } = new URL(request.url);

        const status = searchParams.get('status') || 'processed';
        const limit = parseInt(searchParams.get('limit') || '20', 10);
        const skip = parseInt(searchParams.get('skip') || '0', 10);
        const category = searchParams.get('category') || null;

        // Validate parameters
        if (limit < 1 || limit > 100) {
            return NextResponse.json(
                { error: 'Limit must be between 1 and 100' },
                { status: 400 }
            );
        }

        if (skip < 0) {
            return NextResponse.json(
                { error: 'Skip must be non-negative' },
                { status: 400 }
            );
        }

        const result = await fetchArticles({ status, limit, skip, category });

        return NextResponse.json({
            success: true,
            ...result,
            pagination: {
                limit,
                skip,
                hasMore: skip + result.articles.length < result.total,
            },
        });
    } catch (error) {
        console.error('API Error - GET /api/articles:', error);

        return NextResponse.json(
            {
                success: false,
                error: 'Failed to fetch articles',
                message: error.message
            },
            { status: 500 }
        );
    }
}
