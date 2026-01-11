/**
 * MongoDB connection utility for Next.js.
 * Uses connection pooling optimized for serverless environments.
 */

import { MongoClient } from 'mongodb';
import { getMongoConfig } from './config';

let client = null;
let clientPromise = null;

export async function getMongoClient() {
    if (client) {
        return client;
    }

    if (clientPromise) {
        client = await clientPromise;
        return client;
    }

    const { uri } = getMongoConfig();

    const mongoClient = new MongoClient(uri, {
        maxPoolSize: 10,
        serverSelectionTimeoutMS: 5000,
        socketTimeoutMS: 45000,
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
 * Fetch articles with optional filters and pagination.
 */
export async function fetchArticles({
    status = 'processed',
    limit = 20,
    skip = 0,
    category = null
} = {}) {
    const collection = await getArticlesCollection();

    const query = { status };
    if (category) {
        query['curated.entities'] = { $regex: category, $options: 'i' };
    }

    const articles = await collection
        .find(query)
        .sort({ publishedAt: -1, createdAt: -1 })
        .skip(skip)
        .limit(limit)
        .toArray();

    const total = await collection.countDocuments(query);

    // Convert ObjectId to string for JSON serialization
    const serializedArticles = articles.map(article => ({
        ...article,
        _id: article._id.toString(),
    }));

    return { articles: serializedArticles, total };
}

/**
 * Fetch a single article by ID.
 */
export async function fetchArticleById(id) {
    const { ObjectId } = await import('mongodb');

    // Validate ObjectId format
    if (!id || !ObjectId.isValid(id)) {
        return null;
    }

    const collection = await getArticlesCollection();

    const article = await collection.findOne({ _id: new ObjectId(id) });

    if (!article) {
        return null;
    }

    return {
        ...article,
        _id: article._id.toString(),
    };
}

/**
 * Mark an article as published.
 */
export async function markArticlePublished(id) {
    const { ObjectId } = await import('mongodb');
    const collection = await getArticlesCollection();

    const result = await collection.updateOne(
        { _id: new ObjectId(id) },
        {
            $set: {
                status: 'published',
                publishedAt: new Date(),
                updatedAt: new Date()
            }
        }
    );

    return result.modifiedCount > 0;
}

/**
 * Get distinct categories/entities from articles.
 */
export async function getCategories() {
    const collection = await getArticlesCollection();

    const result = await collection.aggregate([
        { $match: { status: { $in: ['processed', 'published'] } } },
        { $unwind: '$curated.entities' },
        { $group: { _id: '$curated.entities', count: { $sum: 1 } } },
        { $sort: { count: -1 } },
        { $limit: 20 }
    ]).toArray();

    return result.map(r => ({ name: r._id, count: r.count }));
}
