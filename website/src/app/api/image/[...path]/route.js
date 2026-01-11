import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

/**
 * GET /api/image/[...path]
 * 
 * Serves images from the parent directory's generated_images folder.
 * This allows the website to display locally stored generated images.
 */
export async function GET(request, { params }) {
    try {
        const { path: imagePath } = await params;

        // Join the path segments
        const relativePath = Array.isArray(imagePath) ? imagePath.join('/') : imagePath;

        // Construct the absolute path to the image in the parent generated_images folder
        // Website is at e:\LLM News\website, images are at e:\LLM News\generated_images
        const absolutePath = path.join(process.cwd(), '..', 'generated_images', relativePath);

        // Security check: ensure the path is within the generated_images directory
        const normalizedPath = path.normalize(absolutePath);
        const generatedImagesDir = path.normalize(path.join(process.cwd(), '..', 'generated_images'));

        if (!normalizedPath.startsWith(generatedImagesDir)) {
            return NextResponse.json(
                { error: 'Access denied' },
                { status: 403 }
            );
        }

        // Check if file exists
        if (!fs.existsSync(normalizedPath)) {
            return NextResponse.json(
                { error: 'Image not found' },
                { status: 404 }
            );
        }

        // Read the file
        const imageBuffer = fs.readFileSync(normalizedPath);

        // Determine content type based on extension
        const ext = path.extname(normalizedPath).toLowerCase();
        const contentTypeMap = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
        };

        const contentType = contentTypeMap[ext] || 'image/jpeg';

        // Return the image with appropriate headers
        return new NextResponse(imageBuffer, {
            status: 200,
            headers: {
                'Content-Type': contentType,
                'Cache-Control': 'public, max-age=31536000, immutable',
            },
        });
    } catch (error) {
        console.error('Error serving image:', error);
        return NextResponse.json(
            { error: 'Failed to load image' },
            { status: 500 }
        );
    }
}
