/**
 * Smart File Detector
 * Automatically analyzes uploaded files and suggests optimal actions
 *
 * @version 1.0.0
 * @author NCA Toolkit Team
 */

class SmartFileDetector {
    constructor() {
        this.rules = this.loadDetectionRules();
        console.log('🔍 SmartFileDetector initialized');
    }

    /**
     * Analyze uploaded files and suggest actions
     * @param {File[]} files - Array of File objects
     * @returns {Promise<Object>} Analysis result with suggestions
     */
    async analyzeFiles(files) {
        console.log(`🔍 Analyzing ${files.length} file(s)...`);

        const analysis = {
            files: [],
            combinations: [],
            suggestions: [],
            warnings: []
        };

        // Analyze each file individually
        for (const file of files) {
            const fileInfo = await this.analyzeFile(file);
            analysis.files.push(fileInfo);
        }

        // Detect file combinations
        analysis.combinations = this.detectCombinations(analysis.files);

        // Generate suggestions
        analysis.suggestions = this.generateSuggestions(
            analysis.files,
            analysis.combinations
        );

        // Check for potential issues
        analysis.warnings = this.checkWarnings(analysis.files);

        console.log('✅ Analysis complete:', {
            files: analysis.files.length,
            combinations: analysis.combinations.length,
            suggestions: analysis.suggestions.length,
            warnings: analysis.warnings.length
        });

        return analysis;
    }

    /**
     * Analyze single file
     * @param {File} file - File object to analyze
     * @returns {Promise<Object>} File information
     */
    async analyzeFile(file) {
        const info = {
            file: file, // Keep original file object
            name: file.name,
            size: file.size,
            type: file.type,
            extension: this.getExtension(file.name),
            category: this.categorizeFile(file.type),
            metadata: null
        };

        // Get detailed metadata for media files
        if (info.category === 'video' || info.category === 'audio') {
            info.metadata = await this.extractMediaMetadata(file);
        }

        console.log(`  📄 ${file.name}: ${info.category} (${(file.size / 1024 / 1024).toFixed(1)}MB)`);

        return info;
    }

    /**
     * Categorize file by MIME type
     * @param {string} mimeType - MIME type
     * @returns {string} Category
     */
    categorizeFile(mimeType) {
        if (mimeType.startsWith('video/')) return 'video';
        if (mimeType.startsWith('audio/')) return 'audio';
        if (mimeType.startsWith('image/')) return 'image';

        // Check for subtitle files
        if (mimeType.includes('subtitle') ||
            mimeType.includes('srt') ||
            mimeType.includes('vtt')) {
            return 'subtitle';
        }

        return 'other';
    }

    /**
     * Detect file combinations and patterns
     * @param {Object[]} files - Analyzed files
     * @returns {Object[]} Detected combinations
     */
    detectCombinations(files) {
        const combinations = [];

        const videos = files.filter(f => f.category === 'video');
        const audios = files.filter(f => f.category === 'audio');
        const images = files.filter(f => f.category === 'image');
        const subtitles = files.filter(f => f.category === 'subtitle');

        // Video + Audio (highest priority)
        if (videos.length === 1 && audios.length === 1) {
            const durationMatch = this.checkDurationMatch(videos[0], audios[0]);
            combinations.push({
                type: 'video_audio_merge',
                files: [videos[0], audios[0]],
                confidence: durationMatch ? 0.95 : 0.80,
                compatible: durationMatch,
                reason: durationMatch ?
                    'Video und Audio haben gleiche Länge' :
                    'Video und Audio haben unterschiedliche Längen'
            });
        }

        // Multiple Videos (concatenate)
        if (videos.length > 1) {
            const resolutionMatch = this.checkResolutionMatch(videos);
            combinations.push({
                type: 'video_concatenate',
                files: videos,
                confidence: resolutionMatch ? 0.90 : 0.75,
                compatible: resolutionMatch,
                reason: resolutionMatch ?
                    'Alle Videos haben gleiche Auflösung' :
                    'Videos haben unterschiedliche Auflösungen'
            });
        }

        // Video + Subtitle
        if (videos.length === 1 && subtitles.length === 1) {
            combinations.push({
                type: 'video_caption',
                files: [videos[0], subtitles[0]],
                confidence: 0.90,
                compatible: true,
                reason: 'Untertitel können eingebrennt werden'
            });
        }

        // Multiple Images (slideshow)
        if (images.length > 1) {
            combinations.push({
                type: 'images_to_video',
                files: images,
                confidence: 0.75,
                compatible: true,
                reason: 'Bilder können zu Video zusammengefügt werden'
            });
        }

        // Multiple Audio files
        if (audios.length > 1) {
            combinations.push({
                type: 'audio_concatenate',
                files: audios,
                confidence: 0.85,
                compatible: true,
                reason: 'Audio-Dateien können zusammengefügt werden'
            });
        }

        console.log(`  🔗 Found ${combinations.length} combination(s)`);
        return combinations;
    }

