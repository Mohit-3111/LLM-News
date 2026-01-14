import { getArticlesCollection } from '@/lib/mongodb';

export default async function handler(req, res) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const collection = await getArticlesCollection();

        // Get article counts by status
        const pipeline = [
            { $group: { _id: '$status', count: { $sum: 1 } } }
        ];

        const statusCounts = await collection.aggregate(pipeline).toArray();

        // Convert to object
        const articles = {};
        let total = 0;
        statusCounts.forEach(item => {
            if (item._id) {
                articles[item._id] = item.count;
                total += item.count;
            }
        });

        // Get most recent article timestamp
        const latestArticle = await collection
            .find({})
            .sort({ createdAt: -1 })
            .limit(1)
            .toArray();

        const lastUpdated = latestArticle[0]?.createdAt || null;

        const stats = {
            articles: {
                raw: articles.raw || 0,
                curated: articles.curated || 0,
                generating_images: articles.generating_images || 0,
                processed: articles.processed || 0,
                published: articles.published || 0,
                filtered: articles.filtered || 0,
                error: articles.error || 0
            },
            total,
            lastUpdated
        };

        res.status(200).json(stats);

    } catch (error) {
        console.error('Failed to fetch admin stats:', error);
        res.status(500).json({ error: 'Failed to fetch stats' });
    }
}
