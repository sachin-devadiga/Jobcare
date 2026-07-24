import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import '../core/error.dart';

class LocationState {
  final Position? position;
  final String? address;
  final String? city;
  final bool isLoading;
  final bool permissionDenied;
  final Failure? failure;

  const LocationState({
    this.position,
    this.address,
    this.city,
    this.isLoading = false,
    this.permissionDenied = false,
    this.failure,
  });

  LocationState copyWith({
    Position? position,
    String? address,
    String? city,
    bool? isLoading,
    bool? permissionDenied,
    Failure? failure,
  }) {
    return LocationState(
      position: position ?? this.position,
      address: address ?? this.address,
      city: city ?? this.city,
      isLoading: isLoading ?? this.isLoading,
      permissionDenied: permissionDenied ?? this.permissionDenied,
      failure: failure,
    );
  }
}

class LocationNotifier extends StateNotifier<LocationState> {
  LocationNotifier() : super(const LocationState());

  Future<void> getCurrentLocation() async {
    state = state.copyWith(isLoading: true);
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        state = state.copyWith(
          isLoading: false,
          failure: const Failure(
            message: 'Location services are disabled',
          ),
        );
        return;
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          state = state.copyWith(
            isLoading: false,
            permissionDenied: true,
            failure: const Failure(
              message: ErrorMessages.locationPermissionDenied,
            ),
          );
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        state = state.copyWith(
          isLoading: false,
          permissionDenied: true,
          failure: const Failure(
            message:
                'Location permissions are permanently denied. Please enable from settings.',
          ),
        );
        return;
      }

      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      await _getAddressFromPosition(position);
      state = state.copyWith(
        position: position,
        isLoading: false,
        permissionDenied: false,
        failure: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        failure: const Failure(message: 'Failed to get location'),
      );
    }
  }

  Future<void> _getAddressFromPosition(Position position) async {
    try {
      final placemarks = await placemarkFromCoordinates(
        position.latitude,
        position.longitude,
      );
      if (placemarks.isNotEmpty) {
        final place = placemarks.first;
        final addressParts = [
          place.subLocality,
          place.locality,
          place.administrativeArea,
        ].where((p) => p != null && p.isNotEmpty).toList();
        state = state.copyWith(
          address: addressParts.join(', '),
          city: place.locality,
        );
      }
    } catch (_) {
      state = state.copyWith(
        address: '${position.latitude}, ${position.longitude}',
      );
    }
  }

  void setLocation(Position position) {
    state = state.copyWith(position: position);
    _getAddressFromPosition(position);
  }

  void clearFailure() {
    state = state.copyWith(failure: null);
  }
}