    /**
     * Generate action suggestions
     * @param {Object[]} files - Analyzed files
     * @param {Object[]} combinations - Detected combinations
     * @returns {Object[]} Suggested actions
     */
    generateSuggestions(files, combinations) {
        const suggestions = [];

        // Suggestions from combinations (HIGHEST PRIORITY)
        for (const combo of combinations) {
            const suggestion = this.createSuggestionFromCombo(combo);
            if (suggestion) {
                suggestions.push(suggestion);
            }
        }

        // Suggestions for individual files
        for (const file of files) {
            const fileSuggestions = this.getSuggestionsForFile(file);
            suggestions.push(...fileSuggestions);
        }

        // Sort by confidence and priority
        suggestions.sort((a, b) => {
            // Priority order: high > medium > low
            const priorityWeight = { high: 3, medium: 2, low: 1 };
            const aPriority = priorityWeight[a.priority] || 0;
            const bPriority = priorityWeight[b.priority] || 0;

            if (aPriority !== bPriority) {
                return bPriority - aPriority;
            }

            return b.confidence - a.confidence;
        });

        console.log(`  💡 Generated ${suggestions.length} suggestion(s)`);
        return suggestions;
    }

    /**
     * Create suggestion from combination
     * @param {Object} combo - Detected combination
     * @returns {Object|null} Suggestion object
     */
    createSuggestionFromCombo(combo) {
        const suggestionTemplates = {
            'video_audio_merge': {
                title: 'Video mit Audio zusammenführen',
                icon: '🎵',
                description: 'Fügt die Audio-Spur zum Video hinzu',
                endpoint: '/v1/video/add/audio',
                params: (files) => ({
                    video_url: '{{file:0}}',
                    audio_url: '{{file:1}}'
                }),
                priority: 'high'
            },
            'video_concatenate': {
                title: 'Videos zusammenführen',
                icon: '🎬',
                description: `${combo.files.length} Videos zu einem zusammenfügen`,
                endpoint: '/v1/video/concatenate',
                params: (files) => ({
                    video_urls: files.map((f, i) => `{{file:${i}}}`)
                }),
                priority: 'high'
            },
            'video_caption': {
                title: 'Untertitel hinzufügen',
                icon: '📝',
                description: 'Untertitel in Video einbrennen',
                endpoint: '/v1/video/caption',
                params: (files) => ({
                    video_url: '{{file:0}}',
                    subtitle_url: '{{file:1}}'
                }),
                priority: 'high'
            },
            'images_to_video': {
                title: 'Bilder zu Video erstellen',
                icon: '🖼️',
                description: `${combo.files.length} Bilder zu Slideshow-Video`,
                endpoint: '/v1/image/convert/image_to_video',
                params: (files) => ({
                    image_urls: files.map((f, i) => `{{file:${i}}}`),
                    duration_per_image: 3
                }),
                priority: 'medium'
            },
            'audio_concatenate': {
                title: 'Audio-Dateien zusammenführen',
                icon: '🎵',
                description: `${combo.files.length} Audio-Dateien verketten`,
                endpoint: '/v1/audio/concatenate',
                params: (files) => ({
                    audio_urls: files.map((f, i) => `{{file:${i}}}`)
                }),
                priority: 'medium'
            }
        };

        const template = suggestionTemplates[combo.type];
        if (!template) return null;

        return {
            ...template,
            confidence: combo.confidence,
            compatible: combo.compatible,
            files: combo.files,
            reason: combo.reason,
            warning: !combo.compatible ? `⚠️ ${combo.reason}` : null
        };
    }

