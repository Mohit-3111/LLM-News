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
