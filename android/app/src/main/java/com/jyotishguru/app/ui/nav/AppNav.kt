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
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.jyotishguru.app.data.ApiService
import com.jyotishguru.app.data.TokenStore
import com.jyotishguru.app.ui.home.HomeScreen
import com.jyotishguru.app.ui.kundli.KundliScreen
import com.jyotishguru.app.ui.login.ConsentScreen
import com.jyotishguru.app.ui.login.LoginScreen
import com.jyotishguru.app.ui.onboarding.OnboardingScreen

object Routes {
    const val SPLASH = "splash"
    const val LOGIN = "login"
    const val CONSENT = "consent"
    const val ONBOARDING = "onboarding"
    const val HOME = "home"
    const val KUNDLI = "kundli"
}

@Composable
fun AppNavHost(api: ApiService, tokenStore: TokenStore) {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = Routes.SPLASH) {
        composable(Routes.SPLASH) {
            SplashGate(api = api, tokenStore = tokenStore, navController = navController)
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
                onConsented = { navController.navigateAndClear(Routes.ONBOARDING) },
            )
        }
        composable(Routes.ONBOARDING) {
            OnboardingScreen(
                api = api,
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
                onAddProfile = { navController.navigate(Routes.ONBOARDING) },
                onViewKundli = { navController.navigate(Routes.KUNDLI) },
                onLoggedOut = { navController.navigateAndClear(Routes.LOGIN) },
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
            Routes.LOGIN
        } else {
            try {
                val profiles = api.listProfiles()
                if (profiles.isEmpty()) {
                    Routes.ONBOARDING
                } else {
                    if (tokenStore.activeProfileId == -1 ||
                        profiles.none { it.id == tokenStore.activeProfileId }
                    ) {
                        tokenStore.activeProfileId = profiles.first().id
                    }
                    Routes.HOME
                }
            } catch (e: Exception) {
                // Expired/invalid token, or the profile list couldn't be
                // fetched -- fall back to login rather than crash.
                tokenStore.clear()
                Routes.LOGIN
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
