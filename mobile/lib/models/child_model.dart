/// Child profile with computed age fields from the backend.
class ChildModel {
  const ChildModel({
    required this.id,
    required this.name,
    required this.birthYear,
    required this.birthMonth,
    required this.language,
    required this.ageInMonths,
    this.ageGroup,
    this.nextAgeGroup,
    this.daysToNextAgeGroup,
    required this.hasPendingAgeGroupTransition,
  });

  final String id;
  final String name;
  final int birthYear;
  final int birthMonth;
  final String language;
  final int ageInMonths;
  final String? ageGroup;
  final String? nextAgeGroup;
  final int? daysToNextAgeGroup;
  final bool hasPendingAgeGroupTransition;

  factory ChildModel.fromJson(Map<String, dynamic> json) => ChildModel(
        id: json['id'] as String,
        name: json['name'] as String,
        birthYear: json['birth_year'] as int,
        birthMonth: json['birth_month'] as int,
        language: json['language'] as String,
        ageInMonths: json['age_in_months'] as int,
        ageGroup: json['age_group'] as String?,
        nextAgeGroup: json['next_age_group'] as String?,
        daysToNextAgeGroup: json['days_to_next_age_group'] as int?,
        hasPendingAgeGroupTransition: json['has_pending_age_group_transition'] as bool? ?? false,
      );
}
