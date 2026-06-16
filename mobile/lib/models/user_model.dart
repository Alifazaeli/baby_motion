/// Authenticated parent user.
class UserModel {
  const UserModel({
    required this.id,
    required this.email,
    required this.displayName,
    required this.preferredLanguage,
    required this.plan,
  });

  final String id;
  final String email;
  final String displayName;
  final String preferredLanguage;
  final String plan;

  factory UserModel.fromJson(Map<String, dynamic> json) => UserModel(
        id: json['id'] as String,
        email: json['email'] as String? ?? '',
        displayName: json['display_name'] as String? ?? '',
        preferredLanguage: json['preferred_language'] as String? ?? 'en',
        plan: json['plan'] as String? ?? 'free',
      );
}
