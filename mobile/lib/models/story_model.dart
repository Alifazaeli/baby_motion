/// Story with embedded translation fields.
class StoryModel {
  const StoryModel({
    required this.id,
    required this.slug,
    required this.categoryId,
    required this.ageGroup,
    required this.durationSeconds,
    required this.coverUrl,
    required this.title,
    this.description,
    required this.manifestUrl,
  });

  final String id;
  final String slug;
  final String categoryId;
  final String ageGroup;
  final int durationSeconds;
  final String coverUrl;
  final String title;
  final String? description;
  final String manifestUrl;

  factory StoryModel.fromJson(Map<String, dynamic> json) => StoryModel(
        id: json['id'] as String,
        slug: json['slug'] as String,
        categoryId: json['category_id'] as String,
        ageGroup: json['age_group'] as String,
        durationSeconds: json['duration_seconds'] as int? ?? 0,
        coverUrl: json['cover_url'] as String? ?? '',
        title: json['title'] as String? ?? '',
        description: json['description'] as String?,
        manifestUrl: json['manifest_url'] as String? ?? '',
      );
}
