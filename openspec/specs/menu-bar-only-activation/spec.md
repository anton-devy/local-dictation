## Purpose

The app runs with macOS "accessory" activation policy, displaying only in the menu bar (top of screen) and never in the Dock (bottom of screen), following the standard UX pattern for background utility apps.

## Requirements

### Requirement: App does not appear in the Dock
The system SHALL run with macOS activation policy set to "accessory", preventing the app's icon from appearing in the Dock at any time during execution.

#### Scenario: App starts without Dock icon
- **WHEN** the app launches
- **THEN** the menu-bar icon appears and the app is fully functional, but no icon appears in the Dock

#### Scenario: App remains hidden from Dock across full session
- **WHEN** the app is running and the user performs various actions (trigger hotkey, transcribe, let idle, etc.)
- **THEN** the Dock remains free of the app's icon throughout the session

### Requirement: App is excluded from Cmd-Tab switcher
The system SHALL NOT appear in the Cmd-Tab application switcher, as expected behavior for accessory-policy apps.

#### Scenario: Cmd-Tab does not list the app
- **WHEN** the user presses Cmd-Tab to view and switch between open applications
- **THEN** local-dictation does not appear in the list (only user-facing apps do)

### Requirement: Menu-bar icon remains fully functional
The system SHALL maintain full menu-bar icon functionality, hotkey trigger, and all other features when running in accessory activation policy.

#### Scenario: Menu-bar operations work normally
- **WHEN** the app is running in accessory policy and the user clicks the menu-bar icon or uses the trigger hotkey
- **THEN** the menu opens, transcription works, and all callbacks fire as normal

### Requirement: Notifications and HUD remain visible
The system SHALL continue to display notifications and the HUD fallback panel regardless of activation policy.

#### Scenario: Notification appears with accessory policy
- **WHEN** a transcription completes and a notification is shown
- **THEN** the notification appears on screen, unaffected by the app's activation policy

#### Scenario: HUD appears when paste fails
- **WHEN** auto-paste fails or is skipped, triggering the fallback HUD display
- **THEN** the floating HUD panel appears near the cursor as normal
