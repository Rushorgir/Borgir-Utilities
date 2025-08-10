<!-- Banner -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:00ffcc,100:0066ff&height=250&section=header&text=🎙️%20Borgir%20Utilities&fontSize=60&fontColor=ffffff&animation=fadeIn&fontAlignY=38" alt="Borgir Utilities Banner"/>
</p>

<!-- Animated tagline -->
<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?size=24&duration=4000&color=00FFCC&center=true&vCenter=true&width=600&lines=Dynamic+Voice+Channel+Management;Powerful+Discord+Utility+Bot;Built+with+Python+%26+discord.py" alt="Typing Animation"/>
</p>

<!-- Badges -->
<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/discord.py-5865F2?style=for-the-badge&logo=discord&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/github/license/Rushorgir/Borgir-Utilities?style=for-the-badge&color=00ffcc"/>
</p>

---

## ✨ Features

- 🎧 **Dynamic Voice Channels**
  - Turn any VC into a **VC Hub** that spawns temporary sub-channels.
  - Auto-move users into new sub-VCs on join.
  - Auto-delete sub-VCs when empty.

- ⚙️ **Configurable Limits**
  - `user_limit`: Max users per sub-VC.
  - `channel_limit`: Max sub-VCs per hub.

- 💬 **Slash Commands**
  - `/add-vc-hub` — Make a channel a VC hub.
  - `/remove-vc-hub` — Remove a VC hub.
  - `/list-vc-hubs` — View all active hubs.
  - `/purge` — Bulk delete messages.
  - `/help` — View all commands.

- 🔐 **Permission Control**
  - Requires **Manage Channels**, **Manage Messages**, and **Move Members**.

- 💾 **Persistent Storage**
  - Stores settings in **SQLite**.
  - Data survives restarts.

---

## 🚀 Usage

1. **Add a VC Hub**  
   `/add-vc-hub channel:<hub> user_limit:<n> channel_limit:<n>`

2. **Join the Hub**  
   - Bot creates sub-VC & moves you in.

3. **Automatic Cleanup**  
   - Sub-VCs removed when empty.

4. **Manage**  
   - `/list-vc-hubs` — View hubs.  
   - `/purge count:<n>` — Clear messages.

---

<!-- Footer Animation -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0066ff,100:00ffcc&height=150&section=footer"/>
</p>
