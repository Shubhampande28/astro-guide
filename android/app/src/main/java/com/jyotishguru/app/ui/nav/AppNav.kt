package com.jyotishguru.app.ui.nav

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.jyotishguru.app.data.ApiService
import com.jyotishguru.app.data.IndiaPlacesRepository
import com.jyotishguru.app.data.TokenStore
import com.jyotishguru.app.ui.home.HomeScreen
import com.jyotishguru.app.ui.kundli.KundliScreen
import com.jyotishguru.app.ui.login.ConsentScreen
import com.jyotishguru.app.ui.login.LoginScreen
import com.jyotishguru.app.ui.login.WelcomeScreen
import com.jyotishguru.app.ui.onboarding.OnboardingScreen

object Routes {
    const val SPLASH = "splash"
    const val WELCOME = "welcome"
    const val LOGIN = "login"
    const val CONSENT = "consent"
    const val ONBOARDING = "onboarding?family={family}"
    const val HOME = "home"
    const val KUNDLI = "kundli"

    fun onboarding(isAddingFamilyMember: Boolean) = "onboarding?family=$isAddingFamilyMember"
}

@Composable
fun AppNavHost(api: ApiService, tokenStore: TokenStore, indiaPlaces: IndiaPlacesRepository) {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = Routes.SPLASH) {
        composable(Routes.SPLASH) {
            SplashGate(api = api, tokenStore = tokenStore, navController = navController)
        }
        composable(Routes.WELCOME) {
            WelcomeScreen(
                api = api,
                tokenStore = tokenStore,
                onReady = { navController.navigateAndClear(Routes.CONSENT) },
                onSignIn = { navController.navigate(Routes.LOGIN) },
            )
        }
        composable(Routes.LOGIN) {
            LoginScreen(
                api = api,
                tokenStore = tokenStore,
                onLoggedIn = { navController.navigateAndClear(Routes.CONSENT) },
            )
        }
        composable(Routes.CONSENT) {
            ConsentScreen(
                api = api,
                onConsented = {
                    navController.navigateAndClear(Routes.onboarding(isAddingFamilyMember = false))
                },
            )
        }
        composable(
            Routes.ONBOARDING,
            arguments = listOf(navArgument("family") { type = NavType.BoolType; defaultValue = false }),
        ) { backStackEntry ->
            val isAddingFamilyMember = backStackEntry.arguments?.getBoolean("family") ?: false
            OnboardingScreen(
                api = api,
                indiaPlaces = indiaPlaces,
                isAddingFamilyMember = isAddingFamilyMember,
                onProfileCreated = { profileId ->
                    tokenStore.activeProfileId = profileId
                    navController.navigateAndClear(Routes.HOME)
                },
            )
        }
        composable(Routes.HOME) {
            HomeScreen(
                api = api,
                tokenStore = tokenStore,
                onAddProfile = { navController.navigate(Routes.onboarding(isAddingFamilyMember = true)) },
                onViewKundli = { navController.navigate(Routes.KUNDLI) },
                onLoggedOut = { navController.navigateAndClear(Routes.WELCOME) },
            )
        }
        composable(Routes.KUNDLI) {
            KundliScreen(api = api, tokenStore = tokenStore, onBack = { navController.popBackStack() })
        }
    }
}

private fun NavHostController.navigateAndClear(route: String) {
    navigate(route) {
        popUpTo(0) { inclusive = true }
    }
}

@Composable
private fun SplashGate(api: ApiService, tokenStore: TokenStore, navController: NavHostController) {
    var checked by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        val token = tokenStore.token
        val destination = if (token == null) {
            Routes.WELCOME
        } else {
            try {
                val profiles = api.listProfiles()
                if (profiles.isEmpty()) {
                    Routes.onboarding(isAddingFamilyMember = false)
                } else {
                    val current = profiles.find { it.id == tokenStore.activeProfileId }
                    if (current == null) {
                        // Returning user: prefer their own ("self") profile
                        // over a family member's, so signing back in takes
                        // them straight to their own chat without re-asking
                        // for anything.
                        tokenStore.activeProfileId =
                            (profiles.find { it.relation == "self" } ?: profiles.first()).id
                    }
                    Routes.HOME
                }
            } catch (e: Exception) {
                // Expired/invalid token, or the profile list couldn't be
                // fetched -- fall back to the welcome screen rather than
                // crash.
                tokenStore.clear()
                Routes.WELCOME
            }
        }
        navController.navigateAndClear(destination)
        checked = true
    }

    if (!checked) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
    }
}
