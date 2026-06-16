/// Story manifest downloaded from Arvan Cloud CDN.
///
/// Contains audio URL and per-scene image + timing data for the player.
class ManifestModel {
  const ManifestModel({
    required this.storyId,
    required this.slug,
    required this.language,
    required this.title,
    required this.durationSeconds,
    required this.audioUrl,
    required this.scenes,
  });

  final String storyId;
  final String slug;
  final String language;
  final String title;
  final int durationSeconds;
  final String audioUrl;
  final List<SceneModel> scenes;

  factory ManifestModel.fromJson(Map<String, dynamic> json) => ManifestModel(
        storyId: json['story_id'] as String,
        slug: json['slug'] as String,
        language: json['language'] as String,
        title: json['title'] as String,
        durationSeconds: json['duration_seconds'] as int,
        audioUrl: json['audio_url'] as String,
        scenes: (json['scenes'] as List)
            .map((s) => SceneModel.fromJson(s as Map<String, dynamic>))
            .toList(),
      );
}

/// A single scene in a story manifest.
class SceneModel {
  const SceneModel({
    required this.index,
    required this.imageUrl,
    required this.text,
    required this.audioStartSec,
    required this.audioEndSec,
  });

  final int index;
  final String imageUrl;
  final String text;
  final double audioStartSec;
  final double audioEndSec;

  factory SceneModel.fromJson(Map<String, dynamic> json) => SceneModel(
        index: json['index'] as int,
        imageUrl: json['image_url'] as String,
        text: json['text'] as String,
        audioStartSec: (json['audio_start_sec'] as num).toDouble(),
        audioEndSec: (json['audio_end_sec'] as num).toDouble(),
      );
}
