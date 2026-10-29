# Removed packages

Removed from the rebuilt Android filesystem images. Original source files are preserved.

| Package | Reason |
| --- | --- |
| `android.autoinstalls.config.Lenovo.tablet` | OEM partner automatic-install recommendations |
| `com.android.providers.partnerbrowsercustomizations` | Partner browser customization |
| `com.android.providers.partnerbookmarks` | Partner bookmarks |
| `cn.wps.moffice_eng` | Bundled WPS Office |
| `ru.vk.store` | Bundled alternative app store |
| `com.google.android.play.games` | Optional Play Games preload |
| `com.google.android.apps.books` | Optional Play Books preload |
| `com.google.android.videos` | Optional Google TV preload (both copies) |
| `com.google.android.apps.youtube.kids` | Optional YouTube Kids preload |
| `com.google.android.apps.youtube.music` | Optional YouTube Music preload (both copies) |
| `com.google.android.apps.youtube.music.setupwizard` | YouTube Music setup promotion |
| `com.google.android.apps.tachyon` | Optional Google Meet preload |
| `com.google.android.apps.kids.home` | Optional Kids Space preload |
| `com.google.android.gms.supervision` | Optional Family Link preload |
| `com.google.android.projection.gearhead` | Android Auto not needed on travel tablet |
| `com.google.android.feedback` | Optional Google feedback app |
| `com.lmsa.app.lmsapad` | Software Fix tablet companion preload |
| `com.hf.app.wallpaper` | Bundled wallpaper content app |
| `com.zui.notes` | Optional OEM notes preload |
| `com.zui.weather` | Optional OEM weather preload |
| `com.lenovo.weathercenter` | OEM weather backend |
| `com.tblenovo.tabpushout` | OEM push-out promotional client |
| `com.google.android.apps.mediahome.launcher` | Optional Entertainment Space content feed |
| `com.tblenovo.lenovowhatsnew` | OEM promotional feature announcements |
| `com.motorola.demo` | Retail demonstration mode; normal launcher/setup broadcasts retained |
| `com.motorola.omadm.service` | Carrier OMA-DM provisioning client; companion VZW client also removed |
| `com.motorola.omadm.vzw` | Verizon OMA-DM provisioning companion |

Demo-state permission and broadcast references remain in the signed OEM launchers/setup app. Those manifests were not altered. OMA-DM runtime interactions and cross-model hardware compatibility have not been boot-tested.
