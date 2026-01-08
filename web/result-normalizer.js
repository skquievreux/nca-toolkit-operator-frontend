/**
 * Result Normalizer
 * Transforms complex job/scenario results into a standardized format for display.
 */

const ResultNormalizer = {

    // Config: Known keys that indicate specific content types
    TEXT_KEYS: ['text', 'transcript', 'summary', 'content', 'message', 'response', 'result', 'output', 'analysis', 'reasoning'],
    VIDEO_EXTS: ['mp4', 'webm', 'ogg', 'mov'],
    AUDIO_EXTS: ['mp3', 'wav', 'aac', 'm4a'],
    IMAGE_EXTS: ['png', 'jpg', 'jpeg', 'gif', 'webp'],

    /**
     * Main function to normalize any job result object
     * @param {Object} jobResult - The raw result object from the backend
     * @returns {Array} - Array of normalized "blocks" { type, content, label, ... }
     */
    normalize(jobResult) {
        if (!jobResult) return [];

        let blocks = [];
        const seenContent = new Set(); // To prevent duplicates

        // Helper to add unique blocks
        const addBlock = (block) => {
            const contentKey = block.content || block.url;
            if (contentKey && !seenContent.has(contentKey)) {
                seenContent.add(contentKey);
                blocks.push(block);
            }
        };

        // Recursive traversal function
        const traverse = (obj, contextLabel = '') => {
            if (!obj) return;

            // 1. Direct Typed Objects (e.g. from specific steps)
            if (obj.url && typeof obj.url === 'string') {
                const type = this.detectTypeFromUrl(obj.url);
                if (type) {
                    addBlock({ type, url: obj.url, label: contextLabel || 'Media' });
                }
            }

            // 2. Filename without URL -> Construct URL
            if (obj.filename && typeof obj.filename === 'string' && !obj.url) {
                const url = this.constructUrl(obj.filename);
                const type = this.detectTypeFromUrl(obj.filename);
                if (type && url) {
                    addBlock({ type, url: url, label: contextLabel || 'File Result' });
                }
            }

            // 3. Text Content
            for (const key of this.TEXT_KEYS) {
                if (obj[key] && typeof obj[key] === 'string' && obj[key].length > 0) {
                    // Filter out short status messages or HTTP-like strings
                    if (obj[key].length > 20 && !obj[key].startsWith('http')) {
                        addBlock({
                            type: 'text',
                            content: obj[key],
                            label: contextLabel ? `${contextLabel} (${key})` : key
                        });
                    }
                }
            }

            // 4. Recursive Step Traversal
            if (typeof obj === 'object') {
                Object.entries(obj).forEach(([key, val]) => {
                    // recursing into objects, using key as context label (e.g. "transcribe", "download")
                    if (typeof val === 'object' && val !== null) {
                        traverse(val, key); // Pass down the key as a label hint
                    }
                });
            }
        };

        // Start traversal
        traverse(jobResult);

        // Sort blocks: Media first, then Text
        return blocks.sort((a, b) => {
            if (a.type !== 'text' && b.type === 'text') return -1;
            if (a.type === 'text' && b.type !== 'text') return 1;
            return 0;
        });
    },

    /**
     * Detects media type from file extension
     */
    detectTypeFromUrl(url) {
        if (!url) return null;
        const ext = url.split('.').pop().toLowerCase().split('?')[0]; // Handle query params

        if (this.VIDEO_EXTS.includes(ext)) return 'video';
        if (this.AUDIO_EXTS.includes(ext)) return 'audio';
        if (this.IMAGE_EXTS.includes(ext)) return 'image';
        return null; // Unknown or generic file
    },

    /**
     * Constructs a backend URL from a filename
     */
    constructUrl(filename) {
        // Assuming global STATE or CONFIG is available, otherwise default relative
        const backend = (typeof state !== 'undefined' && state.backendUrl) ? state.backendUrl : '';
        return `${backend}/uploads/${filename}`;
    }
};

console.log('✅ ResultNormalizer loaded');
