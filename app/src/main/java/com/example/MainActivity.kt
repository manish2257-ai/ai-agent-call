package com.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import com.example.ui.screens.AuthScreen
import com.example.ui.screens.MainScreen
import com.example.ui.theme.MyApplicationTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MyApplicationTheme {
                var isAuthenticated by remember { mutableStateOf(true) }

                Surface(modifier = Modifier.fillMaxSize()) {
                    if (isAuthenticated) {
                        MainScreen(
                            onSignOut = { isAuthenticated = false }
                        )
                    } else {
                        AuthScreen(
                            onLoginSuccess = { isAuthenticated = true }
                        )
                    }
                }
            }
        }
    }
}
