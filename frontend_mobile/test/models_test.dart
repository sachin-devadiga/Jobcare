import 'package:flutter_test/flutter_test.dart';
import '../lib/models/user_model.dart';
import '../lib/models/job_model.dart';
import '../lib/models/application_model.dart';
import '../lib/models/employee_profile_model.dart';
import '../lib/models/notification_model.dart';
import '../lib/models/category_model.dart';
import '../lib/models/voice_session_model.dart';
import '../lib/models/payment_model.dart';

final DateTime now = DateTime.now();

void main() {
  group('UserModel', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 'u1',
        'email': 'test@test.com',
        'phone': '9876543210',
        'name': 'Test User',
        'role': 'employee',
        'profile_image': 'https://example.com/pic.jpg',
        'auth_provider': 'email',
        'is_email_verified': true,
        'is_phone_verified': false,
        'is_profile_complete': true,
        'language': 'en',
        'created_at': now.toIso8601String(),
        'updated_at': now.toIso8601String(),
      };

      final user = UserModel.fromJson(json);

      expect(user.id, 'u1');
      expect(user.email, 'test@test.com');
      expect(user.name, 'Test User');
      expect(user.role, UserRole.employee);
      expect(user.profileImage, 'https://example.com/pic.jpg');
      expect(user.authProvider, AuthProvider.email);
      expect(user.isEmailVerified, true);
      expect(user.language, 'en');
    });

    test('toJson and fromJson are symmetric', () {
      final user = UserModel(
        id: 'u1',
        email: 'test@test.com',
        name: 'Test',
        role: UserRole.employee,
        createdAt: now,
        updatedAt: now,
      );

      final json = user.toJson();
      final restored = UserModel.fromJson(json);

      expect(restored.id, user.id);
      expect(restored.email, user.email);
      expect(restored.name, user.name);
      expect(restored.role, user.role);
    });

    test('copyWith preserves unchanged fields', () {
      final user = UserModel(
        id: 'u1', email: 'a@b.com', name: 'A',
        role: UserRole.employee, createdAt: now, updatedAt: now,
      );

      final copy = user.copyWith(name: 'B');

      expect(copy.id, 'u1');
      expect(copy.email, 'a@b.com');
      expect(copy.name, 'B');
    });
  });

  group('JobModel', () {
    test('fromJson parses all fields', () {
      final json = {
        'id': 'j1',
        'employer_id': 'e1',
        'company_id': 'c1',
        'title': 'Software Engineer',
        'description': 'Build apps',
        'job_type': 'full_time',
        'shift_type': 'day',
        'salary_type': 'range',
        'salary_min': 50000,
        'salary_max': 80000,
        'salary_currency': 'INR',
        'salary_period': 'monthly',
        'urgency': 'normal',
        'status': 'active',
        'experience_level': 'mid',
        'experience_min': 2,
        'experience_max': 5,
        'education_required': 'B.Tech',
        'required_skills': ['Flutter', 'Dart'],
        'location': 'Bangalore',
        'city': 'Bangalore',
        'state': 'Karnataka',
        'open_positions': 3,
        'applicants_count': 10,
        'category_name': 'IT',
        'is_remote': true,
        'is_featured': true,
        'is_urgent': false,
        'is_saved': true,
        'has_applied': false,
        'created_at': now.toIso8601String(),
        'updated_at': now.toIso8601String(),
      };

      final job = JobModel.fromJson(json);

      expect(job.id, 'j1');
      expect(job.title, 'Software Engineer');
      expect(job.jobType, JobType.fullTime);
      expect(job.salaryMin, 50000);
      expect(job.salaryMax, 80000);
      expect(job.isRemote, true);
      expect(job.isSaved, true);
      expect(job.hasApplied, false);
      expect(job.requiredSkills, ['Flutter', 'Dart']);
      expect(job.city, 'Bangalore');
    });

    test('toJson and fromJson are symmetric', () {
      final job = JobModel(
        id: 'j1', title: 'Test', companyId: 'c1', employerId: 'e1',
        jobType: JobType.fullTime, createdAt: now, updatedAt: now,
      );

      final json = job.toJson();
      final restored = JobModel.fromJson(json);

      expect(restored.id, job.id);
      expect(restored.title, job.title);
      expect(restored.jobType, job.jobType);
    });
  });

  group('ApplicationModel', () {
    test('fromJson parses with interview', () {
      final json = {
        'id': 'a1',
        'job_id': 'j1',
        'user_id': 'u1',
        'employer_id': 'e1',
        'status': 'shortlisted',
        'cover_letter': 'I am a good fit',
        'resume_url': 'https://example.com/resume.pdf',
        'interview': {
          'id': 'iv1',
          'scheduled_at': now.toIso8601String(),
          'interview_type': 'video',
          'meeting_link': 'https://meet.google.com/abc',
          'status': 'scheduled',
        },
        'applied_at': now.toIso8601String(),
        'created_at': now.toIso8601String(),
        'updated_at': now.toIso8601String(),
      };

      final app = ApplicationModel.fromJson(json);

      expect(app.id, 'a1');
      expect(app.status, ApplicationStatus.shortlisted);
      expect(app.interview, isNotNull);
      expect(app.interview!.interviewType, 'video');
      expect(app.interview!.meetingLink, 'https://meet.google.com/abc');
    });
  });

  group('EmployeeProfileModel', () {
    test('fromJson parses with nested objects', () {
      final json = {
        'id': 'p1',
        'user_id': 'u1',
        'full_name': 'John',
        'skills': ['Flutter', 'Dart'],
        'experiences': [
          {
            'id': 'ex1',
            'company': 'Tech Co',
            'role': 'Developer',
            'start_date': now.toIso8601String(),
            'is_current': true,
          }
        ],
        'education': [
          {
            'id': 'ed1',
            'institution': 'MIT',
            'degree': 'B.Tech',
            'start_date': now.toIso8601String(),
          }
        ],
        'is_available': true,
        'created_at': now.toIso8601String(),
        'updated_at': now.toIso8601String(),
      };

      final profile = EmployeeProfileModel.fromJson(json);

      expect(profile.fullName, 'John');
      expect(profile.skills, ['Flutter', 'Dart']);
      expect(profile.experiences.length, 1);
      expect(profile.experiences.first.company, 'Tech Co');
      expect(profile.education.length, 1);
      expect(profile.education.first.institution, 'MIT');
    });

    test('completionScore calculates correctly', () {
      final profile = EmployeeProfileModel(
        id: 'p1', userId: 'u1',
        fullName: 'John',
        phone: '9999999999',
        skills: ['Flutter'],
        experiences: [Experience(
          id: 'ex1', company: 'Co', role: 'Dev',
          startDate: now, isCurrent: true,
        )],
        education: [Education(
          id: 'ed1', institution: 'MIT', degree: 'B.Tech',
          startDate: now,
        )],
        resumeUrl: 'https://resume.url',
        expectedSalary: '50000',
        city: 'Bangalore',
        createdAt: now, updatedAt: now,
      );

      expect(profile.completionScore, greaterThan(0));
    });
  });

  group('NotificationModel', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 'n1',
        'user_id': 'u1',
        'type': 'job_alert',
        'title': 'New Job Alert',
        'body': 'Check out this job',
        'is_read': false,
        'created_at': now.toIso8601String(),
      };

      final notif = NotificationModel.fromJson(json);

      expect(notif.type, NotificationType.jobAlert);
      expect(notif.title, 'New Job Alert');
      expect(notif.isRead, false);
    });
  });

  group('CategoryModel', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 'c1',
        'name': 'IT',
        'icon': 'code',
        'job_count': 25,
        'is_active': true,
        'sort_order': 1,
        'created_at': now.toIso8601String(),
        'updated_at': now.toIso8601String(),
      };

      final cat = CategoryModel.fromJson(json);

      expect(cat.name, 'IT');
      expect(cat.jobCount, 25);
      expect(cat.isActive, true);
    });
  });

  group('VoiceCommandResult', () {
    test('fromJson parses search command', () {
      final json = {
        'type': 'search',
        'command': 'find jobs',
        'transcript': 'find me some jobs',
        'parsed_data': {'query': 'driver'},
        'action': 'search',
        'response_text': 'Found 5 jobs',
      };

      final result = VoiceCommandResult.fromJson(json);

      expect(result.type, VoiceCommandType.search);
      expect(result.command, 'find jobs');
      expect(result.responseText, 'Found 5 jobs');
    });
  });

  group('PaymentModel', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 'pay1',
        'user_id': 'u1',
        'amount': 499.0,
        'currency': 'INR',
        'status': 'success',
        'payment_method': 'upi',
        'transaction_id': 'txn123',
        'created_at': now.toIso8601String(),
        'updated_at': now.toIso8601String(),
      };

      final payment = PaymentModel.fromJson(json);

      expect(payment.amount, 499.0);
      expect(payment.status, PaymentStatus.success);
      expect(payment.paymentMethod, 'upi');
    });
  });

  group('Enum extensions', () {
    test('UserRole.fromString handles all cases', () {
      expect(UserRole.fromString('employee'), UserRole.employee);
      expect(UserRole.fromString('EMPLOYER'), UserRole.employer);
      expect(UserRole.fromString('Admin'), UserRole.admin);
      expect(UserRole.fromString('unknown'), UserRole.employee);
    });

    test('JobType.fromString handles all cases', () {
      expect(JobType.fromString('full_time'), JobType.fullTime);
      expect(JobType.fromString('part_time'), JobType.partTime);
      expect(JobType.fromString('internship'), JobType.internship);
    });

    test('ApplicationStatus.fromString handles all cases', () {
      expect(ApplicationStatus.fromString('applied'), ApplicationStatus.applied);
      expect(ApplicationStatus.fromString('shortlisted'), ApplicationStatus.shortlisted);
      expect(ApplicationStatus.fromString('rejected'), ApplicationStatus.rejected);
      expect(ApplicationStatus.fromString('withdrawn'), ApplicationStatus.withdrawn);
    });
  });
}
