import 'dart:convert';

enum VoiceCommandType {
  search,
  apply,
  save,
  filter,
  navigate,
  read,
  help,
  unknown;

  String get value {
    switch (this) {
      case VoiceCommandType.search:
        return 'search';
      case VoiceCommandType.apply:
        return 'apply';
      case VoiceCommandType.save:
        return 'save';
      case VoiceCommandType.filter:
        return 'filter';
      case VoiceCommandType.navigate:
        return 'navigate';
      case VoiceCommandType.read:
        return 'read';
      case VoiceCommandType.help:
        return 'help';
      case VoiceCommandType.unknown:
        return 'unknown';
    }
  }

  static VoiceCommandType fromString(String value) {
    switch (value.toLowerCase()) {
      case 'search':
        return VoiceCommandType.search;
      case 'apply':
        return VoiceCommandType.apply;
      case 'save':
        return VoiceCommandType.save;
      case 'filter':
        return VoiceCommandType.filter;
      case 'navigate':
        return VoiceCommandType.navigate;
      case 'read':
        return VoiceCommandType.read;
      case 'help':
        return VoiceCommandType.help;
      default:
        return VoiceCommandType.unknown;
    }
  }
}

class VoiceCommandResult {
  final VoiceCommandType type;
  final String command;
  final String? transcript;
  final Map<String, dynamic>? parsedData;
  final String? action;
  final String? responseText;

  const VoiceCommandResult({
    required this.type,
    required this.command,
    this.transcript,
    this.parsedData,
    this.action,
    this.responseText,
  });

  factory VoiceCommandResult.fromJson(Map<String, dynamic> json) {
    return VoiceCommandResult(
      type: VoiceCommandType.fromString(
          json['type'] as String? ?? 'unknown'),
      command: json['command'] as String,
      transcript: json['transcript'] as String?,
      parsedData: json['parsed_data'] as Map<String, dynamic>?,
      action: json['action'] as String?,
      responseText: json['response_text'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'type': type.value,
    'command': command,
    'transcript': transcript,
    'parsed_data': parsedData,
    'action': action,
    'response_text': responseText,
  };
}

class VoiceSessionModel {
  final String id;
  final String userId;
  final String? inputText;
  final String? inputAudioUrl;
  final String? outputText;
  final String? outputAudioUrl;
  final VoiceCommandType commandType;
  final String? language;
  final double? confidence;
  final double? processingTime;
  final bool isSuccessful;
  final String? errorMessage;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;

  const VoiceSessionModel({
    required this.id,
    required this.userId,
    this.inputText,
    this.inputAudioUrl,
    this.outputText,
    this.outputAudioUrl,
    this.commandType = VoiceCommandType.unknown,
    this.language,
    this.confidence,
    this.processingTime,
    this.isSuccessful = true,
    this.errorMessage,
    this.metadata,
    required this.createdAt,
  });

  factory VoiceSessionModel.fromJson(Map<String, dynamic> json) {
    return VoiceSessionModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      inputText: json['input_text'] as String?,
      inputAudioUrl: json['input_audio_url'] as String?,
      outputText: json['output_text'] as String?,
      outputAudioUrl: json['output_audio_url'] as String?,
      commandType: VoiceCommandType.fromString(
          json['command_type'] as String? ?? 'unknown'),
      language: json['language'] as String?,
      confidence: (json['confidence'] as num?)?.toDouble(),
      processingTime: (json['processing_time'] as num?)?.toDouble(),
      isSuccessful: json['is_successful'] as bool? ?? true,
      errorMessage: json['error_message'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'user_id': userId,
    'input_text': inputText,
    'input_audio_url': inputAudioUrl,
    'output_text': outputText,
    'output_audio_url': outputAudioUrl,
    'command_type': commandType.value,
    'language': language,
    'confidence': confidence,
    'processing_time': processingTime,
    'is_successful': isSuccessful,
    'error_message': errorMessage,
    'metadata': metadata,
    'created_at': createdAt.toIso8601String(),
  };

  String toJsonString() => json.encode(toJson());

  factory VoiceSessionModel.fromJsonString(String str) =>
      VoiceSessionModel.fromJson(
          json.decode(str) as Map<String, dynamic>);

  VoiceSessionModel copyWith({
    String? id,
    String? userId,
    String? inputText,
    String? inputAudioUrl,
    String? outputText,
    String? outputAudioUrl,
    VoiceCommandType? commandType,
    String? language,
    double? confidence,
    double? processingTime,
    bool? isSuccessful,
    String? errorMessage,
    Map<String, dynamic>? metadata,
    DateTime? createdAt,
  }) {
    return VoiceSessionModel(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      inputText: inputText ?? this.inputText,
      inputAudioUrl: inputAudioUrl ?? this.inputAudioUrl,
      outputText: outputText ?? this.outputText,
      outputAudioUrl: outputAudioUrl ?? this.outputAudioUrl,
      commandType: commandType ?? this.commandType,
      language: language ?? this.language,
      confidence: confidence ?? this.confidence,
      processingTime: processingTime ?? this.processingTime,
      isSuccessful: isSuccessful ?? this.isSuccessful,
      errorMessage: errorMessage ?? this.errorMessage,
      metadata: metadata ?? this.metadata,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
