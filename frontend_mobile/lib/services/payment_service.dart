import 'package:dio/dio.dart';
import '../core/error.dart';
import 'api_service.dart';
import '../models/payment_model.dart';

class PaymentService {
  final ApiService _apiService;

  PaymentService(this._apiService);

  Future<Map<String, dynamic>> createOrder({
    required double amount,
    String currency = 'INR',
    String? description,
  }) async {
    try {
      final response = await _apiService.post(
        '/payments/create-order',
        data: {
          'amount': amount,
          'currency': currency,
          'description': description,
        },
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<PaymentModel> verifyPayment({
    required String orderId,
    required String paymentId,
    required String signature,
  }) async {
    try {
      final response = await _apiService.post(
        '/payments/verify',
        data: {
          'order_id': orderId,
          'payment_id': paymentId,
          'signature': signature,
        },
      );
      final data = response.data as Map<String, dynamic>;
      return PaymentModel.fromJson(
          data['payment'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<List<PaymentModel>> getPaymentHistory({
    int page = 1,
    int limit = 20,
  }) async {
    try {
      final response = await _apiService.get(
        '/payments',
        queryParameters: {'page': page, 'limit': limit},
      );
      final data = response.data as Map<String, dynamic>;
      final payments = data['payments'] as List<dynamic>;
      return payments
          .map((e) => PaymentModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<PaymentModel> getPaymentById(String id) async {
    try {
      final response = await _apiService.get('/payments/$id');
      final data = response.data as Map<String, dynamic>;
      return PaymentModel.fromJson(
          data['payment'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<List<SubscriptionPlan>> getSubscriptionPlans() async {
    try {
      final response = await _apiService.get('/subscriptions/plans');
      final data = response.data as Map<String, dynamic>;
      final plans = data['plans'] as List<dynamic>;
      return plans
          .map((e) =>
              SubscriptionPlan.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<SubscriptionModel> subscribe({
    required String planId,
    required String paymentId,
    bool autoRenew = false,
  }) async {
    try {
      final response = await _apiService.post(
        '/subscriptions',
        data: {
          'plan_id': planId,
          'payment_id': paymentId,
          'auto_renew': autoRenew,
        },
      );
      final data = response.data as Map<String, dynamic>;
      return SubscriptionModel.fromJson(
          data['subscription'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<SubscriptionModel> getCurrentSubscription() async {
    try {
      final response = await _apiService.get('/subscriptions/current');
      final data = response.data as Map<String, dynamic>;
      return SubscriptionModel.fromJson(
          data['subscription'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> cancelSubscription(String id) async {
    try {
      await _apiService.put('/subscriptions/$id/cancel');
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> enableAutoRenew(String id) async {
    try {
      await _apiService.put(
        '/subscriptions/$id/auto-renew',
        data: {'auto_renew': true},
      );
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> disableAutoRenew(String id) async {
    try {
      await _apiService.put(
        '/subscriptions/$id/auto-renew',
        data: {'auto_renew': false},
      );
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }
}
