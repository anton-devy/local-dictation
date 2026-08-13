## Purpose

The app exits cleanly and gracefully: resource warnings are eliminated, background threads are properly stopped, timers are cancelled, and OS resources are released before process termination. No leaked semaphores, no orphaned threads.

## Requirements

### Requirement: No resource_tracker warnings on quit
The system SHALL exit without emitting `multiprocessing.resource_tracker` warnings about leaked semaphores.

#### Scenario: App quits without resource warning
- **WHEN** the user quits the app via the menu's "Quit" button after running a transcription (which triggers tqdm initialization)
- **THEN** the process exits cleanly with no `resource_tracker: There appear to be 1 leaked semaphore objects to clean up at shutdown` warning printed to stderr

### Requirement: Background trigger thread is stopped on quit
The system SHALL cleanly stop the global-hotkey event-tap thread before exiting.

#### Scenario: Event tap thread stops gracefully
- **WHEN** the user quits the app while the global-hotkey trigger is active
- **THEN** the trigger thread receives a stop signal and terminates before the main process exits (verified via thread inspection or absence of hanging threads)

### Requirement: Idle-unload timer is cancelled on quit
The system SHALL cancel any pending idle-timeout timer before exiting.

#### Scenario: Idle timer cancelled during quit
- **WHEN** the user quits the app while an idle-unload timer is running (e.g., between a transcription and the idle timeout expiry)
- **THEN** the idle timer is cancelled and does not fire after quit is initiated

### Requirement: HUD auto-hide timer is cancelled on quit
The system SHALL cancel any pending HUD auto-hide timer if the HUD panel is active.

#### Scenario: HUD timer cancelled on quit
- **WHEN** the user quits the app while a HUD panel is visible with an active auto-hide timer
- **THEN** the auto-hide timer is cancelled before the HUD is destroyed

### Requirement: Transcription model is unloaded on quit
The system SHALL release the loaded Whisper model from memory as part of shutdown.

#### Scenario: Model unloaded on quit
- **WHEN** the user quits the app while a transcription model is loaded in memory
- **THEN** the model is unloaded (freed from RAM) before process exit

### Requirement: Quit menu item initiates shutdown sequence
The system SHALL respond to the "Quit" menu click by running the shutdown sequence (all of the above) before calling the Cocoa termination routine.

#### Scenario: Quit menu click triggers shutdown sequence
- **WHEN** the user clicks "Quit" in the menu bar
- **THEN** the app's shutdown sequence executes (stopping threads, cancelling timers, unloading model) before the process exits
