import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../auth/providers/auth_provider.dart';
import '../providers/catalog_provider.dart';
import '../widgets/age_transition_banner.dart';
import '../widgets/category_row.dart';
import '../widgets/younger_stories_toggle.dart';

/// FR-A4: Home catalog with categories in horizontal scroll rows.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  void _load() {
    final auth = context.read<AuthProvider>();
    final child = auth.child;
    if (child == null) return;
    context.read<CatalogProvider>().load(
          childId: child.id,
          language: child.language,
        );
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final catalog = context.watch<CatalogProvider>();
    final child = auth.child;

    return Scaffold(
      appBar: AppBar(
        title: Text(child?.name ?? 'Home'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => Navigator.of(context).pushNamed('/settings'),
          ),
        ],
      ),
      body: Builder(builder: (context) {
        if (catalog.isLoading) {
          return const Center(child: CircularProgressIndicator());
        }
        if (catalog.error != null) {
          return Center(child: Text(catalog.error!));
        }
        return RefreshIndicator(
          onRefresh: _load,
          child: CustomScrollView(
            slivers: [
              if (child?.hasPendingAgeGroupTransition == true)
                SliverToBoxAdapter(
                  child: AgeTransitionBanner(child: child!),
                ),
              SliverToBoxAdapter(
                child: YoungerStoriesToggle(
                  value: catalog.includeYounger,
                  onChanged: (_) => catalog.toggleIncludeYounger(
                    childId: child!.id,
                    language: child.language,
                  ),
                ),
              ),
              SliverList(
                delegate: SliverChildBuilderDelegate(
                  (context, i) {
                    final cat = catalog.categories[i];
                    final stories = catalog.storiesByCategory[cat.id] ?? [];
                    if (stories.isEmpty) return const SizedBox.shrink();
                    return CategoryRow(category: cat, stories: stories);
                  },
                  childCount: catalog.categories.length,
                ),
              ),
            ],
          ),
        );
      }),
    );
  }
}
