/**
 * Configuration loader for the website.
 * 
 * Priority:
 * 1. Environment variables (for Vercel/production)
 * 2. config.yaml file (for local development)
 */

import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

let config = null;

/**
 * Check if running with environment variables (Vercel deployment)
 */
function hasEnvConfig() {
    return !!process.env.MONGODB_URI;
}

export function getConfig() {
    // If environment variables are set, don't load from file
    if (hasEnvConfig()) {
        return null;
    }

    if (config) {
        return config;
    }

    try {
        // Read config.yaml from parent directory (for local development)
        const configPath = path.join(process.cwd(), '..', 'config.yaml');
        const fileContents = fs.readFileSync(configPath, 'utf8');
        config = yaml.load(fileContents);
        return config;
    } catch (error) {
        console.error('Failed to load config.yaml:', error.message);
        return null;
    }
}

export function getMongoConfig() {
    // Priority 1: Environment variables (Vercel)
    if (hasEnvConfig()) {
        return {
            uri: process.env.MONGODB_URI,
            dbName: process.env.MONGODB_DB || 'llm_news',
            collectionName: process.env.MONGODB_COLLECTION || 'articles',
        };
    }

    // Priority 2: Local config.yaml file
    const cfg = getConfig();
    if (cfg && cfg.MONGODB) {
        return {
            uri: cfg.MONGODB.CONNECTION_URL,
            dbName: cfg.MONGODB.DATABASE_NAME || 'llm_news',
            collectionName: cfg.MONGODB.COLLECTION_NAME || 'articles',
        };
    }

    // No configuration found
    throw new Error(
        'MongoDB configuration not found. ' +
        'Set MONGODB_URI environment variable (production) or ensure config.yaml exists (development).'
    );
}
