/**
 * Configuration loader for the website.
 * Reads from the parent directory's config.yaml file.
 */

import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

let config = null;

export function getConfig() {
    if (config) {
        return config;
    }

    try {
        // Read config.yaml from parent directory (e:\LLM News\config.yaml)
        const configPath = path.join(process.cwd(), '..', 'config.yaml');
        const fileContents = fs.readFileSync(configPath, 'utf8');
        config = yaml.load(fileContents);
        return config;
    } catch (error) {
        console.error('Failed to load config.yaml:', error);
        throw new Error('Configuration file not found. Ensure config.yaml exists in the LLM News root directory.');
    }
}

export function getMongoConfig() {
    const cfg = getConfig();
    return {
        uri: cfg.MONGODB.CONNECTION_URL,
        dbName: cfg.MONGODB.DATABASE_NAME,
        collectionName: cfg.MONGODB.COLLECTION_NAME,
    };
}