    /**
     * Get suggestions for individual file
     * @param {Object} file - File info
     * @returns {Object[]} Suggestions
     */
    getSuggestionsForFile(file) {
        const suggestions = [];

        if (file.category === 'video') {
            suggestions.push(
                {
                    title: 'Thumbnail erstellen',
                    icon: '🖼️',
                    description: 'Vorschaubild aus Video generieren',
                    endpoint: '/v1/video/thumbnail',
                    params: { video_url: '{{file:0}}', timestamp: '00:00:05' },
                    confidence: 0.70,
                    priority: 'medium',
                    compatible: true,
                    files: [file]
                },
                {
                    title: 'Zu MP3 konvertieren',
                    icon: '🎧',
                    description: 'Audio aus Video extrahieren',
                    endpoint: '/v1/media/convert/mp3',
                    params: { media_url: '{{file:0}}' },
                    confidence: 0.65,
                    priority: 'medium',
                    compatible: true,
                    files: [file]
                },
                {
                    title: 'Video transkribieren',
                    icon: '📝',
                    description: 'Sprache zu Text umwandeln',
                    endpoint: '/v1/media/transcribe',
                    params: { media_url: '{{file:0}}', language: 'de' },
                    confidence: 0.65,
                    priority: 'medium',
                    compatible: true,
                    files: [file]
                }
            );
        }

        if (file.category === 'audio') {
            suggestions.push(
                {
                    title: 'Audio transkribieren',
                    icon: '📝',
                    description: 'Sprache zu Text umwandeln',
                    endpoint: '/v1/media/transcribe',
                    params: { media_url: '{{file:0}}', language: 'de' },
                    confidence: 0.75,
                    priority: 'medium',
                    compatible: true,
                    files: [file]
                },
                {
                    title: 'Zu MP3 konvertieren',
                    icon: '🎧',
                    description: 'Audio-Format umwandeln',
                    endpoint: '/v1/media/convert/mp3',
                    params: { media_url: '{{file:0}}' },
                    confidence: 0.60,
                    priority: 'low',
                    compatible: true,
                    files: [file]
                }
            );
        }

        if (file.category === 'image') {
            suggestions.push(
                {
                    title: 'Bild zu Video konvertieren',
                    icon: '🎬',
                    description: 'Statisches Bild als Video',
                    endpoint: '/v1/image/convert/image_to_video',
                    params: { image_url: '{{file:0}}', duration: 5 },
                    confidence: 0.55,
                    priority: 'low',
                    compatible: true,
                    files: [file]
                }
            );
        }

        return suggestions;
    }

    /**
     * Extract media metadata using browser APIs
     * @param {File} file - File object
     * @returns {Promise<Object|null>} Metadata or null
     */
    async extractMediaMetadata(file) {
        return new Promise((resolve) => {
            const element = document.createElement(
                file.type.startsWith('video/') ? 'video' : 'audio'
            );

            element.preload = 'metadata';

            element.onloadedmetadata = () => {
                const metadata = {
                    duration: element.duration,
                    width: element.videoWidth || null,
                    height: element.videoHeight || null,
                    resolution: element.videoWidth ?
                        `${element.videoWidth}x${element.videoHeight}` : null
                };

                console.log(`    ℹ️ Metadata: ${metadata.resolution || 'audio'} - ${this.formatDuration(metadata.duration)}`);

                URL.revokeObjectURL(element.src);
                resolve(metadata);
            };

            element.onerror = () => {
                console.warn(`    ⚠️ Could not extract metadata from ${file.name}`);
                URL.revokeObjectURL(element.src);
                resolve(null);
            };

            element.src = URL.createObjectURL(file);
        });
    }

