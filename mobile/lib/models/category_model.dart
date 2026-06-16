/// Story category with localized name.
class CategoryModel {
  const CategoryModel({
    required this.id,
    required this.slug,
    required this.name,
    this.iconUrl,
    required this.displayOrder,
  });

  final String id;
  final String slug;
  final String name;
  final String? iconUrl;
  final int displayOrder;

  factory CategoryModel.fromJson(Map<String, dynamic> json) => CategoryModel(
        id: json['id'] as String,
        slug: json['slug'] as String,
        name: json['name'] as String? ?? json['slug'] as String,
        iconUrl: json['icon_url'] as String?,
        displayOrder: json['display_order'] as int? ?? 0,
      );
}
