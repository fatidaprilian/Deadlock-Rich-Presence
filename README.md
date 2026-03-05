<div align="center">
  <img width="800" alt="Deadlock Dynamic Discord RPC Preview" src="https://github.com/user-attachments/assets/6d562252-a7e6-44ab-bfeb-8a753469b117" />

  # Deadlock Dynamic Discord RPC
  
  [![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence) ![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey?cacheSeconds=100000)
</div>

A heavily modified and enhanced Discord Rich Presence for Valve's [Deadlock](https://store.steampowered.com/app/1422450/Deadlock/). This Python application runs silently in your system tray, tracking your game state, heroes, and parties while fetching high-definition assets directly from the official Deadlock APIs.

**Major Credits:** This project is fundamentally built upon the original foundation created by [Jelloge](https://github.com/Jelloge/DeadlockRPC). A huge thank you to Jelloge for mapping out the initial log patterns and creating the Discord App ID!

---

## 🔥 Features & Upgrades
- **100% Dynamic Hero Data & Images:** Taps into `deadlock-api.com`! Hero names, flavor text, and HD **image assets** are pulled dynamically. No more waiting for developers to manually upload assets to the Discord Developer Portal for new heroes.
- **Dynamic Layout Swaps:** 
  - **In Lobby:** Clean Deadlock Logo with your selected Hero as the badge icon.
  - **In Match:** Explosive layout swap! Your presence background transforms into the HD full-sized Hero Portrait card showcasing who you're playing.
- **Silent Background Tracking:** Runs completely invisible in your System Tray without annoying CMD windows.
- **Unique Hideout Text:** Displays hero-specific flavor text (e.g., *"Mixing Drinks in the Hideout"* for Infernus).
- **IPC Pipe Fix:** Cycles through pipes `discord-ipc-0` to `-9` automatically to avoid conflicts with Spotify/Music presence plugins.

## ⚙️ Installation and Setup

1. Download **DeadlockRPC.exe** from the releases page.
2. ⚠️ **CRITICAL REQUIREMENT:** DeadlockRPC reads game logs. You **MUST** tell Deadlock to output these logs. 
   - Open Steam -> Go to Library.
   - Right-click **Deadlock** -> Choose **Properties**.
   - In the **General** tab, scroll down to **Launch Options**.
   - Type in `-condebug`.
3. Simply run `DeadlockRPC.exe`. It will quietly place an icon in your Windows System Tray (bottom right). Play Deadlock normally and look at your Discord!

<details>
<summary>Building from source</summary>

1. **Clone the repo**
2. **Install dependencies**: `pip install pypresence requests pystray Pillow`
3. **Configure** (optional): Edit `src/config.json` if needed.
4. **Build the exe**:
   ```bash
   pip install pyinstaller
   python build.py
   ```
   Output will be at `dist/DeadlockRPC.exe`.
</details>

## 🛠️ How It Works
The tracker monitors Deadlock's `console.log` file (enabled by the `-condebug` flag). It parses log events using regex patterns to detect game state changes seamlessly, without ever touching game memory. It is purely log-based and 100% VAC-safe.

*Got ideas or found bugs? Feel free to open an issue or contribute!*
