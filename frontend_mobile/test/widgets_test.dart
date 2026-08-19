import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../lib/models/application_model.dart';
import '../lib/models/company_model.dart';
import '../lib/models/job_model.dart';
import '../lib/widgets/empty_state.dart';
import '../lib/widgets/glass_card.dart';
import '../lib/widgets/gradient_button.dart';
import '../lib/widgets/job_card.dart';
import '../lib/widgets/rating_bar_widget.dart';
import '../lib/widgets/section_header.dart';
import '../lib/widgets/skill_chip.dart';
import '../lib/widgets/status_badge.dart';

final DateTime now = DateTime.now();

Widget wrapWithMaterial(Widget widget) {
  return ProviderScope(child: MaterialApp(home: Scaffold(body: widget)));
}

void main() {
  group('JobCard', () {
    testWidgets('displays job information correctly', (tester) async {
      final job = JobModel(
        id: '1', title: 'Software Engineer',
        companyId: 'c1', employerId: 'e1',
        company: CompanyModel(id: '1', name: 'Tech Corp', createdAt: now, updatedAt: now),
        salaryMin: 50000, salaryMax: 80000,
        location: 'Bangalore',
        jobType: JobType.fullTime, createdAt: now, updatedAt: now,
      );
      await tester.pumpWidget(wrapWithMaterial(JobCard(job: job)));
      await tester.pumpAndSettle();
      expect(find.text('Software Engineer'), findsOneWidget);
      expect(find.text('Tech Corp'), findsOneWidget);
    });

    testWidgets('shows bookmark icon', (tester) async {
      final job = JobModel(
        id: '1', title: 'Flutter Developer',
        companyId: 'c1', employerId: 'e1',
        company: CompanyModel(id: '1', name: 'App Co', createdAt: now, updatedAt: now),
        jobType: JobType.fullTime, createdAt: now, updatedAt: now,
      );
      await tester.pumpWidget(wrapWithMaterial(JobCard(job: job, onSave: () {})));
      await tester.pumpAndSettle();
      expect(find.byIcon(Icons.bookmark_outline), findsOneWidget);
    });

    testWidgets('shows saved state with filled bookmark', (tester) async {
      final job = JobModel(
        id: '1', title: 'Flutter Developer',
        companyId: 'c1', employerId: 'e1',
        company: CompanyModel(id: '1', name: 'App Co', createdAt: now, updatedAt: now),
        isSaved: true, jobType: JobType.fullTime, createdAt: now, updatedAt: now,
      );
      await tester.pumpWidget(wrapWithMaterial(JobCard(job: job, onSave: () {})));
      await tester.pumpAndSettle();
      expect(find.byIcon(Icons.bookmark), findsOneWidget);
    });

    testWidgets('shows location when provided', (tester) async {
      final job = JobModel(
        id: '1', title: 'Driver', companyId: 'c1', employerId: 'e1',
        company: CompanyModel(id: '1', name: 'Trans Co', createdAt: now, updatedAt: now),
        city: 'Mumbai', jobType: JobType.fullTime, createdAt: now, updatedAt: now,
      );
      await tester.pumpWidget(wrapWithMaterial(JobCard(job: job)));
      await tester.pumpAndSettle();
      expect(find.text('Mumbai'), findsOneWidget);
    });

    testWidgets('calls onTap when tapped', (tester) async {
      bool tapped = false;
      final job = JobModel(
        id: '1', title: 'Test Job', companyId: 'c1', employerId: 'e1',
        company: CompanyModel(id: '1', name: 'Co', createdAt: now, updatedAt: now),
        jobType: JobType.fullTime, createdAt: now, updatedAt: now,
      );
      await tester.pumpWidget(wrapWithMaterial(JobCard(job: job, onTap: () => tapped = true)));
      await tester.tap(find.text('Test Job'));
      await tester.pumpAndSettle();
      expect(tapped, true);
    });
  });

  group('GlassCard', () {
    testWidgets('renders children', (tester) async {
      await tester.pumpWidget(wrapWithMaterial(
        const GlassCard(child: Text('Card Content')),
      ));
      expect(find.text('Card Content'), findsOneWidget);
    });
  });

  group('GradientButton', () {
    testWidgets('renders text', (tester) async {
      await tester.pumpWidget(wrapWithMaterial(
        const GradientButton(onPressed: null, text: 'Submit'),
      ));
      expect(find.text('Submit'), findsOneWidget);
    });

    testWidgets('shows loading indicator when loading', (tester) async {
      await tester.pumpWidget(wrapWithMaterial(
        const GradientButton(onPressed: null, text: 'Submit', isLoading: true),
      ));
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.text('Submit'), findsNothing);
    });
  });

  group('EmptyState', () {
    testWidgets('shows title and message', (tester) async {
      await tester.pumpWidget(wrapWithMaterial(
        const EmptyState(icon: Icons.info, title: 'Empty', message: 'Nothing here'),
      ));
      expect(find.text('Empty'), findsOneWidget);
      expect(find.text('Nothing here'), findsOneWidget);
    });
  });

  group('StatusBadge', () {
    testWidgets('renders with applied status', (tester) async {
      await tester.pumpWidget(wrapWithMaterial(
        const StatusBadge(status: ApplicationStatus.applied),
      ));
      expect(find.text('Applied'), findsOneWidget);
    });
  });

  group('SkillChip', () {
    testWidgets('renders skill label', (tester) async {
      await tester.pumpWidget(wrapWithMaterial(
        const SkillChip(label: 'Flutter'),
      ));
      expect(find.text('Flutter'), findsOneWidget);
    });
  });

  group('SectionHeader', () {
    testWidgets('renders title', (tester) async {
      await tester.pumpWidget(wrapWithMaterial(
        const SectionHeader(title: 'My Section'),
      ));
      expect(find.text('My Section'), findsOneWidget);
    });

    testWidgets('shows see all button when provided', (tester) async {
      await tester.pumpWidget(wrapWithMaterial(
        SectionHeader(title: 'Section', onSeeAll: () {}),
      ));
      expect(find.text('See All'), findsOneWidget);
    });
  });

  group('RatingBar', () {
    testWidgets('renders with given rating', (tester) async {
      await tester.pumpWidget(wrapWithMaterial(
        const RatingBarWidget(rating: 4.5, itemSize: 20),
      ));
      expect(find.byType(RatingBarWidget), findsOneWidget);
    });
  });
}
