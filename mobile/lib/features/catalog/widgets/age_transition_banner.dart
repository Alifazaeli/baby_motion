import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/constants/api_constants.dart';
import '../../../core/services/api_service.dart';
import '../../../models/child_model.dart';

/// FR-A11: One-time banner shown when a child enters a new age group.
class AgeTransitionBanner extends StatelessWidget {
  const AgeTransitionBanner({super.key, required this.child});

  final ChildModel child;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.primaryContainer,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          const Text('🎉', style: TextStyle(fontSize: 28)),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              '${child.name} is now ${child.ageInMonths} months old! New stories have been unlocked.',
              style: theme.textTheme.bodyLarge,
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close),
            onPressed: () => _dismiss(context),
          ),
        ],
      ),
    );
  }

  Future<void> _dismiss(BuildContext context) async {
    try {
      await context.read<ApiService>().post<void>(ApiConstants.acknowledgeAgeGroup(child.id));
    } catch (_) {}
  }
}
