/// Client-side age group helpers (mirrors backend services.py logic).
///
/// Kept here so the UI can compute values locally without an extra round-trip.
class AgeGroupUtils {
  AgeGroupUtils._();

  static const _boundaries = [
    (18, '12_18m'),
    (30, '18_30m'),
    (42, '30_42m'),
    (60, '42_60m'),
  ];

  static int ageInMonths(int birthYear, int birthMonth) {
    final now = DateTime.now();
    return (now.year - birthYear) * 12 + (now.month - birthMonth);
  }

  static String? ageGroup(int birthYear, int birthMonth) {
    final months = ageInMonths(birthYear, birthMonth);
    if (months < 12) return null;
    for (final (threshold, group) in _boundaries) {
      if (months < threshold) return group;
    }
    return '60m_plus';
  }

  static String displayLabel(String? group) => switch (group) {
        '12_18m' => '12–18 months',
        '18_30m' => '18–30 months',
        '30_42m' => '30–42 months',
        '42_60m' => '42–60 months',
        '60m_plus' => '60+ months',
        _ => 'Too young',
      };
}
