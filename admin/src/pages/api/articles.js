import { getArticlesCollection } from '@/lib/mongodb';

export default async function handler(req, res) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { limit = '20', status = 'all' } = req.query;
        const collection = await getArticlesCollection();

        // Build query
        const query = {};
        if (status && status !== 'all') {
            query.status = status;
        }

        // Fetch articles
        const articles = await collection
            .find(query)
            .sort({ createdAt: -1 })
            .limit(parseInt(limit))
            .toArray();

        // Serialize ObjectId
        const serialized = articles.map(article => ({
            _id: article._id.toString(),
            title: article.title,
            source: article.source,
            status: article.status,
            createdAt: article.createdAt,
            publishedAt: article.publishedAt,
            url: article.url,
            hasImages: !!(article.images?.website?.url),
            imageRetryCount: article.image_retry_count || 0
        }));

        res.status(200).json({ articles: serialized });

    } catch (error) {
        console.error('Failed to fetch articles:', error);
        res.status(500).json({ error: 'Failed to fetch articles' });
    }
}