    /**
     * Check if durations match (within 1 second tolerance)
     * @param {Object} file1 - First file info
     * @param {Object} file2 - Second file info
     * @returns {boolean|null} True if match, false if not, null if unknown
     */
    checkDurationMatch(file1, file2) {
        if (!file1.metadata || !file2.metadata) return null;
        if (!file1.metadata.duration || !file2.metadata.duration) return null;

        const diff = Math.abs(file1.metadata.duration - file2.metadata.duration);
        return diff < 1.0; // Within 1 second
    }

    /**
     * Check if all videos have same resolution
     * @param {Object[]} videos - Array of video file infos
     * @returns {boolean|null} True if match, false if not, null if unknown
     */
    checkResolutionMatch(videos) {
        const resolutions = videos
            .map(v => v.metadata?.resolution)
            .filter(r => r);

        if (resolutions.length === 0) return null;
        if (resolutions.length !== videos.length) return null;

        const first = resolutions[0];
        return resolutions.every(r => r === first);
    }

    /**
     * Check for potential issues
     * @param {Object[]} files - Analyzed files
     * @returns {Object[]} Warnings
     */
    checkWarnings(files) {
        const warnings = [];

        // Check file sizes
        const largeFiles = files.filter(f => f.size > 500 * 1024 * 1024); // >500MB
        if (largeFiles.length > 0) {
            warnings.push({
                type: 'large_file',
                severity: 'warning',
                message: `${largeFiles.length} Datei(en) über 500MB. Upload kann länger dauern.`,
                files: largeFiles
            });
        }

        // Check for unsupported formats
        const unsupported = files.filter(f =>
            !['video', 'audio', 'image', 'subtitle'].includes(f.category)
        );
        if (unsupported.length > 0) {
            warnings.push({
                type: 'unsupported_format',
                severity: 'error',
                message: `${unsupported.length} Datei(en) mit nicht unterstütztem Format`,
                files: unsupported
            });
        }

        // Check for resolution mismatches in video concatenation
        const videos = files.filter(f => f.category === 'video');
        if (videos.length > 1) {
            const resolutionMatch = this.checkResolutionMatch(videos);
            if (resolutionMatch === false) {
                warnings.push({
                    type: 'resolution_mismatch',
                    severity: 'warning',
                    message: 'Videos haben unterschiedliche Auflösungen. Automatische Anpassung wird durchgeführt.',
                    files: videos
                });
            }
        }

        if (warnings.length > 0) {
            console.log(`  ⚠️ Found ${warnings.length} warning(s)`);
        }

        return warnings;
    }

    /**
     * Get file extension
     * @param {string} filename - Filename
     * @returns {string} Extension
     */
    getExtension(filename) {
        return filename.split('.').pop().toLowerCase();
    }

    /**
     * Format duration in seconds to MM:SS
     * @param {number} seconds - Duration in seconds
     * @returns {string} Formatted duration
     */
    formatDuration(seconds) {
        if (!seconds || isNaN(seconds)) return '';

        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    /**
     * Load detection rules (for future extensibility)
     * @returns {Object} Detection rules
     */
    loadDetectionRules() {
        // Could be loaded from config/API in future
        return {
            version: '1.0.0',
            lastUpdated: '2026-01-08'
        };
    }
}

// Make globally available
if (typeof window !== 'undefined') {
    window.SmartFileDetector = SmartFileDetector;
    console.log('✅ SmartFileDetector class loaded');
}
