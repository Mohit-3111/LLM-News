/**
 * MongoDB connection utility for Admin Panel.
 * Supports environment variables (production) and config.yaml (development).
 */

import { MongoClient } from 'mongodb';
import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

let client = null;
let clientPromise = null;

/**
 * Get MongoDB configuration from env vars or config.yaml
 */
function getMongoConfig() {
    // Priority 1: Environment variables
    if (process.env.MONGODB_URI) {
        return {
            uri: process.env.MONGODB_URI,
            dbName: process.env.MONGODB_DB || 'llm_news',
            collectionName: process.env.MONGODB_COLLECTION || 'articles'
        };
    }

    // Priority 2: config.yaml from parent LLM News directory
    try {
        const configPath = path.join(process.cwd(), '..', 'config.yaml');
        const fileContents = fs.readFileSync(configPath, 'utf8');
        const config = yaml.load(fileContents);
        return {
            uri: config.MONGODB.CONNECTION_URL,
            dbName: config.MONGODB.DATABASE_NAME || 'llm_news',
            collectionName: config.MONGODB.COLLECTION_NAME || 'articles'
        };
    } catch (error) {
        console.error('Failed to load config.yaml:', error.message);
        throw new Error('MongoDB config not found. Set MONGODB_URI env var or ensure config.yaml exists.');
    }
}

export async function getMongoClient() {
    if (client) return client;
    if (clientPromise) {
        client = await clientPromise;
        return client;
    }

    const { uri } = getMongoConfig();
    const mongoClient = new MongoClient(uri, {
        maxPoolSize: 10,
        serverSelectionTimeoutMS: 5000
    });

    clientPromise = mongoClient.connect();
    client = await clientPromise;
    return client;
}

export async function getDatabase() {
    const mongoClient = await getMongoClient();
    const { dbName } = getMongoConfig();
    return mongoClient.db(dbName);
}

export async function getArticlesCollection() {
    const db = await getDatabase();
    const { collectionName } = getMongoConfig();
    return db.collection(collectionName);
}

/**
 * Get the pageviews collection for analytics.
 */
export async function getPageviewsCollection() {
    const db = await getDatabase();
    return db.collection('pageviews');
}

/**
 * Get analytics data for the dashboard.
 * 
 * New data structure: One document per article with:
 * - articleId, title, count, timestamps[]
 * 
 * @param {number} days - Number of days to look back (default: 7)
 */
export async function getAnalyticsData(days = 7) {
    const db = await getDatabase();
    const pageviews = db.collection('pageviews');
    const articles = db.collection('articles');

    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    const startDateISO = startDate.toISOString();
    const todayStart = new Date();
    todayStart.setHours(0, 0, 0, 0);
    const todayISO = todayStart.toISOString();

    // Get all tracked articles
    const allArticles = await pageviews.find({}).toArray();

    // Calculate total views (sum of all counts)
    const totalViews = allArticles.reduce((sum, a) => sum + (a.count || 0), 0);

    // Calculate views in date range (count timestamps within range)
    let recentViews = 0;
    let todayViews = 0;
    const dailyViewsMap = {};

    allArticles.forEach(article => {
        const timestamps = article.timestamps || [];
        timestamps.forEach(ts => {
            if (ts >= startDateISO) {
                recentViews++;
                const dateKey = ts.split('T')[0];
                dailyViewsMap[dateKey] = (dailyViewsMap[dateKey] || 0) + 1;
            }
            if (ts >= todayISO) {
                todayViews++;
            }
        });
    });

    // Convert daily views map to sorted array
    const dailyViews = Object.entries(dailyViewsMap)
        .map(([date, views]) => ({ date, views }))
        .sort((a, b) => a.date.localeCompare(b.date));

    // Top articles by total count (already sorted by count)
    const topArticles = allArticles
        .sort((a, b) => (b.count || 0) - (a.count || 0))
        .slice(0, 10);

    // Enrich top articles with source from articles collection
    const enrichedTopArticles = await Promise.all(
        topArticles.map(async (item) => {
            try {
                const { ObjectId } = await import('mongodb');
                if (item.articleId && ObjectId.isValid(item.articleId)) {
                    const article = await articles.findOne({ _id: new ObjectId(item.articleId) });
                    return {
                        _id: item.articleId,
                        title: article?.title || item.title || 'Unknown',
                        source: article?.source?.name || article?.source || 'Unknown',
                        views: item.count || 0
                    };
                }
            } catch (e) {
                // Ignore errors
            }
            return {
                _id: item.articleId,
                title: item.title || 'Unknown',
                source: 'Unknown',
                views: item.count || 0
            };
        })
    );

    // Views by source
    const sourceCountMap = {};
    for (const item of enrichedTopArticles) {
        const source = item.source || 'Unknown';
        sourceCountMap[source] = (sourceCountMap[source] || 0) + item.views;
    }
    const viewsBySource = Object.entries(sourceCountMap)
        .map(([source, count]) => ({ source, count }))
        .sort((a, b) => b.count - a.count);

    return {
        totalViews,
        recentViews,
        todayViews,
        dailyViews,
        topArticles: enrichedTopArticles,
        viewsBySource,
        uniqueArticlesViewed: allArticles.length,
        avgDailyViews: days > 0 ? Math.round(recentViews / days * 10) / 10 : 0
    };
}

