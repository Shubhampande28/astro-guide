package com.jyotishguru.app.data

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.Path

interface ApiService {
    @POST("auth/otp/request")
    suspend fun requestOtp(@Body body: OtpRequestBody): Response<Unit>

    @POST("auth/otp/verify")
    suspend fun verifyOtp(@Body body: OtpVerifyBody): TokenResponse

    @POST("auth/guest")
    suspend fun createGuestSession(): TokenResponse

    @POST("me/consent")
    suspend fun giveConsent(): Response<Unit>

    @DELETE("me")
    suspend fun deleteMyData(): Response<Unit>

    @POST("profiles")
    suspend fun createProfile(@Body body: ProfileCreateBody): ProfileResponse

    @GET("profiles")
    suspend fun listProfiles(): List<ProfileResponse>

    @GET("profiles/{id}")
    suspend fun getProfile(@Path("id") id: Int): ProfileResponse

    @PATCH("profiles/{id}")
    suspend fun updateProfile(@Path("id") id: Int, @Body body: ProfileUpdateBody): ProfileResponse

    @GET("profiles/{id}/history")
    suspend fun getHistory(@Path("id") id: Int): List<ChatHistoryItem>

    @POST("profiles/{profileId}/history/{messageId}/feedback")
    suspend fun submitFeedback(
        @Path("profileId") profileId: Int,
        @Path("messageId") messageId: Int,
        @Body body: FeedbackBody,
    ): Response<Unit>

    @POST("chat")
    suspend fun sendChat(@Body body: ChatRequestBody): ChatResponse

    @POST("chart")
    suspend fun computeChart(@Body body: ChartRequestBody): ChartResponse
}
