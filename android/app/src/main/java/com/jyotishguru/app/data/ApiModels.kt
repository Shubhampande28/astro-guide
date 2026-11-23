package com.jyotishguru.app.data

import com.google.gson.annotations.SerializedName

// --- Auth ---

data class OtpRequestBody(@SerializedName("phone_number") val phoneNumber: String)

data class OtpVerifyBody(
    @SerializedName("phone_number") val phoneNumber: String,
    val code: String,
)

data class TokenResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("token_type") val tokenType: String,
)

// --- Profiles ---

data class ProfileCreateBody(
    val name: String,
    val relation: String,
    val language: String,
    @SerializedName("birth_date") val birthDate: String, // "YYYY-MM-DD"
    @SerializedName("birth_time") val birthTime: String?, // "HH:MM:SS"
    @SerializedName("birth_time_unknown") val birthTimeUnknown: Boolean,
    val latitude: Double,
    val longitude: Double,
    val timezone: String,
)

data class ProfileUpdateBody(
    val name: String? = null,
    val language: String? = null,
)

data class ProfileResponse(
    val id: Int,
    val name: String,
    val relation: String,
    val language: String,
    @SerializedName("birth_date") val birthDate: String,
    @SerializedName("birth_time") val birthTime: String?,
    @SerializedName("birth_time_unknown") val birthTimeUnknown: Boolean,
    val latitude: Double,
    val longitude: Double,
    val timezone: String,
    @SerializedName("created_at") val createdAt: String,
)

// --- Chat ---

data class ChatRequestBody(
    @SerializedName("profile_id") val profileId: Int,
    val message: String,
    @SerializedName("previous_topic") val previousTopic: String? = null,
    val language: String? = null,
)

data class ChatResponse(
    @SerializedName("message_id") val messageId: Int,
    val topic: String?,
    val summary: String,
    val why: List<String>,
    val sources: List<String>,
    val timing: List<String>,
    val remedies: List<String>,
    val confidence: String,
    val language: String,
    @SerializedName("is_safety_response") val isSafetyResponse: Boolean,
    @SerializedName("is_declined") val isDeclined: Boolean,
    @SerializedName("is_clarifying_question") val isClarifyingQuestion: Boolean,
    @SerializedName("ai_rewritten_summary") val aiRewrittenSummary: String?,
)

data class ChatHistoryItem(
    val id: Int,
    @SerializedName("message_text") val messageText: String,
    val topic: String?,
    val summary: String,
    val language: String,
    val confidence: String,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("is_accurate") val isAccurate: Boolean?,
)

data class FeedbackBody(@SerializedName("is_accurate") val isAccurate: Boolean)

// --- Chart (Kundli) ---

data class ChartRequestBody(
    @SerializedName("birth_date") val birthDate: String,
    @SerializedName("birth_time") val birthTime: String,
    val timezone: String,
    val latitude: Double,
    val longitude: Double,
)

data class LagnaResponse(
    @SerializedName("sidereal_longitude_deg") val siderealLongitudeDeg: Double,
    val sign: String,
    @SerializedName("degree_in_sign") val degreeInSign: Double,
    val nakshatra: String,
    val pada: Int,
)

data class GrahaResponse(
    val graha: String,
    @SerializedName("sidereal_longitude_deg") val siderealLongitudeDeg: Double,
    val sign: String,
    @SerializedName("degree_in_sign") val degreeInSign: Double,
    val nakshatra: String,
    val pada: Int,
    val house: Int,
    val dignity: String,
    val retrograde: Boolean,
    @SerializedName("navamsa_sign") val navamsaSign: String,
)

data class AntarDashaResponse(
    val lord: String,
    val start: String,
    val end: String,
)

data class MahaDashaResponse(
    val lord: String,
    val start: String,
    val end: String,
    @SerializedName("antar_dashas") val antarDashas: List<AntarDashaResponse>,
)

data class ChartResponse(
    @SerializedName("birth_utc") val birthUtc: String,
    @SerializedName("ayanamsa_deg") val ayanamsaDeg: Double,
    val lagna: LagnaResponse,
    val grahas: List<GrahaResponse>,
    val vimshottari: List<MahaDashaResponse>,
    @SerializedName("current_maha_dasha") val currentMahaDasha: String?,
    @SerializedName("current_antar_dasha") val currentAntarDasha: String?,
)

// The 8 topics the backend's rules engine understands, for the chip row.
val TOPICS = listOf(
    "career", "marriage", "money", "health",
    "education", "foreign_travel", "children", "property",
)
