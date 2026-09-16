package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.model.ContactCategory
import com.example.data.model.VipContact
import com.example.data.repository.CallAgentRepository
import com.example.ui.components.SectionHeader
import com.example.ui.theme.PrimaryCyan
import com.example.ui.theme.UrgencyHigh

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ContactsScreen(
    modifier: Modifier = Modifier
) {
    val contacts by CallAgentRepository.contacts.collectAsState()

    var showAddDialog by remember { mutableStateOf(false) }
    var name by remember { mutableStateOf("") }
    var phone by remember { mutableStateOf("") }
    var notes by remember { mutableStateOf("") }
    var selectedCat by remember { mutableStateOf(ContactCategory.CLIENT) }
    var alwaysAlert by remember { mutableStateOf(true) }
    var alwaysTransfer by remember { mutableStateOf(false) }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        contentPadding = PaddingValues(top = 12.dp, bottom = 36.dp)
    ) {
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                SectionHeader(
                    title = "VIP & Known Contacts",
                    subtitle = "Special priority handling and call routing"
                )
                FilledTonalButton(
                    onClick = { showAddDialog = true },
                    contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                ) {
                    Icon(Icons.Default.PersonAdd, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Add VIP", fontSize = 12.sp)
                }
            }
        }

        // Contact Cards
        items(contacts, key = { it.id }) { contact ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(14.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                border = CardDefaults.outlinedCardBorder()
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        modifier = Modifier.weight(1f)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(40.dp)
                                .clip(CircleShape)
                                .background(
                                    if (contact.isBlocked) Color.Gray.copy(alpha = 0.2f)
                                    else PrimaryCyan.copy(alpha = 0.15f)
                                ),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = if (contact.isBlocked) Icons.Default.Block else Icons.Default.Star,
                                contentDescription = null,
                                tint = if (contact.isBlocked) Color.Gray else PrimaryCyan,
                                modifier = Modifier.size(20.dp)
                            )
                        }

                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                Text(contact.name, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                                Surface(
                                    shape = RoundedCornerShape(4.dp),
                                    color = MaterialTheme.colorScheme.surfaceVariant
                                ) {
                                    Text(
                                        contact.category.label,
                                        fontSize = 10.sp,
                                        modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                                    )
                                }
                            }
                            Text(contact.phoneNumber, fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            if (contact.notes.isNotBlank()) {
                                Text(contact.notes, fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            }

                            // Tags
                            Row(
                                modifier = Modifier.padding(top = 6.dp),
                                horizontalArrangement = Arrangement.spacedBy(6.dp)
                            ) {
                                if (contact.alwaysAlert) {
                                    Surface(shape = RoundedCornerShape(4.dp), color = UrgencyHigh.copy(alpha = 0.15f)) {
                                        Text("Always Alert", fontSize = 10.sp, color = UrgencyHigh, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 5.dp, vertical = 2.dp))
                                    }
                                }
                                if (contact.alwaysTransfer) {
                                    Surface(shape = RoundedCornerShape(4.dp), color = PrimaryCyan.copy(alpha = 0.15f)) {
                                        Text("Direct Transfer", fontSize = 10.sp, color = PrimaryCyan, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 5.dp, vertical = 2.dp))
                                    }
                                }
                            }
                        }
                    }

                    IconButton(onClick = { CallAgentRepository.deleteContact(contact.id) }) {
                        Icon(Icons.Default.DeleteOutline, contentDescription = "Delete", tint = MaterialTheme.colorScheme.error)
                    }
                }
            }
        }
    }

    if (showAddDialog) {
        AlertDialog(
            onDismissRequest = { showAddDialog = false },
            title = { Text("Add VIP Contact") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    OutlinedTextField(
                        value = name,
                        onValueChange = { name = it },
                        label = { Text("Full Name") },
                        modifier = Modifier.fillMaxWidth()
                    )
                    OutlinedTextField(
                        value = phone,
                        onValueChange = { phone = it },
                        label = { Text("Phone Number (+E.164)") },
                        modifier = Modifier.fillMaxWidth()
                    )
                    OutlinedTextField(
                        value = notes,
                        onValueChange = { notes = it },
                        label = { Text("Notes (Company / Relation)") },
                        modifier = Modifier.fillMaxWidth()
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("Always Alert on Calls", fontSize = 12.sp)
                        Switch(checked = alwaysAlert, onCheckedChange = { alwaysAlert = it })
                    }

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("Direct Live Transfer", fontSize = 12.sp)
                        Switch(checked = alwaysTransfer, onCheckedChange = { alwaysTransfer = it })
                    }
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        if (name.isNotBlank() && phone.isNotBlank()) {
                            CallAgentRepository.addContact(
                                VipContact(
                                    id = "c_${System.currentTimeMillis() % 1000}",
                                    name = name,
                                    phoneNumber = phone,
                                    category = selectedCat,
                                    notes = notes,
                                    alwaysAlert = alwaysAlert,
                                    alwaysTransfer = alwaysTransfer
                                )
                            )
                            showAddDialog = false
                            name = ""
                            phone = ""
                            notes = ""
                        }
                    }
                ) {
                    Text("Save Contact")
                }
            },
            dismissButton = {
                TextButton(onClick = { showAddDialog = false }) { Text("Cancel") }
            }
        )
    }
}
