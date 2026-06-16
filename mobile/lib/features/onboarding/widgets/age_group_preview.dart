import 'package:flutter/material.dart';

import '../../../core/utils/age_group_utils.dart';

/// Live preview of the computed age group shown during onboarding (FR-A3).
class AgeGroupPreview extends StatelessWidget {
  const AgeGroupPreview({super.key, required this.birthYear, required this.birthMonth});

  final int birthYear;
  final int birthMonth;

  @override
  Widget build(BuildContext context) {
    final group = AgeGroupUtils.ageGroup(birthYear, birthMonth);
    final label = AgeGroupUtils.displayLabel(group);
    final months = AgeGroupUtils.ageInMonths(birthYear, birthMonth);
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.primaryContainer,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Icon(Icons.child_care, color: theme.colorScheme.primary),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Age group: $label', style: theme.textTheme.titleLarge),
              Text('$months months old', style: theme.textTheme.bodyMedium),
            ],
          ),
        ],
      ),
    );
  }
}
